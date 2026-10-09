#!/bin/bash
# TECH v0.9.3: build the bsnes libretro core used by tools/emu_bsnes.py (second, cycle-accurate emulator for the visual
# checks). bsnes is GPLv3 (https://github.com/bsnes-emu/bsnes); it is fetched and built locally, never shipped in the ROM.
# usage: tools/build_bsnes_core.sh [work dir, default /tmp/claude-0]   -> <work>/bsnes/bsnes/out/bsnes_libretro.so
set -e
W="${1:-/tmp/claude-0}"; T="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$W"; cd "$W"
[ -d bsnes ] || git clone https://github.com/bsnes-emu/bsnes.git bsnes
cd bsnes
git checkout -q "$(cat "$T/bsnes_ff6x/BSNES_COMMIT.txt")"
git checkout -q -- bsnes/target-libretro/GNUmakefile bsnes/target-libretro/program.cpp
git apply "$T/bsnes_ff6x/bsnes_ff6x.patch"
cp "$T/bsnes_ff6x/ff6x_dump.cpp" bsnes/target-libretro/ff6x_dump.cpp
make -C bsnes -j"$(nproc)" target=libretro binary=library
ls -la bsnes/out/bsnes_libretro.so
