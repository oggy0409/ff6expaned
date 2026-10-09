import sys
lo,hi=[int(x.replace(':',''),16) for x in sys.argv[1:3]]
for l in open(sys.argv[3] if len(sys.argv)>3 else '/tmp/claude-0/-home-user-ff6expaned/50190d0f-15ac-56a1-947a-50a94afc6a25/scratchpad/insn.tsv'):
    p=l.rstrip('\n').split('\t')
    a=int(p[0].replace(':',''),16)
    if lo<=a<=hi: print(p[0],p[1].ljust(12),p[6] if len(p)>6 else '', '  ;', p[5].split('/')[-1] if len(p)>5 else '')
