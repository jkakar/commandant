#!/bin/bash

# Template based on bzr.simple for enabling bash completion for
# Commandant programs.  Replace commandant-program below with the
# name of your Commandant program.  Replace commandant_program below
# with the name of your Commandant program, but with dashes
# converted to underscores.  source the resulting file to enable
# completion.

_commandant_program_commands()
{
     commandant-program help commands | sed -r 's/^([-[:alnum:]]*).*/\1/' | grep '^[[:alnum:]]'
}

_commandant_program()
{
    cur=${COMP_WORDS[COMP_CWORD]}
    prev=${COMP_WORDS[COMP_CWORD-1]}
    if [ $COMP_CWORD -eq 1 ]; then
        COMPREPLY=( $( compgen -W "$(_commandant_program_commands)" $cur ) )
    elif [ $COMP_CWORD -eq 2 ]; then
        case "$prev" in
        help)
            COMPREPLY=( $( compgen -W "$(_commandant_program_commands) commands" $cur ) )
            ;;
        esac
    fi
}

complete -F _commandant_program -o default commandant-program
