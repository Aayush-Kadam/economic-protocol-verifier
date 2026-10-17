#!/usr/bin/env bash
# Build the actual pinned upstream checker; no global install or substitute.
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
source_dir="$root/.tools/carcara-source"
commit="051d2f79ccd3d5736bb3d93356f05df3dfc696e9"
upstream="https://github.com/ufmg-smite/carcara.git"
mkdir -p "$root/.tools"
if [ ! -e "$source_dir" ]; then
  git clone "$upstream" "$source_dir"
fi
test "$(git -C "$source_dir" remote get-url origin)" = "$upstream"
test -z "$(git -C "$source_dir" status --porcelain)"
git -C "$source_dir" checkout --detach "$commit"
test "$(git -C "$source_dir" rev-parse HEAD)" = "$commit"
cargo build --release --locked --bin carcara --manifest-path "$source_dir/Cargo.toml" --target-dir "$root/.tools/carcara-build"
cp "$root/.tools/carcara-build/release/carcara" "$root/.tools/carcara-current"
"$root/.tools/carcara-current" --version
