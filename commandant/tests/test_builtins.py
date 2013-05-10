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

"""Unit tests for L{commandant.builtins}."""

import doctest
import os
from textwrap import dedent

from bzrlib.commands import Command

from testresources import ResourcedTestCase
from testtools.matchers import DocTestMatches

from commandant import __version__
from commandant.builtins import (
    cmd_version, cmd_help,
    topic_basic, topic_commands, topic_hidden_commands, topic_topics)
from commandant.testing.basic import CommandantTestCase
from commandant.testing.resources import CommandFactoryResource


class VersionCommandTest(ResourcedTestCase):
    """Tests for L{cmd_version}."""

    resources = [("factory", CommandFactoryResource())]

    def setUp(self):
        super(VersionCommandTest, self).setUp()
        self.command = self.factory.create_command("version", cmd_version)

    def test_run(self):
        """The version command prints out the program name and version."""
        self.command.run()
        output = self.command.outf.getvalue()
        self.assertTrue(output.startswith("commandant %s\n" % (__version__,)))

    def test_run_with_short_option(self):
        """
        The version command only prints the version if the C{--short} option
        is proved.
        """
        self.command.run(short=True)
        self.assertEquals(self.command.outf.getvalue(),
                          "%s\n" % (__version__,))


class CustomVersionCommandTest(ResourcedTestCase):
    """Tests for L{cmd_version} with custom program details."""

    resources = [("factory", CommandFactoryResource("test", "42.3.17"))]

    def setUp(self):
        super(CustomVersionCommandTest, self).setUp()
        self.command = self.factory.create_command("version", cmd_version)

    def test_run(self):
        """Custom program details are used if available."""
        self.command.run()
        self.assertTrue(
            self.command.outf.getvalue().startswith("test 42.3.17\n"))


