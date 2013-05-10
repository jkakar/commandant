# Commandant is a toolkit for building command-oriented tools.
# Copyright (C) 2009-2010 Jamshed Kakar.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""Unit tests for L{commandant.commands}."""

import os
import sys

from twisted.internet.defer import succeed
from twisted.trial.unittest import TestCase

from bzrlib.commands import Command

from testresources import ResourcedTestCase

from commandant.commands import ExecutableCommand, TwistedCommand
from commandant.testing.mocker import MockerResource
from commandant.testing.resources import (
    TemporaryDirectoryResource, CommandFactoryResource, FakeCommand,
    StdoutResource)


class CommandTest(ResourcedTestCase):
    """Tests for C{bzrlib.commands.Command} integration."""

    resources = [("factory", CommandFactoryResource()),
                 ("stdout", StdoutResource())]

    def tearDown(self):
        # Reset bzrlib command hooks.
        Command.hooks["list_commands"]._callbacks = []
        Command.hooks["list_commands"]._callback_names = {}
        Command.hooks["get_command"]._callbacks = []
        Command.hooks["get_command"]._callback_names = {}

        super(CommandTest, self).tearDown()

    def test_run_with_args_without_arguments(self):
        """
        The positional and keyword arguments passed to C{Command.run} are
        empty when no arguments are available.
        """
        self.factory.controller.install_bzrlib_hooks()
        command = self.factory.create_command("fake")
        command.run_argv_aliases([])
        self.assertEquals(sys.stdout.getvalue(), "((), {})")

    def test_run_with_args_with_arguments(self):
        """Arguments are mapped to the command being run."""

        class FakeArgumentCommand(FakeCommand):
            """A fake command taking command line arguments."""
            takes_args = ["test_arg0", "test_arg1"]

        self.factory.controller.install_bzrlib_hooks()
        command = self.factory.create_command("fake", FakeArgumentCommand)
        command.run_argv_aliases(["hello", "world"])
        self.assertEquals(
            sys.stdout.getvalue(),
            "((), {'test_arg0': 'hello', 'test_arg1': 'world'})")


class ExecutableCommandTest(ResourcedTestCase):
    """Tests for L{ExecutableCommand}."""

    resources = [("directory", TemporaryDirectoryResource()),
                 ("mocker", MockerResource()),
                 ("factory", CommandFactoryResource())]

    def test_run(self):
        """
        Running an executable command calls out to run the actual program.
        """
        path = os.path.join(self.directory.path, "executable")
        system_mock = self.mocker.replace("os.system")
        system_mock(path)
        self.mocker.replay()

        command = self.factory.create_command("test", ExecutableCommand)
        command.path = path
        command.run([])

    def test_run_with_arguments(self):
        """Arguments passed to the command are passed to the actual program."""
        path = os.path.join(self.directory.path, "executable")
        system_mock = self.mocker.replace("os.system")
        system_mock("%s --with-test-arg 1" % (path,))
        self.mocker.replay()

        command = self.factory.create_command("test", ExecutableCommand)
        command.path = path
        command.run_argv_aliases(["--with-test-arg", "1"])


class TwistedCommandTest(ResourcedTestCase, TestCase):

    resources = [("factory", CommandFactoryResource())]

    def test_get_reactor(self):
        """
        L{TwistedCommand.get_reactor} returns the Twisted reactor to use when
        running the command.  It can be overridden to install and run a
        non-standard reactor.
        """
        from twisted.internet import reactor

        class FakeCommand(TwistedCommand):

            def run(self):
                return succeed(True)

        command = self.factory.create_twisted_command("test", FakeCommand)
        self.assertIdentical(reactor, command.get_reactor())

    def test_run_argv_aliases_returns_value(self):
        """
        The return value of the command is passed back to Bazaar, after
        C{run_argv_aliases} has run.  Because of the mocking place, the exact
        value is return in tests, but in practice the real value will be
        returned back to Bazaar.
        """

        class FakeCommand(TwistedCommand):

            def run(self):
                return succeed(True)

        command = self.factory.create_twisted_command("test", FakeCommand)

        def check(result):
            self.assertTrue(result)

        deferred = command.run_argv_aliases([])
        deferred.addCallback(check)
        return deferred

    def test_run_with_arguments(self):
        """
        The same conventions for defining arguments and options works with
        L{TwistedCommand}s.
        """

        class FakeCommand(TwistedCommand):

            takes_args = ["argument"]

            def run(self, argument):
                return succeed(argument)

        command = self.factory.create_twisted_command("test", FakeCommand)

        def check(result):
            self.assertEqual("test-value", result)

        deferred = command.run_argv_aliases(["test-value"])
        deferred.addCallback(check)
        return deferred

    def test_run_with_non_deferred_return_value(self):
        """A L{TwistedCommand} is not required to return a C{Deferred}."""

        class FakeCommand(TwistedCommand):

            def run(self):
                return "test-value"

        command = self.factory.create_twisted_command("test", FakeCommand)

        def check(result):
            self.assertEqual("test-value", result)

        result = command.run_argv_aliases([])
        self.assertEqual("test-value", result)

    def test_run_with_exception(self):
        """
        If an exception is raised by the command, it will be rethrown after
        the reactor stops.
        """

        class FakeCommand(TwistedCommand):

            def run(self):
                raise RuntimeError("KABOOM!")

        command = self.factory.create_twisted_command("test", FakeCommand)
        self.assertRaises(RuntimeError, command.run_argv_aliases, [])
