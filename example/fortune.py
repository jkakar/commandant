from random import randint

from bzrlib.commands import Command
from bzrlib.option import Option

FORTUNES = ["%s will win a million dollars tomorrow",
            "%s will find deep satisfaction",
            "%s will develop a strong relationship"]

class cmd_fortune(Command):
    """Show a fortune.

    This command prints a fortune.
    """

    takes_args = ["name"]
    takes_options = [
        Option("crude", help="Add a crude suffix to the fortune.")]

    def run(self, name=None, crude=None):
        fortune = FORTUNES[randint(0, len(FORTUNES) - 1)] % (name,)
        if crude:
            fortune = "%s in bed" % (fortune,)
        print >>self.outf, fortune
