"""Unit tests for L{commandant.formatting}."""

from cStringIO import StringIO
from unittest import TestCase

from commandant.formatting import print_columns


class PrintColumnsTest(TestCase):
    """Tests for L{print_columns}."""

    def setUp(self):
        super(PrintColumnsTest, self).setUp()
        self.outf = StringIO()

    def test_no_rows(self):
        """No output is produced if the input rows list is empty."""
        print_columns(self.outf, [])
        self.assertEquals(self.outf.getvalue(), "")

    def test_one_column(self):
        """A sequence of single-element lists is printed as a list of items."""
        print_columns(self.outf, [["1234"], ["2345"]])
        self.assertEquals(self.outf.getvalue(), "1234\n2345\n")

    def test_many_columns(self):
        """
        A sequence of multi-element lists is printed as a list of columns.
        """
        print_columns(self.outf, [["1234", "A description"]])
        self.assertEquals(self.outf.getvalue(), "1234  A description\n")

    def test_padding(self):
        """
        The optional C{padding} parameter can be used to change the amount of
        padding used between columns.
        """
        print_columns(self.outf, [["1234", "A description"]], padding=5)
        self.assertEquals(self.outf.getvalue(), "1234     A description\n")

    def test_shrink_index(self):
        """
        The optional C{shrink_index} parameter specifies the column to
        truncate, should the line being output exceed the C{max_width}.
        """
        description = ("A long description that will be truncated by the "
                       "shrinking logic")
        print_columns(self.outf, [["1234", description]], shrink_index=1)
        self.assertEquals(self.outf.getvalue(),
                          "1234  %s\n" % (description[:71],))

    def test_max_width(self):
        """The optional C{max_width} parameter sets the maximum line length."""
        description = ("A long description that will be truncated by the "
                       "shrinking logic")
        print_columns(self.outf, [["1234", description]], shrink_index=1,
                      max_width=68)
        self.assertEquals(self.outf.getvalue(),
                          "1234  %s\n" % (description[:62],))

    def test_max_width_ignored_without_shrink_index(self):
        """
        The C{max_width} parameter is ignored if a C{shrink_index} isn't
        provided.
        """
        description = ("A long description that will be truncated by the "
                       "shrinking logic")
        print_columns(self.outf, [[description]], max_width=10)
        self.assertEquals(self.outf.getvalue(), "%s\n" % (description,))

    def test_last_item_has_no_trailing_whitespace(self):
        """
        The text for the last column output for each line shouldn't have any
        trailing whitespace.
        """
        print_columns(self.outf, [["up"], ["down"]])
        self.assertEquals(self.outf.getvalue(), """\
up
down
""")
