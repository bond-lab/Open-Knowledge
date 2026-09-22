#!/bin/bash
#
# Build the slides, copy them into the website, and freeze the static site
# into docs/.  Run this before committing whenever slides/ or web/ changed:
# it is the only thing that keeps slides/*.pdf, web/static/pdf/*.pdf and
# docs/ in step with each other.
#
#   ./freeze.sh              build the slides, copy them, freeze
#   ./freeze.sh --no-slides  freeze only (when nothing in slides/ changed)
#
set -euo pipefail

cd "$(dirname "$0")"

SLIDES=yes
[ "${1:-}" = "--no-slides" ] && SLIDES=no

# Ensure uv is installed
if ! command -v uv &>/dev/null; then
  echo "❌ uv not found. Please install it first: https://github.com/astral-sh/uv"
  exit 1
fi

# Create the virtual environment if missing
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  uv venv .venv
fi

if [ "$SLIDES" = yes ]; then
  # ---- build every deck and handout ----------------------------------------
  echo "Building slides..."
  cd slides
  for tex in *.tex; do
    [ "$tex" = "shared.tex" ] && continue      # preamble, not a document
    if ! latexmk -lualatex -interaction=nonstopmode "$tex" >/dev/null 2>&1; then
      echo "❌ ${tex%.tex} failed to build — run: latexmk -lualatex $tex"
      exit 1
    fi
    printf '   %-28s %s pages\n' "${tex%.tex}" \
      "$(pdfinfo "${tex%.tex}.pdf" | awk '/Pages/{print $2}')"
  done

  # ---- warn about the mistakes that do not stop a build --------------------
  problems=0
  for log in *.log; do
    for pattern in 'Missing character' 'Citation.*undefined' 'Overfull \\vbox'; do
      n=$(grep -c "$pattern" "$log" || true)
      if [ "$n" -gt 0 ]; then
        printf '   ⚠  %-28s %s: %s\n' "${log%.log}" "$pattern" "$n"
        problems=$((problems + 1))
      fi
    done
  done
  [ "$problems" -eq 0 ] && \
    echo "   no missing glyphs, undefined citations, or frames off the slide"
  cd ..

  # ---- copy into the website -----------------------------------------------
  echo "Copying PDFs into web/static/pdf..."
  for pdf in slides/*.pdf; do
    target="web/static/pdf/$(basename "$pdf")"
    if [ ! -f "$target" ] || ! cmp -s "$pdf" "$target"; then
      cp "$pdf" "$target"
      echo "   updated $(basename "$pdf")"
    fi
  done
else
  echo "Skipping slides (--no-slides)"
fi

# Activate and run commands inside uv
echo "Installing dependencies..."
uv pip install -q -r requirements.txt

echo "Running freeze.py..."
uv run python freeze.py

echo
echo "Now check what changed:  git status --short"