class HelpCommandTest(CommandantTestCase):
    """Tests for L{cmd_help}."""

    resources = [("factory", CommandFactoryResource())]

    def setUp(self):
        super(HelpCommandTest, self).setUp()
        self.command = self.factory.create_command("help", cmd_help)
        self.basic_help_topic = (
            self.factory.create_help_topic("basic", topic_basic))
        self.commands_help_topic = (
            self.factory.create_help_topic("commands", topic_commands))
        self.commands_help_topic = (
            self.factory.create_help_topic("hidden-commands",
                                           topic_hidden_commands))
        self.topics_help_topic = (
            self.factory.create_help_topic("topics", topic_topics))

    def test_run_with_stock_help_text(self):
        """The help command displays the stock help text."""
        self.command.run()
        self.assertEquals(self.command.outf.getvalue(), """\
commandant -- A toolkit for building command-oriented tools.
https://github.com/jkakar/commandant

Basic commands:
  commandant help commands  List all commands
  commandant help topics    List all help topics
""")

    def test_run_with_custom_help_text(self):
        """
        If a file called C{basic.txt} is present, its contents are shown
        instead of the stock help text.
        """
        content = """\
Basic commands.

custom -- help for commandant tool

Custom help text!
"""
        path = os.path.join(self.factory.directory.path, "basic.txt")
        self.factory.directory.make_path(content, path)
        self.factory.controller.load_path(self.factory.directory.path)
        self.command.run()
        self.assertEquals(self.command.outf.getvalue(), """\
custom -- help for commandant tool

Custom help text!
""")

    def test_run_with_custom_help_text_trims_trailing_whitespace(self):
        """Trailing whitespace in custom help text is trimmed."""
        content = """\
Basic commands.

custom -- help for commandant tool

Custom help text!


"""
        path = os.path.join(self.factory.directory.path, "basic.txt")
        self.factory.directory.make_path(content, path)
        self.factory.controller.load_path(self.factory.directory.path)
        self.command.run()
        self.assertEquals(self.command.outf.getvalue(), """\
custom -- help for commandant tool

Custom help text!
""")

    def test_run_commands(self):
        """
        The C{commands} topic displays a list of available command names and
        summaries.
        """
        self.command.run(topic="commands")
        self.assertEquals(self.command.outf.getvalue(), """\
help  Show help about a command or topic.
""")

    def test_run_many_commands(self):
        """
        The C{commands} topic displays a list of available command names and
        summaries.  The summaries are aligned in a column.
        """
        self.factory.create_command("version", cmd_version)
        self.command.run(topic="commands")
        self.assertEquals(self.command.outf.getvalue(), """\
help     Show help about a command or topic.
version  Show version of commandant.
""")

    def test_run_commands_without_docstring(self):
        """
        A summary is not output for Python commands that don't have a
        docstring.
        """

        class cmd_fake_command(Command):
            name = "fake-command"

        self.factory.create_command("fake-command", cmd_fake_command)
        self.command.run(topic="commands")
        expected = dedent("""\
            fake-command
            help          Show help about a command or topic.
            """)
        self.assertThat(
            self.command.outf.getvalue(),
            DocTestMatches(expected, doctest.NORMALIZE_WHITESPACE))

    def test_run_commands_with_custom_help_topic(self):
        """
        If a custom topic is provided for a Python command the summary from
        the custom topic used when the C{command} topic is run.
        """

        class cmd_fake_command(Command):
            name = "fake-command"

        content = """\
A fake command.

This fake command implementation is runnable, but does nothing when run.
"""
        path = os.path.join(self.factory.directory.path, "fake-command.txt")
        self.factory.directory.make_path(content, path)
        self.factory.create_command("fake-command", cmd_fake_command)
        self.factory.controller.load_path(self.factory.directory.path)
        self.command.run(topic="commands")
        self.assertEquals(self.command.outf.getvalue(), """\
fake-command  A fake command.
help          Show help about a command or topic.
""")

    def test_run_commands_with_custom_help_help_topic(self):
        """
        The summary shown when a custom help topic is available for the
        C{help} command is not altered.
        """
        content = """\
A fake help command.

The fake summary above won't be used, as a special case, since the entire
contents of help.txt is used as the basic output for 'commandant help';
therefore, it isn't expected to have a single-line summary, like other help
topics.
"""
        path = os.path.join(self.factory.directory.path, "help.txt")
        self.factory.directory.make_path(content, path)
        self.command.run(topic="commands")
        self.assertEquals(self.command.outf.getvalue(), """\
help  Show help about a command or topic.
""")

    def test_run_with_hidden_commands(self):
        """
        The C{commands} topic shouldn't show hidden
        C{bzrlib.commands.Command}s.
        """

        class cmd_fake_command(Command):
            """A fake hidden command."""
            hidden = True

        self.factory.create_command("fake-command", cmd_fake_command)
        self.command.run(topic="commands")
        self.assertEquals(self.command.outf.getvalue(), """\
help  Show help about a command or topic.
""")

    def test_run_hidden_commands(self):
        """
        The C{commands} topic should only show hidden
        C{bzrlib.commands.Command}s.
        """

        class cmd_fake_command(Command):
            """A fake hidden command."""
            hidden = True

        self.factory.create_command("fake-command", cmd_fake_command)
        self.command.run(topic="hidden-commands")
        self.assertEquals(self.command.outf.getvalue(), """\
fake-command  A fake hidden command.
""")

    def test_run_hidden_commands_without_hidden_commands(self):
        """
        The C{commands} topic shouldn't show anything if there are no hidden
        C{bzrlib.commands.Command}s.
        """
        self.command.run(topic="hidden-commands")
        self.assertEquals(self.command.outf.getvalue(), "")

    def test_run_topics(self):
        """The C{topics} topic lists help topics."""
        self.command.run(topic="topics")
        self.assertEquals(self.command.outf.getvalue(), """\
basic            Basic commands.
commands         Basic help for all commands.
hidden-commands  Basic help for hidden commands.
topics           Topics list.
""")

    def test_run_topics_with_custom_help_topic(self):
        """The C{topics} topic lists help topics, including custom topics."""
        path = os.path.join(self.factory.directory.path, "custom-topic.txt")
        self.factory.directory.make_path("A custom topic.", path)
        self.factory.controller.load_path(self.factory.directory.path)
        self.command.run(topic="topics")
        self.assertEquals(self.command.outf.getvalue(), """\
basic            Basic commands.
commands         Basic help for all commands.
custom-topic     A custom topic.
hidden-commands  Basic help for hidden commands.
topics           Topics list.
""")

    def test_run_topics_ignores_custom_command_help(self):
        """The C{topics} command doesn't display topics for commands."""

        class cmd_fake_command(Command):
            pass

        path = os.path.join(self.factory.directory.path, "fake_command.txt")
        self.factory.directory.make_path("A custom topic.", path)
        self.factory.controller.load_path(self.factory.directory.path)
        self.factory.create_command("fake-command", cmd_fake_command)
        self.command.run(topic="topics")
        self.assertEquals(self.command.outf.getvalue(), """\
basic            Basic commands.
commands         Basic help for all commands.
hidden-commands  Basic help for hidden commands.
topics           Topics list.
""")

    def test_run_topics_with_custom_underscore_help_topic(self):
        """Underscores in topic names are automatically converted to dashes."""
        path = os.path.join(self.factory.directory.path, "custom_topic.txt")
        self.factory.directory.make_path("A custom topic.", path)
        self.factory.controller.load_path(self.factory.directory.path)
        self.command.run(topic="topics")
        self.assertEquals(self.command.outf.getvalue(), """\
basic            Basic commands.
commands         Basic help for all commands.
custom-topic     A custom topic.
hidden-commands  Basic help for hidden commands.
topics           Topics list.
""")

    def test_run_with_custom_topic(self):
        """
        Custom topic text is shown if its name matches the topic passed to
        C{help}.
        """
        content = """\
A custom topic.

Long descriptive text that
spans multiples lines.
"""
        path = os.path.join(self.factory.directory.path, "custom-topic.txt")
        self.factory.directory.make_path(content, path)
        self.factory.controller.load_path(self.factory.directory.path)
        self.command.run(topic="custom-topic")
        self.assertEquals(self.command.outf.getvalue(), """\
Long descriptive text that
spans multiples lines.
""")

    def test_run_with_custom_topic_strips_whitespace(self):
        """Trailing whitespace in custom help text is trimmed."""
        content = """\
A custom topic.


This is descriptive text.


"""
        path = os.path.join(self.factory.directory.path, "custom-topic.txt")
        self.factory.directory.make_path(content, path)
        self.factory.controller.load_path(self.factory.directory.path)
        self.command.run(topic="custom-topic")
        self.assertEquals(self.command.outf.getvalue(),
                          "This is descriptive text.\n")

    def test_run_with_python_command_topic(self):
        """
        Python commands used C{bzrlib.commands.Command.get_help_text} to get
        nicely formatted help text with information about command-line
        arguments and options included.
        """

        class cmd_test_command(Command):
            """A test command.

            This is the help text for this test command.
            """
            pass

        self.factory.create_command("test-command", cmd_test_command)
        self.command.run(topic="test-command")
        expected = dedent("""\
            Purpose: A test command.
            Usage:   commandant test-command

            Options:
              --usage        Show usage message and options.
              ...
              -h, --help     Show help message.

            Description:
              This is the help text for this test command.
            """)
        self.assertThat(
            self.command.outf.getvalue(),
            DocTestMatches(expected, doctest.ELLIPSIS))

    def test_run_with_python_command_without_docstring(self):
        """
        No help topic text is shown for a Python command without a docstring.
        """

        class cmd_test_command(Command):
            pass

        self.factory.create_command("test-command", cmd_test_command)
        self.command.run(topic="test-command")
        self.assertEquals(self.command.outf.getvalue(), "")

    def test_run_with_unknown_command_or_topic_name(self):
        """
        Running the C{help} command with an unknown topic results in an error
        message being shown.
        """
        self.command.run(topic="test-command")
        self.assertEquals(self.command.outf.getvalue(),
                          "test-command is an unknown command or topic.\n")


class CustomHelpCommandTest(ResourcedTestCase):
    """Tests for L{cmd_help} with custom program details."""

    resources = [(
        "factory", CommandFactoryResource(
            "test-program", "42.7.13", "A test program.",
            "http://example.com"))]

    def setUp(self):
        super(CustomHelpCommandTest, self).setUp()
        self.command = self.factory.create_command("help", cmd_help)
        self.basic_help_topic = (
            self.factory.create_help_topic("basic", topic_basic))

    def test_run_with_stock_help_text(self):
        """The help command displays the stock help text."""
        self.command.run()
        self.assertEquals(self.command.outf.getvalue(), """\
test-program -- A test program.
http://example.com

Basic commands:
  test-program help commands  List all commands
  test-program help topics    List all help topics
""")
