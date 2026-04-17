#!/usr/bin/env bash
# Deploy dist/ to the gh-pages branch of origin as a clean orphan commit.
#
# Why not the `gh-pages` CLI?  v6.3.0 clones the default branch first, so main's
# tracked files (.claude/, claude/.superpowers/, nested .gitignores) leak into
# the gh-pages branch, and the root .gitignore's `*.xlsx` rule filters out
# dist/data/PERFORMANCE_REPORT.xlsx during `git add -A`.  This script sidesteps
# both by staging dist/ in a temp dir with `git init`, so no parent state
# bleeds in.
set -euo pipefail

DIST_DIR="$(cd "$(dirname "$0")/.." && pwd)/dist"
REMOTE_URL="https://github.com/rhurst1029/stat_scraper.git"
BRANCH="gh-pages"

if [[ ! -d "$DIST_DIR" ]]; then
  echo "dist/ not found at $DIST_DIR — run 'npm run build' first" >&2
  exit 1
fi

DEPLOY_DIR="$(mktemp -d)"
trap 'rm -rf "$DEPLOY_DIR"' EXIT

cp -R "$DIST_DIR/." "$DEPLOY_DIR/"
touch "$DEPLOY_DIR/.nojekyll"

cd "$DEPLOY_DIR"
git init -q -b "$BRANCH"
git add -A
git -c user.name="Ryan Hurst" -c user.email="rhurst1029@gmail.com" \
    commit -q -m "Deploy Pacific Cup Dashboard"
git remote add origin "$REMOTE_URL"
git push -f origin "$BRANCH"

echo "Deployed to https://rhurst1029.github.io/stat_scraper/"
