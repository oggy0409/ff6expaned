#!/bin/bash
# usage: dis.sh START END   (e.g. C0:9FD0 C0:A030)
awk -F'\t' -v a="$1" -v b="$2" '$1>=a && $1<=b {printf "%s  %-12s %s\n",$1,$2,$7}' /tmp/claude-0/-home-user-ff6expaned/50190d0f-15ac-56a1-947a-50a94afc6a25/scratchpad/insn.tsv
