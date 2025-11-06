#!/usr/bin/env bash
# mkgitlinks.sh - Manage relative symlinks for git repositories
#
# Ensures git-committed symlinks are:
#   - Relative (not absolute) for portability across clones
#   - Symbolic (not file copies) for space efficiency
#   - Clean (no broken/stale links cluttering directories)
#
# Usage: mkgitlinks.sh [-n] [-f] [-c] <links_dir> <target>
#   -n, --dry-run   Show what would happen
#   -f, --force     Replace regular files with symlinks
#   -c, --cleanup   Remove broken/orphaned symlinks
#
# Example (in git hook):
#   ./scripts/mkgitlinks.sh --cleanup \
#     docs/code_stubs/module/dev_notes \
#     kanji_time/module/dev_notes
#
# LLM DISCLOSURE: Created interactively with review input from ChatGPT 5 and Claude Sonnet 4.5

set -euo pipefail

dry_run=false
force=false
cleanup=false

# Parse options
while [[ $# -gt 0 ]]; do
  case "$1" in
    -n|--dry-run)
      dry_run=true
      shift
      ;;
    -f|--force)
      force=true
      shift
      ;;
    -c|--cleanup)
      cleanup=true
      shift
      ;;
    -*)
      echo "Unknown option: $1" >&2
      echo "Usage: $0 [-n|--dry-run] [-f|--force] [-c|--cleanup] <links_dir> <target>" >&2
      exit 1
      ;;
    *)
      break
      ;;
  esac
done

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 [-n|--dry-run] [-f|--force] [-c|--cleanup] <links_dir> <target>" >&2
  echo "  target can be a directory or a single file" >&2
  exit 1
fi

# Check that unusual tools are present.
# Let errors occur naturally for missing standard tools.
if ! command -v realpath >/dev/null 2>&1; then
  echo "Error: realpath not found. Install coreutils." >&2
  exit 127
fi

# Check for GNU realpath (BSD realpath lacks required flags)
if ! realpath --version 2>&1 | grep -q GNU; then
  echo "Error: GNU realpath required (BSD variant detected)" >&2
  if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "macOS detected. Install GNU coreutils:" >&2
    echo "  brew install coreutils" >&2
    if command -v grealpath >/dev/null 2>&1; then
      echo "Note: grealpath is available - you can:" >&2
      echo "  1. Alias: alias realpath=grealpath" >&2
      echo "  2. Symlink: ln -s \$(which grealpath) /usr/local/bin/realpath" >&2
    fi
  else
    echo "Install GNU coreutils for your platform" >&2
  fi
  exit 127
fi

links_dir=$1
target=$2

# Sanity checks - fail before touching filesystem
if [[ ! -e "$target" ]]; then
  echo "Error: target does not exist: $target" >&2
  exit 1
fi

if [[ ! -d "$links_dir" ]]; then
  if $dry_run; then
    echo "[DRY-RUN] Would create links_dir: $links_dir"
  else
    echo "Creating links_dir: $links_dir"
    mkdir -p "$links_dir"
  fi
fi

# Normalize to absolute paths
links_dir=$(realpath -m "$links_dir")
target=$(realpath -m "$target")

# Safety check: prevent same-directory operations
if [[ "$links_dir" == "$target" ]]; then
  echo "Error: links_dir and target cannot be the same" >&2
  exit 1
fi

# Track statistics
created=0
updated=0
skipped=0
removed=0
forced=0

# Factor out the link creation logic
process_file() {
  local tgt=$1
  local base=$(basename -- "$tgt")
  local link="$links_dir/$base"
  local rel=$(realpath --relative-to="$links_dir" "$tgt")

  # Handle existing regular files
  if [[ -e "$link" && ! -L "$link" ]]; then
    if $force; then
      if $dry_run; then
        echo "[DRY-RUN] FORCE: Would remove regular file and create link: $link -> $rel"
      else
        echo "FORCE: Removing regular file: $link"
        rm "$link"
        echo "CREATE: $link -> $rel"
        ln -snf -- "$rel" "$link"
      fi
      ((forced++)) || true
      return
    else
      echo "SKIP: $link (exists, not a symlink; use --force to overwrite)"
      ((skipped++)) || true
      return
    fi
  fi

  # Skip if link already correct
  if [[ -L "$link" ]]; then
    local current=$(readlink "$link" || true)
    if [[ "$current" == "$rel" ]]; then
      echo "OK: $link -> $rel (already correct)"
      ((skipped++)) || true
      return
    fi
    # Link exists but points to wrong target
    if $dry_run; then
      echo "[DRY-RUN] Would update: $link -> $rel (currently: $current)"
    else
      echo "UPDATE: $link -> $rel (was: $current)"
    fi
    ((updated++)) || true
  else
    # Link doesn't exist
    if $dry_run; then
      echo "[DRY-RUN] Would create: $link -> $rel"
    else
      echo "CREATE: $link -> $rel"
    fi
    ((created++)) || true
  fi

  # Create or update symlink
  $dry_run || ln -snf -- "$rel" "$link"
}

# Cleanup mode: remove broken/orphaned symlinks
if $cleanup; then
  echo "Cleanup mode: Checking for orphaned symlinks in $links_dir"
  
  # Get absolute target path for comparison
  target_abs=$(realpath -m "$target")
  
  # Find all symlinks in links_dir
  while IFS= read -r -d '' link; do
    echo "Removing $link"
    # Check if symlink is broken
    if [[ ! -e "$link" ]]; then
      if $dry_run; then
        echo "[DRY-RUN] CLEANUP: Would remove broken link: $link"
      else
        echo "CLEANUP: Removing broken link: $link"
        rm "$link"
      fi
      ((removed++)) || true
      continue
    fi
    # Check if symlink points outside target directory
    link_target=$(readlink -f "$link" || true)
    if [[ -n "$link_target" ]]; then
      # Check if link target is under target directory
      case "$link_target" in
        "$target_abs"/*|"$target_abs")
          # Points to something in target - keep it
          ;;
        *)
          # Points outside target - remove it
          if $dry_run; then
            echo "[DRY-RUN] CLEANUP: Would remove orphaned link: $link (points to: $link_target)"
          else
            echo "CLEANUP: Removing orphaned link: $link (points outside target)"
            rm "$link"
          fi
          ((removed++)) || true
          ;;
      esac
    fi
  done < <(find "$links_dir" -type l -print0 2>/dev/null || true)
  
  echo ""
fi

# Handle single file vs. directory
if [[ -f "$target" ]]; then
  # Single file mode
  echo "Processing single file: $target"
  process_file "$target"
elif [[ -d "$target" ]]; then
  # Directory mode - process all regular files at top level
  while IFS= read -r -d '' tgt; do
    process_file "$tgt"
  done < <(find "$target" -type f -print0)
else
  echo "Error: target is neither a regular file nor directory: $target" >&2
  exit 1
fi

# Summary
echo ""
echo "Summary:"
echo "  Created: $created"
echo "  Updated: $updated"
echo "  Skipped: $skipped"
$force && echo "  Forced:  $forced"
$cleanup && echo "  Removed: $removed"
$dry_run && echo "  (DRY-RUN: No changes made)"