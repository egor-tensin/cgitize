#!/usr/bin/env dash

script_dir="$( dirname -- "$0" )"
cd -- "$script_dir/html-converters/"

path="$1"
path="$( echo "$1" | tr '[:upper:]' '[:lower:]' )"

case "$path" in
    *.markdown|*.mdown|*.md|*.mkd)
        exec ./md2html
        ;;
esac
