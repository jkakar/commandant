Commandant is a toolkit for building command-oriented tools.

A command driven program takes a command name as its first argument.
Subsequent arguments and options are passed to the command to
customize its behaviour.  Commandant is inspired by Bazaar's user
interface and is, in fact, a thin wrapper on top of `bzrlib`.


## License

Commandant is a toolkit for building command-oriented tools.
Copyright (C) 2009-2010 Jamshed Kakar.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

On Ubuntu systems, the complete text of the GNU General Public
Version 2 License is in `/usr/share/common-licenses/GPL-2`.


## Setting up a development environment

Install dependencies and run the test suite:

    virtualenv .
    . bin/activate
    make

Or create the virtualenv with `virtualenvwrapper`:

    mkvirtualenv commandant
    make

And then easily switch to it in the future:

    workon commandant

Run tests:

    make check


## Using Commandant

Commandant can be used as a command runner.  The `bin/commandant`
program can present an application made up of commands and help topics
grouped together in a directory.  The `example` program described in
the following sections is available in the `example` directory.  You
can try it out from the current directory by running the following
commands:

```bash
alias example="bin/commandant example"
source example/tab-completion.sh
```

### Create a Commandant program

Commands are grouped into Commandant programs.  A Commandant program
is made up of an arbitrary number of commands stored in a directory:

```bash
mkdir -p ~/example
```

An alias can be used to provide a name that can used to run commands
in the Commandant program:

```bash
alias example="commandant ~/example"
```

### Getting help

Commands provides builtin `help` and `version` commands.  Running
the `example` program by itself shows basic help information:

```
Commandant -- a toolkit for building command-oriented tools
https://github.com/jkakar/commandant

Basic commands:
  commandant help commands  List all commands
  commandant help topics    List all help topics
```

Running `example help commands` lists the commands that are available,
with a short summary about each one:

```
help    Show help about a command or topic.
version Show version of commandant.
```

Running `example help topics` lists the help topics that are
available, with a short summary about each one:

```
commands   Basic help for all commands.
topics     Topics list.
```

Running `example version` shows the version of Commandant being used:

```
commandant 0.5.0
```

### Create an executable command

One of the easiest ways to add a command to a Commandant program is by
creating a shell script and making it executable:

```bash
echo -e '#!/bin/sh\necho Hello, world!' > ~/example/hello
chmod +x ~/example/hello
```

The new `hello` command in the `example` program is now registered and
displayed when you run `example help commands`:

```
hello
help    Show help about a command or topic.
version Show version of commandant.
```

You should see `Hello, world!` printed to your screen when you run
`example hello`:

```
Hello, world!
```

### Create an executable command that takes arguments

Commandant will pass all arguments beyond the command name to the
executable for that command:

```bash
echo -e '#!/bin/sh\necho $*' > ~/example/echo
chmod +x ~/example/echo
```

Again, just by putting an executable file in the command directory,
the new `echo` command has been added to the `example` program which
you can see by running `example help commands`:

```
echo
hello
help    Show help about a command or topic.
version Show version of commandant.
```

The new command will repeat whatever we tell it when we run `example
echo Hello there!`:

```
Hello there!
```

### Providing help for commands

The commands in the `example` program have been very easy to add, but
they could be easier to use.  Commandant's builtin help system can be
extended to provide help topics for user-provided commands.  Files in
the command directory with a .txt extension, and with the same name as
a command, will be treated as help content for that command.  Adding
help content for the `hello` command is quite easy (see
*~/example/hello.txt*):

```
Greet the world!

Print 'Hello, world!' to the screen.
```

The first line in a help topic is used as a short description.  This
short description is used when listing commands with `example help
commands`:

```
echo
hello    Greet the world!
help     Show help about a command or topic.
version  Show version of commandant.
```

Notice that the `hello` command uses the short description from the
help topic.  The complete help text can be seen by running `example
help hello`:

```
Print 'Hello, world!' to the screen.
```

### Providing a custom splash page

The stock help text shown when the `help` command is run points users
to the list of commands and help topics.  It can be overridden by
providing a file called `basic.txt` (see *~/example/basic.txt*):

```
example -- A collection of command examples that work with Commandant.
https://github.com/jkakar/commandant

Basic commands:
  example help commands  List all commands
  example help topics    List all help topics
```

The contents of this file are shown when `example help` is run without
a topic.

### Providing help topics

The builtin help system can also be used to provide general help
topics, not bound to any command name.  Files in the command directory
with a `.txt` extension, and with a name that doesn't match any
command name, will be treated as help topics.  Adding help to describe
a concept, for example, is quite easy (see *~/example/greetings.txt*):

```
Greetings are a way to initiate communication.

Greeting (also called accosting) is a way for human beings (as well
as other members of the animal kingdom) to intentionally communicate
awareness of each other's presence, to show attention to, and to
suggest a type of relationship or social status between individuals
or groups of people coming in contact with each other.

Taken from http://en.wikipedia.org/wiki/Greeting.
```

As with help files for commands, the first line contains a short
summary with help text following.  The topic will now appear in the
topics list when `example help topics` is run:

```
commands   Basic help for all commands.
greetings  Greetings are a way to initiate communication.
topics     Topics list.
```

The contents of this file are shown when `example help greetings` is
run.

### Create a Python command

