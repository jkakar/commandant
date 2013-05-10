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

"""Test resources."""

from cStringIO import StringIO
import os
import shutil
import sys
import tempfile

import bzrlib.ui
from bzrlib.commands import Command

from testresources import TestResource

from commandant.controller import CommandController


class TemporaryDirectory(object):
    """A temporary directory resource/"""

    def setUp(self):
        self._counter = 1
        self.path = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.path)

    def make_dir(self):
        """Make a temporary directory.

        @return: The path to the new directory.
        """
        path = self.make_path()
        os.mkdir(path)
        return path

    def make_path(self, content=None, path=None):
        """Create a new C{path} name, optionally writing C{content} to it.

        @return: The C{path} provided or a new one if it was C{None}.
        """
        if path is None:
            self._counter += 1
            path = "%s/%03d" % (self.path, self._counter)
        if content is not None:
            file = open(path, "w")
            try:
                file.write(content)
            finally:
                file.close()
        return path


class TemporaryDirectoryResource(TestResource):
    """Resource provides and destroys temporary directories."""

    def make(self, dependency_resources):
        """Create a temporary directory."""
        directory = TemporaryDirectory()
        directory.setUp()
        return directory

    def clean(self, directory):
        """Destroy a temporary directory."""
        directory.tearDown()


class FakeCommand(Command):
    """Summary text.

    Long descriptive text that
    spans multiples lines.
    """

    def run(self, *args, **kwargs):
        self.outf.write(repr((args, kwargs)))


class FakeHelpTopic(Command):
    # This class intentionally doesn't have a docstring.

    name = "fake-help-topic"

    def get_summary(self):
        """Get a short topic summary for use in a topic listing."""
        return "A fake summary!"

    def get_text(self):
        """Get topic content."""
        return "Fake descriptive help text."


class CommandFactory(object):
    """Factory creates C{bzrlib.commands.Command} and L{HelpTopic} objects."""

    def __init__(self, program_name, program_version, program_summary,
                 program_url):
        super(CommandFactory, self).__init__()
        self.controller = CommandController(program_name, program_version,
                                            program_summary, program_url)

    def create_command(self, name, command_class=FakeCommand):
        """Register a C{command_class} using C{name}.

        @return: A C{command_class} instance.
        """
        self.controller.register_command(name, command_class)
        command = self.controller.get_command(name)
        command.controller = self.controller
        command.outf = StringIO()
        return command

    def create_twisted_command(self, name, command_class):
        """Register C{command_class} using C{name}.

        The logic that starts and stops the reactor is replaced with fake
        versions, so that the command can be tested without breaking the test
        suite.

        @param name: The name of the command.
        @param command_class: A subclass of L{TwistedCommand}.
        @return: A C{command_class} instance.
        """
        command = self.create_command(name, command_class)

        def fake_start_reactor(argv, alias_argv=None):
            return command._run_command(argv, alias_argv)

        def fake_stop_reactor(result):
            command._capture_return_value(result)
            return result

        command._start_reactor = fake_start_reactor
        command._stop_reactor = fake_stop_reactor
        return command

    def create_help_topic(self, name, help_topic_class=FakeHelpTopic):
        """Register a C{help_topic_class} using C{name}.

        @return: A C{help_topic_class} instance.
        """
        self.controller.register_help_topic(name, help_topic_class)
        help_topic = self.controller.get_help_topic(name)
        help_topic.controller = self.controller
        help_topic.outf = StringIO()
        return help_topic


class CommandFactoryResource(TestResource):
    """Resource creates L{CommandFactory}s."""

    resources = [("directory", TemporaryDirectoryResource())]

    def __init__(self, program_name=None, program_version=None,
                 program_summary=None, program_url=None):
        super(CommandFactoryResource, self).__init__()
        self.program_name = program_name
        self.program_version = program_version
        self.program_summary = program_summary
        self.program_url = program_url

    def make(self, dependency_resources):
        """Create a L{CommandFactory}."""
        return CommandFactory(self.program_name, self.program_version,
                              self.program_summary, self.program_url)


class BzrlibHooks(object):
    """Resource resets C{bzrlib.commands.Command.hooks} internals."""

    def reset(self):
        Command.hooks["list_commands"]._callbacks = []
        Command.hooks["list_commands"]._callback_names = {}
        Command.hooks["get_command"]._callbacks = []
        Command.hooks["get_command"]._callback_names = {}


class BzrlibHooksResource(TestResource):
    """
    Resource creates a L{BzrlibHooks} instance to manage C{bzrlib.commands}
    internals.
    """

    def make(self, dependency_resources):
        """Create a L{BzrlibHooks} manager."""
        bzrlib_hooks = BzrlibHooks()
        bzrlib_hooks.reset()
        self._original_ui_factory = bzrlib.ui.ui_factory
        return bzrlib_hooks

    def clean(self, bzrlib_hooks):
        """Reset C{bzrlib.commands} hooks."""
        bzrlib_hooks.reset()
        bzrlib.ui.ui_factory = self._original_ui_factory


class CommandModules(object):
    """Resource cleans up dynamically loaded Commandant command modules."""

    def reset(self):
        commandant_commands = []
        for name in sys.modules.iterkeys():
            if name.startswith("commandant_command"):
                commandant_commands.append(name)
        for name in commandant_commands:
            del sys.modules[name]


class CommandModulesResource(TestResource):
    """
    Resource creates a L{CommandModules} instance to clean up dynamically
    loaded Commandant command modules.
    """

    def make(self, dependency_resources):
        """Create a L{CommandModules} manager."""
        modules = CommandModules()
        modules.reset()
        return modules

    def clean(self, modules):
        """Reset dynamically created Commandant command modules."""
        modules.reset()


class Stdout(object):
    """Resource mocks C{sys.stdout}."""

    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = StringIO()

    def tearDown(self):
        sys.stdout = self.stdout


class StdoutResource(TestResource):
    """
    Resource creates a L{Stdout} resource that replaces C{sys.stdout} with a
    C{StringIO} instance while a test is running and resets it after the test
    is over.
    """

    def make(self, dependency_resources):
        """Create a L{Stdout} manager."""
        stdout = Stdout()
        stdout.setUp()
        return stdout

    def clean(self, stdout):
        """Reset dynamically created Commandant command modules."""
        stdout.tearDown()
