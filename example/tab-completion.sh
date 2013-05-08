#!/bin/bash

# Template based on bzr.simple for enabling bash completion for
# Commandant programs.

_example_commands()
{
     example help commands | sed -r 's/^([-[:alnum:]]*).*/\1/' | grep '^[[:alnum:]]'
}

_example()
{
    cur=${COMP_WORDS[COMP_CWORD]}
    prev=${COMP_WORDS[COMP_CWORD-1]}
    if [ $COMP_CWORD -eq 1 ]; then
        COMPREPLY=( $( compgen -W "$(_example_commands)" $cur ) )
    elif [ $COMP_CWORD -eq 2 ]; then
        case "$prev" in
        help)
            COMPREPLY=( $( compgen -W "$(_example_commands) commands" $cur ) )
            ;;
        esac
    fi
}

complete -F _example -o default example
