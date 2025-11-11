#!/bin/bash
# add_copyright.sh - Add AGPL copyright headers to Python files
#
# LLM DISCLOSURE: Created with Claude Sonnet 4.5 & human-reviewed for correctness.


set -e

AUTHOR="Andrew Milton"
YEARS="2024, 2025"
LICENSE="AGPL-3.0-or-later"

add_header() {
    local file="$1"
    local basename=$(basename "$file")
    
    # Check if top 3 lines contain copyright or SPDX
    if head -n 3 "$file" | grep -qi -e "Copyright" -e "SPDX-License-Identifier"; then
        echo "SKIP: $file (already has copyright)"
        return
    fi
    
    # Create temp file with header
    local tmp=$(mktemp)
    {
        echo "# $basename"
        echo "# Copyright (C) $YEARS $AUTHOR"
        echo "# SPDX-License-Identifier: $LICENSE"
        echo ""
        cat "$file"
    } > "$tmp"
    
    # Replace original
    mv "$tmp" "$file"
    echo "ADDED: $file"
}

# Main
if [ $# -eq 0 ]; then
    echo "Usage: $0 <file.py> [file2.py ...] OR $0 <directory>"
    exit 1
fi

for arg in "$@"; do
    if [ -f "$arg" ] && [[ "$arg" == *.py ]]; then
        add_header "$arg"
    elif [ -d "$arg" ]; then
        # Find all .py files in directory
        find "$arg" -type f -name "*.py" | while read -r pyfile; do
            add_header "$pyfile"
        done
    else
        echo "SKIP: $arg (not a .py file or directory)"
    fi
done

echo ""
echo "Done! Review changes with: git diff"