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

"""Unit tests for L{commandant.entry_point}."""

import os
import sys

from bzrlib.errors import BzrCommandError
from bzrlib.commands import all_command_names

from testresources import ResourcedTestCase

from commandant.errors import UsageError
from commandant.entry_point import main
from commandant.testing.resources import (
    TemporaryDirectoryResource, BzrlibHooksResource, StdoutResource)


class MainTest(ResourcedTestCase):
    """Tests for L{main}."""

    resources = [("directory", TemporaryDirectoryResource()),
                 ("bzrlib_hooks", BzrlibHooksResource()),
                 ("stdout", StdoutResource())]

    def test_incorrect_number_of_arguments(self):
        """
        L{main} requires a minimum of 2 arguments, the name of the program,
        typically C{commandant}, and the path to locate commands.  A
        L{UsageError} is raised if a sufficient number of arguments aren't
        provided.
        """
        self.assertRaises(UsageError, main, [])
        self.assertRaises(UsageError, main, ["commandant"])

    def test_invalid_path_argument(self):
        """
        If the path argument starts with C{-} the user likely typed in
        C{--help} or something similar.  In this case a L{UsageError} is
        raised.
        """
        self.assertRaises(UsageError, main, ["commandant", "--help"])

    def test_default_to_help(self):
        """
        If no command name is provided the C{help} command is used as a
        default.
        """
        self.directory.make_path()
        main(["commandant", self.directory.path])
        self.assertEquals(sys.stdout.getvalue(), """\
commandant -- A framework for building command-oriented tools.
http://launchpad.net/commandant

Basic commands:
  commandant help commands  List all commands
  commandant help topics    List all help topics
""")

    def test_unknown_command(self):
        """
        C{bzrlib.error.BzrCommandError} is raised if an unknown command is
        run.
        """
        self.assertRaises(BzrCommandError, main,
                          ["commandant", self.directory.path, "unknown"])

    def test_controller_path(self):
        """
        C{CommandController.path} is set to the path specified as the first
        argument, in the entry point logic.  In the future this should be
        removed, and commands should not rely on it.
        """
        hello_path = os.path.join(self.directory.path, "hello")
        content = """\
from bzrlib.commands import Command

class cmd_test_command(Command):
    def run(self):
        file = open('%s', 'w')
        file.write('Hello, world!')
        file.close()
""" % (hello_path,)
        path = os.path.join(self.directory.path, "test_command.py")
        self.directory.make_path(content=content, path=path)
        main(["commandant", self.directory.path, "test-command"])
        self.assertEquals(open(hello_path).read(), "Hello, world!")

    def test_install_bzr_hooks(self):
        """
        L{CommandController.install_bzrlib_hooks} is called to hook the
        controller into C{bzrlib}.
        """
        main(["commandant", self.directory.path, "version"])
        self.assertEquals(all_command_names(), set(["help", "version"]))
