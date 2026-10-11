#!/usr/bin/env bash
# Publish a complete static site without changing the application's checkout.
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_dir"
npm run build:pages

publication_dir="$(mktemp -d "${TMPDIR:-/tmp}/anatomy-pages.XXXXXX")"
trap 'rm -rf "$publication_dir"' EXIT
remote_url="$(git remote get-url origin)"
author_name="$(git config user.name)"
author_email="$(git config user.email)"
source_revision="$(git rev-parse --short HEAD)"

git clone --shared --no-checkout "$repo_dir" "$publication_dir"
git -C "$publication_dir" remote set-url origin "$remote_url"
existing_branch="$(git ls-remote --heads "$remote_url" refs/heads/gh-pages)"
if [[ -n "$existing_branch" ]]; then
  git -C "$publication_dir" fetch origin gh-pages
  git -C "$publication_dir" switch -c gh-pages FETCH_HEAD
  git -C "$publication_dir" rm -rf --ignore-unmatch .
else
  git -C "$publication_dir" switch --orphan gh-pages
fi

cp -a dist/. "$publication_dir/"
touch "$publication_dir/.nojekyll"
git -C "$publication_dir" config user.name "$author_name"
git -C "$publication_dir" config user.email "$author_email"
git -C "$publication_dir" add --all
if git -C "$publication_dir" diff --cached --quiet; then
  echo "GitHub Pages already contains this build."
  exit 0
fi
git -C "$publication_dir" commit -m "Publish anatomy atlas from $source_revision"
git -C "$publication_dir" push origin HEAD:gh-pages
