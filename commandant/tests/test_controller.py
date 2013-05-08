# Commandant is a framework for building command-oriented tools.
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

"""Unit tests for L{commandant.controller}."""

import os
import stat
import sys

import bzrlib.ui
from bzrlib.errors import BzrCommandError
from bzrlib.commands import all_command_names, Command

from testresources import ResourcedTestCase

from commandant import __version__
from commandant.controller import CommandController
from commandant.testing.mocker import MockerResource
from commandant.testing.resources import (
    TemporaryDirectoryResource, FakeCommand, FakeHelpTopic, StdoutResource,
    BzrlibHooksResource, CommandModulesResource)


class CommandControllerTest(ResourcedTestCase):
    """Tests for L{CommandController}."""

    resources = [("mocker", MockerResource()),
                 ("directory", TemporaryDirectoryResource()),
                 ("bzrlib_hooks", BzrlibHooksResource()),
                 ("modules", CommandModulesResource()),
                 ("stdout", StdoutResource())]

    def setUp(self):
        super(CommandControllerTest, self).setUp()
        self.controller = CommandController()

    def test_instantiate(self):
        """
        A L{CommandController} has no C{bzrlib.commands.Command}s, by default.
        It's program name and version are those of Commandant by default, too.
        """
        self.assertEquals(self.controller.get_command_names(), set())
        self.assertEquals(self.controller.program_name, "commandant")
        self.assertEquals(self.controller.program_version, __version__)
        self.assertEquals(self.controller.program_summary,
                          "A framework for building command-oriented tools.")
        self.assertEquals(self.controller.program_url,
                          "http://launchpad.net/commandant")

    def test_instantiate_with_custom_program_details(self):
        """
        A L{CommandController} can be instantiated with a custom program name,
        version, summary and URL.
        """
        controller = CommandController("test-program", "42.3.17",
                                       "A test program.", "http://example.com")
        self.assertEquals(controller.program_name, "test-program")
        self.assertEquals(controller.program_version, "42.3.17")
        self.assertEquals(controller.program_summary, "A test program.")
        self.assertEquals(controller.program_url, "http://example.com")

    def test_install_bzrlib_hooks(self):
        """
        The L{CommandController.install_bzrlib_hooks} method registers the
        controller with C{bzrlib.Command.hooks} to make use of Bazaar's
        command infrastructure.  It also sets up C{bzrlib.ui}.
        """
        original_ui_factory = bzrlib.ui.ui_factory
        self.assertEquals(len(Command.hooks["list_commands"]), 0)
        self.assertEquals(len(Command.hooks["get_command"]), 0)
        self.controller.install_bzrlib_hooks()
        self.assertNotEquals(original_ui_factory, bzrlib.ui.ui_factory)
        self.assertEquals(len(Command.hooks["list_commands"]), 1)
        self.assertEquals(len(Command.hooks["get_command"]), 1)

    def test_register_command(self):
        """
        The L{CommandController.register_command} method adds a named
        C{bzrlib.commands.Command} to the controller.
        """
        self.controller.install_bzrlib_hooks()
        self.assertEquals(all_command_names(), set())
        self.controller.register_command("fake-command", FakeCommand)
        self.assertEquals(all_command_names(), set(["fake-command"]))

    def test_get_command(self):
        """
        The L{CommandController.get_command} method returns a
        C{bzrlib.commands.Command} instances matching a specified name.
        """
        self.assertEquals(self.controller.get_command("fake-command"), None)
        self.controller.register_command("fake-command", FakeCommand)
        command = self.controller.get_command("fake-command")
        self.assertTrue(isinstance(command, FakeCommand))
        self.assertEquals(command.controller, self.controller)

    def test_run_unknown_command(self):
        """
        C{bzrlib.error.BzrCommandError} is raised if an unknown
        C{bzrlib.commands.Command} name is used.
        """
        self.assertRaises(BzrCommandError, self.controller.run, ["unknown"])

    def test_run_command_without_arguments(self):
        """
        L{CommandController.run} runs the C{bzrlib.commands.Command} with the
        name that matches the first command-line argument.
        """
        self.controller.install_bzrlib_hooks()
        self.controller.register_command("fake-command", FakeCommand)
        self.controller.run(["fake-command"])
        self.assertEquals(sys.stdout.getvalue(), "((), {})")

    def test_run_command_with_arguments(self):
        """
        Arguments passed to L{CommandController.run} are mapped to the
        command's C{run} method.
        """

        class FakeArgumentCommand(FakeCommand):
            """A fake command taking command line arguments."""
            takes_args = ["test_arg"]

        self.controller.install_bzrlib_hooks()
        self.controller.register_command("fake-command", FakeArgumentCommand)
        self.controller.run(["fake-command", "test-arg"])
        # The argument value is sometimes be coerced into a unicode
        # string. Could this be a change in bzrlib?
        self.assertIn(
            sys.stdout.getvalue(), (
                "((), {'test_arg': 'test-arg'})",
                "((), {'test_arg': u'test-arg'})",
                ))

    def test_register_help_topic(self):
        """
        L{CommandController.register_help_topic} adds a L{HelpTopic} to the
        controller.
        """
        self.assertEquals(self.controller.get_help_topic_names(), set())
        self.controller.register_help_topic("test-topic", FakeHelpTopic)
        self.assertEquals(self.controller.get_help_topic_names(),
                          set(["test-topic"]))

    def test_get_help_topic(self):
        """
        L{CommandController.get_help_topic} returns a L{HelpTopic} instances
        matching the specified name, or C{None} if a match can't be found.
        """
        self.assertEquals(self.controller.get_help_topic("test-topic"), None)
        self.controller.register_help_topic("test-topic", FakeHelpTopic)
        help_topic = self.controller.get_help_topic("test-topic")
        self.assertTrue(isinstance(help_topic, FakeHelpTopic), help_topic)
        self.assertEquals(help_topic.controller, self.controller)
        self.assertEquals(help_topic.get_summary(), "A fake summary!")
        self.assertEquals(help_topic.get_text(), "Fake descriptive help text.")

    def test_load_path_with_empty_directory(self):
        """
        Loading an empty directory doesn't make any changes to the controller.
        """
        self.controller.load_path(self.directory.path)
        self.assertEquals(self.controller.get_command_names(), set())

    def test_load_path_with_mixed_executables_and_normal_files(self):
        """
        The controller ignores non-executable files that aren't C{.txt} or
        C{.py} files.
        """
        path = os.path.join(self.directory.path, "non-executable")
        self.directory.make_path(content="non-executable file", path=path)
        path = os.path.join(self.directory.path, "executable")
        self.directory.make_path(content="executable file", path=path)
        os.chmod(path, stat.S_IEXEC)
        self.controller.load_path(self.directory.path)
        self.assertEquals(sorted(os.listdir(self.directory.path)),
                          ["executable", "non-executable"])
        self.assertEquals(self.controller.get_command_names(),
                          set(["executable"]))

    def test_load_path_with_help_topic(self):
        """
        A C{.txt} file in the command directory is treated as a L{HelpTopic}.
        """
        content = """\
This line contains a short summary for the help topic.

All remaining content makes up the long descriptive text for the help topic.
"""
        path = os.path.join(self.directory.path, "test-topic.txt")
        self.directory.make_path(content=content, path=path)
        self.controller.load_path(self.directory.path)
        self.assertEquals(os.listdir(self.directory.path), ["test-topic.txt"])
        self.assertEquals(self.controller.get_help_topic_names(),
                          set(["test-topic"]))

    def test_load_path_replaces_underscores_with_dashes(self):
        """
        Command names for executables are generated from their filenames.
        Underscores in filenames are converted to dashes for the command name.
        """
        path = os.path.join(self.directory.path, "executable_command")
        self.directory.make_path(content="executable file", path=path)
        os.chmod(path, stat.S_IEXEC)
        self.controller.load_path(self.directory.path)
        self.assertEquals(sorted(os.listdir(self.directory.path)),
                          ["executable_command"])
        self.assertEquals(self.controller.get_command_names(),
                          set(["executable-command"]))

    def test_load_path_ignores_executables_that_are_backup_copies(self):
        """Backup files are ignored by the controller."""
        path = os.path.join(self.directory.path, "executable~")
        self.directory.make_path(content="executable file", path=path)
        os.chmod(path, stat.S_IEXEC)
        self.controller.load_path(self.directory.path)
        self.assertEquals(sorted(os.listdir(self.directory.path)),
                          ["executable~"])
        self.assertEquals(self.controller.get_command_names(), set())

    def test_load_path_ignores_missing_temporary_files(self):
        """
        If a file is opened in emacs, but unsaved, it creates a symlink that
        points to a missing file.  A failure is caused when C{os.stat} is used
        with these files.
        """
        os.symlink(os.path.join(self.directory.path, "missing-file"),
                   os.path.join(self.directory.path, "#.symlink"))
        self.controller.load_path(self.directory.path)
        self.assertEquals(sorted(os.listdir(self.directory.path)),
                          ["#.symlink"])
        self.assertEquals(self.controller.get_command_names(), set())

    def test_load_path_ignores_directories(self):
        """Directories are ignored by the controller."""
        self.directory.make_dir()
        self.controller.load_path(self.directory.path)
        self.assertEquals(self.controller.get_command_names(), set())

    def test_load_path_with_commandless_python_module(self):
        """
        Loading a Python module that has no commands or help topics has no
        effect on the controller.
        """
        path = os.path.join(self.directory.path, "test_no_command.py")
        self.directory.make_path(content="a = 1", path=path)
        self.controller.load_path(self.directory.path)
        self.assertEquals(self.controller.get_command_names(), set())

    def test_load_path_with_exploding_python_module(self):
        """
        Exceptions raised while a Python module containing commands and help
        topics is being imported are not suppressed.
        """
        path = os.path.join(self.directory.path, "test_explode.py")
        self.directory.make_path(content="{", path=path)
        self.assertRaises(SyntaxError, self.controller.load_path,
                          self.directory.path)

    def test_load_path_with_python_command(self):
        """
        Objects in Python modules with names that start with C{cmd_} are
        loaded as commands.
        """
        content = """\
from bzrlib.commands import Command

class cmd_test_command(Command):
    def run(self):
        pass
"""
        path = os.path.join(self.directory.path, "test_command.py")
        self.directory.make_path(content=content, path=path)
        self.controller.load_path(self.directory.path)
        self.assertEquals(self.controller.get_command_names(),
                          set(["test-command"]))

    def test_load_path_uses_name_from_command_class(self):
        """
        The command name is derived from the class name and has nothing to do
        with the module name.
        """
        content = """\
from bzrlib.commands import Command

class cmd_test_class_name(Command):
    def run(self):
        pass
"""
        path = os.path.join(self.directory.path, "test_module.py")
        self.directory.make_path(content=content, path=path)
        self.controller.load_path(self.directory.path)
        self.assertEquals(self.controller.get_command_names(),
                          set(["test-class-name"]))

    def test_load_path_with_python_command_with_dash_in_filename(self):
        """
        Command names for Python commands are generated from their class
        names.  Underscores in class names are converted to dashes for the
        command name.
        """
        content = """\
from bzrlib.commands import Command

class cmd_test_dash_command(Command):
    def run(self):
        pass
"""
        path = os.path.join(self.directory.path, "test-dash-command.py")
        self.directory.make_path(content=content, path=path)
        self.controller.load_path(self.directory.path)
        self.assertEquals(self.controller.get_command_names(),
                          set(["test-dash-command"]))

    def test_load_path_with_python_commands_in_multiple_files(self):
        """The controller will load Python commands from all C{.py} files."""
        content = """\
from bzrlib.commands import Command

class cmd_%s(Command):
    def run(self):
        pass
"""
        for name in ("test_command", "test-dash-command"):
            path = os.path.join(self.directory.path, "%s.py" % (name,))
            name = name.replace("-", "_")
            self.directory.make_path(content=content % (name,), path=path)
        self.controller.load_path(self.directory.path)
        self.assertEquals(self.controller.get_command_names(),
                          set(["test-command", "test-dash-command"]))

    def test_load_module_with_command(self):
        """
        L{CommandController.load_module} ignores objects that don't start with
        C{cmd_}.
        """

        class FakeModule(object):
            __dict__ = {"cmd_test": Command, "ignored": int}

        self.controller.load_module(FakeModule())
        self.assertEquals(self.controller.get_command_names(), set(["test"]))

    def test_load_module_with_help_topic(self):
        """
        L{CommandController.load_module} ignores objects that don't start with
        C{topic_}.
        """

        class FakeModule(object):
            __dict__ = {"topic_test": Command, "ignored": int}

        self.controller.load_module(FakeModule())
        self.assertEquals(self.controller.get_help_topic_names(),
                          set(["test"]))

    def test_load_module_multiple_commands(self):
        """Multiple commands can be loaded from a single module."""

        class FakeModule(object):
            __dict__ = {"cmd_test1": Command, "cmd_test2": Command}

        self.controller.load_module(FakeModule())
        self.assertEquals(self.controller.get_command_names(),
                          set(["test1", "test2"]))

    def test_load_module_with_command_replaces_underscores_with_dashes(self):
        """
        Command names for Python commands are generated from their class
        names.  Underscores in class names are converted to dashes for the
        command name.
        """

        class FakeModule(object):
            __dict__ = {"cmd_test_command": Command, "ignored": int}

        self.controller.load_module(FakeModule())
        self.assertEquals(self.controller.get_command_names(),
                          set(["test-command"]))

    def test_load_module_with_help_topic_replaces_underscore_with_dash(self):
        """
        Help topic names for Python help topics are generated from their class
        names.  Underscores in class names are converted to dashes for the
        help topic name.
        """

        class FakeModule(object):
            __dict__ = {"topic_test_topic": Command, "ignored": int}

        self.controller.load_module(FakeModule())
        self.assertEquals(self.controller.get_help_topic_names(),
                          set(["test-topic"]))
