from bzrlib.commands import Command


class cmd_rock_fact(Command):
    """Show a fact about rocks.

    This command prints a fascinating fact about rocks.
    """

    def run(self):
        print >>self.outf, "Rocks are really hard."