Executable commands such as shell scripts are great for some tasks,
but they are unweildy for others.  Commandant builds on `bzrlib`'s
command API for implementing Python commands, which are useful in
situations where executable commands don't work well, such as when
complex command-line argument and option parsing is required.  When
Commandant loads commands from the command directory it imports Python
commands from files with a `.py` extension.  The commands in the files
need to subclass the Command class and need to be named using the
`cmd_<name>` naming convention (see *~/example/rock-fact.py*):

```python
from bzrlib.commands import Command

class cmd_rock_fact(Command):
    """Show a fact about rocks.

    This command prints a fascinating fact about rocks.
    """
    def run(self):
        print >>self.outf, "Rocks are really hard."
```

Just like with executable commands, adding a Python command is as easy
as adding a file to the command directory.  An `outf` attribute will
be set on the command object when it's run and should be used when
printing text.  Run `example help commands` to see the command:

```
echo
hello      Greet the world!
help       Show help about a command or topic.
rock-fact  Show a fact about rocks.
version    Show version of commandant.
```

The new command is available using the name of the class, without the
`cmd_` part, and with underscores converted to dashes.  The doctring
is used to provide builtin help.  The first line is used as the
summary and the subsequent content is used as the help text, just like
in help files for executable commands such as `example help rock-fact`:

```
This command prints a fascinating fact about rocks.
```

More than one Command implementation can be provided in a single
Python file.

### Create a Python command that takes arguments

One of the main advantages of writing Python commands is being able to
express command-line argument and option parameters.  `bzrlib` uses
this data to automatically provide parsing and integration with the
help system (see *~/example/fortune.py*):

```python
from random import randint

from bzrlib.commands import Command

FORTUNES = ["%s will win a million dollars",
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
```

The functionality provides by `bzrlib`'s Command implementation makes
it possible to write commands with very rich command-line
interfaces.

### Create a Python command that uses Twisted

Twisted is a popular toolkit for asynchronous network programming.
Commandant has builtin support for writing commands that need to run
in a Twisted reactor.  Simply subclass `TwistedCommand` and implement
a command as you normally would.  It's `run()` method will be called
inside a running reactor (see *~/example/get-page.py*):

```python
from twisted.internet import reactor
from twisted.internet.ssl import ClientContextFactory
from twisted.web.client import HTTPClientFactory

from commandant.commands import TwistedCommand

class cmd_get_page(TwistedCommand):
    """Download a web page using Twisted and print it to the screen.

    This command uses Twisted to download a web page and demonstrates how to
    write an asynchronous command with Commandant.
    """

    takes_args = ["url"]

    def run(self, url):
        """Fetch the page at C{url} and print it to the screen."""
        client = HTTPClientFactory(url)
        if client.scheme == "https":
            factory = ClientContextFactory()
            reactor.connectSSL(client.host, client.port, client, factory)
        else:
            reactor.connectTCP(client.host, client.port, client)

        def write_response(self, result):
            print >>self.outf, result.decode("utf-8")

        def write_failure(self, failure):
            print >>self.outf, failure

        client.deferred.addCallback(write_response)
        client.deferred.addErrback(write_failure)
        return client.deferred
```

When the command finishes, the reactor will be stopped.


## Embedding Commandant in an application

To this point, the examples have centered around commands and help
topics grouped together in directory, with `bin/commandant` used to
present a frontend.  This mode of using Commandant is useful in
certain situations, but much of the time embedding Commandant directly
in an application is more desirable.

### Bootstrapping an application

The first step is to create an entry point which registers commands
and help topics and then subsequently runs your program.  The
`CommandController` is both a registry and dispatching device:

```python
from commandant import builtins
from commandant.controller import CommandController

def main(argv):
    """Run the command named in C{argv}.

    If a command name isn't provided the C{help} command is shown.

    @param argv: A list command-line arguments.  The first argument should be
       the name of the command to run.  Any further arguments are passed to
       the command.
    """
    if len(argv) < 2:
        argv.append("help")

    controller = CommandController("name", "version", "summary", "url")
    controller.load_module(builtins)
    controller.install_bzrlib_hooks()
    controller.run(argv[1:])
```

The name, version, summary and URL are used in generated help text.
The `builtins` module contains the builtin `help` and `version`
commands, and the `basic`, `commands`, `hidden-commands` and `topics`
help topics.

### Registering application commands

Commands can be grouped in a module and registered with the command
controller.  Just like in the examples above, command classes should
be named using the `cmd_command_name` naming convention and will be
loaded automatically when the module is registered.  If all the
commands in the examples above were grouped in an `example.commands`
module they could be registered just like the builtin commands:

```python
from example import commands

controller.load_module(commands)
```

### Create a Python help topic

In the examples above, help topics are text files in a directory.
When embedding Commandant in an application, its easier to use Python
for help topics:

```python
from commandant.help_topics import DocstringHelpTopic

class topic_sample_document(DocstringHelpTopic):
    """This first line is the short topic summary.

    The rest of the docstring is the help topic content and will
    be shown when the `example help sample-document` command is
    run.
    """
```

### Registering help topics

Registering help topics is just like registering commands.  They can
be grouped in a module and registered with the command controller.
Topics should use the `topic_document_name` naming convention:

```python
from example import help_topics

controller.load_module(help_topics)
```

### Providing a custom splash page

The stock help text shown when the `help` command is run points users
to the list of commands and help topics that have been registered with
the controller.  If a `topic_basic` help topic has been registered it
will be shown instead of the builtin splash page.


## Making a release

The first thing to do is login:

    make login

When you're authenticated you can upload a new version to PyPI:

    make publish

Optionally, you can create a tarball release:

    make release

