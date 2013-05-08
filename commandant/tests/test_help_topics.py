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

"""Unit tests for L{commandant.help_topics}."""

import doctest
import os
from textwrap import dedent

from testresources import ResourcedTestCase
from testtools import TestCase
from testtools.matchers import DocTestMatches

from commandant.help_topics import (
    HelpTopic, DocstringHelpTopic, FileHelpTopic, CommandHelpTopic)
from commandant.testing.basic import CommandantTestCase
from commandant.testing.resources import (
    TemporaryDirectoryResource, CommandFactoryResource)


class HelpTopicTest(TestCase):
    """Tests for L{HelpTopic}."""

    def test_instantiate(self):
        """
        L{HelpTopic} is a base class that needs to be overridden to be useful.
        """
        help_topic = HelpTopic()
        self.assertRaises(NotImplementedError, help_topic.get_summary)
        self.assertRaises(NotImplementedError, help_topic.get_text)


class DocstringHelpTopicTest(TestCase):

    def test_get_help_contents(self):
        """L{FileHelpTopic} loads topic summary and text from a file."""
        content = """\
This line contains a short summary for the help topic.

All remaining content makes up the long descriptive text for the help topic.
"""
        help_topic = DocstringHelpTopic()
        help_topic.__doc__ = content
        self.assertEquals(
            help_topic.get_summary(),
            "This line contains a short summary for the help topic.")
        self.assertEquals(
            help_topic.get_text(),
            "All remaining content makes up the long descriptive text for "
            "the help topic.")

    def test_get_help_contents_without_long_description(self):
        """L{FileHelpTopic} loads topic summary and text from a file."""
        help_topic = DocstringHelpTopic()
        help_topic.__doc__ = "This line contains a short summary."
        self.assertEquals(help_topic.get_summary(),
                          "This line contains a short summary.")
        self.assertEquals(help_topic.get_text(), "")


class FileHelpTopicTest(ResourcedTestCase):
    """Tests for L{FileHelpTopic}."""

    resources = [("directory", TemporaryDirectoryResource())]

    def test_instantiate(self):
        """L{FileHelpTopic} doesn't have a path by default."""
        help_topic = FileHelpTopic()
        self.assertEquals(help_topic.path, None)

    def test_get_help_contents(self):
        """L{FileHelpTopic} loads topic summary and text from a file."""
        content = """\
This line contains a short summary for the help topic.

All remaining content makes up the long descriptive text for the help topic.
"""
        help_topic_path = os.path.join(self.directory.path, "test-topic.txt")
        self.directory.make_path(content=content, path=help_topic_path)
        help_topic = FileHelpTopic()
        help_topic.path = help_topic_path
        self.assertEquals(
            help_topic.get_summary(),
            "This line contains a short summary for the help topic.")
        self.assertEquals(
            help_topic.get_text(),
            "All remaining content makes up the long descriptive text for "
            "the help topic.")


class CommandHelpTopicTest(CommandantTestCase):
    """Tests for L{CommandHelpTopic}."""

    resources = [("factory", CommandFactoryResource())]

    def test_instantiate(self):
        """
        L{CommandHelpTopic} exposes the C{bzrlib.commands.Command} it was
        created with via its C{command} attribute.
        """
        command = self.factory.create_command("fake-command")
        help_topic = CommandHelpTopic(command)
        self.assertEquals(help_topic.command, command)

    def test_get_help_contents(self):
        """
        L{CommandHelpTopic} loads topic summary and text from a
        C{bzrlib.commands.Command}.
        """
        command = self.factory.create_command("fake-command")
        command.name = lambda: "fake-command"
        help_topic = CommandHelpTopic(command)
        help_topic.controller = self.factory.controller
        self.assertEquals(help_topic.get_summary(), "Summary text.")
        expected = dedent("""\
            Purpose: Summary text.
            Usage:   commandant fake-command

            Options:
              ...

            Description:
              Long descriptive text that
              spans multiples lines.
            """)
        self.assertThat(
            help_topic.get_text() + "\n",
            DocTestMatches(expected, doctest.ELLIPSIS))


class CustomCommandHelpTopicTest(CommandantTestCase):
    """Tests for L{CommandHelpTopic} with custom program details."""

    resources = [("factory", CommandFactoryResource("test-program"))]

    def test_get_help_contents(self):
        """
        L{CommandHelpTopic} loads topic summary and text from a
        C{bzrlib.commands.Command}.
        """
        command = self.factory.create_command("fake-command")
        command.name = lambda: "fake-command"
        help_topic = CommandHelpTopic(command)
        help_topic.controller = self.factory.controller
        self.assertEquals(help_topic.get_summary(), "Summary text.")
        expected = dedent("""\
            Purpose: Summary text.
            Usage:   test-program fake-command

            Options:
              ...

            Description:
              Long descriptive text that
              spans multiples lines.
            """)
        self.assertThat(
            help_topic.get_text() + "\n",
            DocTestMatches(expected, doctest.ELLIPSIS))
