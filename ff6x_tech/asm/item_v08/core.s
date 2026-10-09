; =============================================================================
; FF6 Expanded Edition - TECH v0.7.1 Signature Equipment Bank - CORE (bank FA)
; =============================================================================
; Extended item IDs $100-$13F (low byte $00-$3F, high bit kept outside the vanilla byte).
;
; Saved RAM (audited free, SAVED_RAM_AUDIT_v0.7.1.md), 48 bytes $1CF8-$1D27:
;   XBITS  $1CF8-$1D23  352-bit field.  bit n -> byte $1CF8+(n>>3), mask 1<<(n&7)
;          n = 0..255            : inventory slot n holds an extended item ($100 | $1869[n])
;          n = 256+rec*6+slot    : character record rec (0..15), equip slot (0=weapon .. 5=relic 2)
;                                  holds an extended item ($100 | $161F[rec*37+slot])
;   XSIG   $1D24-$1D27  'X' 'I' version $01 ~version   (legacy saves hold Bushido-name bytes A5 9A A6 FF here)
;
; FAR routines: JSL with A16/XY16 (REP #$30) unless stated otherwise. DB and D are never used
; (all RAM access is long $7E:xxxx). Registers not listed as outputs are preserved; P is preserved
; except the documented carry result.
; =============================================================================

INVID   = $7E1869
INVQTY  = $7E1969
EQP0    = $7E161F               ; + rec*37 + slot
XBITS   = $7E1CF8
XSIG    = $7E1D24
EVBITS  = $7E1E80
XSIG01  = $4958                 ; 'X','I'
XSIG23  = $FE01                 ; version 1, ~version
NBITS_B = 44                    ; bytes of XBITS
EQBIT0  = 256
MAXQTY  = 99

.section XFA_CODE $FA8000

; ---------------------------------------------------------------------------
; stable far entry points (hooks in other banks only ever JSL to this table)
XJ_BitTst:      jml XBitTst             ; +$00
XJ_BitSet:      jml XBitSet             ; +$04
XJ_BitClr:      jml XBitClr             ; +$08
XJ_EqpN:        jml XEqpN               ; +$0C
XJ_Sanitize:    jml XSanitize           ; +$10
XJ_NewGame:     jml XNewGame            ; +$14
XJ_GiveExt:     jml XGiveExt            ; +$18
XJ_TakeExt:     jml XTakeExt            ; +$1C
XJ_HasExt:      jml XHasExt             ; +$20
XJ_ValidExt:    jml XValidExt           ; +$24
XJ_EvSwitch:    jml XEvSwitch           ; +$28
XJ_Arrange:     jml XArrange            ; +$2C
XJ_BattleEndInv: jml XBattleEndInv      ; +$30
XJ_HandNames:   jml XC1_HandNames       ; +$34
XJ_NameIdx:     jml XC1_NameIdx         ; +$38
XJ_SwapGuard:   jml XC1_SwapGuard       ; +$3C
XJ_JumpAnimR:   jml XC1_JumpAnimR       ; +$40
XJ_JumpAnimL:   jml XC1_JumpAnimL       ; +$44
XJ_HandSwapBits: jml XC1_HandSwapBits  ; +$48

        .a16
        .i16
; ===========================================================================
; near helpers (A16/XY16)
; ===========================================================================

; BitPrep: A = n -> X = n>>3, A = mask
BitPrep:
        pha
        lsr a
        lsr a
        lsr a
        tax
        pla
        and #$0007
        asl a
        phx
        tax
        lda f:XMaskW,x
        plx
        rts
        .a16
        .i16

; TstN: A = n -> A = (bit ? mask : 0), Z set if clear. X,Y preserved
TstN:
        phx
        jsr BitPrep
        and f:XBITS,x
        plx
        cmp #$0000
        rts
        .a16
        .i16

; SetN / ClrN: A = n. X,Y preserved, A destroyed
SetN:
        phx
        jsr BitPrep
        ora f:XBITS,x
        sta f:XBITS,x
        plx
        rts
        .a16
        .i16

ClrN:
        phx
        jsr BitPrep
        eor #$FFFF
        and f:XBITS,x
        sta f:XBITS,x
        plx
        rts
        .a16
        .i16

; ValidLo: A = low byte of an extended id -> C=1 if $100|lo is a DEFINED extended item. A destroyed, X,Y kept
ValidLo:
        cmp #$0040
        bcs @no
        phx
        tax
        lda f:XExtFlags,x
        plx
        and #$0001
        cmp #$0001
        rts
        .a16
        .i16
@no:    clc
        rts
        .a16
        .i16

; OfsToN: A = data offset of an equip slot byte relative to $161F (rec*37+slot) -> A = n. X,Y kept
OfsToN:
        phx
        ldx #EQBIT0
@sub:   cmp #37
        bcc @done
        sbc #37
        pha
        txa
        clc
        adc #6
        tax
        pla
        bra @sub
@done:  phx
        clc
        adc 1,s
        plx
        plx
        rts
        .a16
        .i16

; RetC: copy C into the P byte saved by the caller's PHP. Stack at the JSR: [P][...] i.e. P = 3,s inside
; RetC before its own PHA (5,s after it). A16, A and X/Y preserved.
RetC:
        pha
        sep #$20
        bcs @set
        lda 5,s
        and #$FE
        bra @st
@set:   lda 5,s
        ora #$01
@st:    sta 5,s
        rep #$20
        pla
        rts
        .a16
        .i16

; ===========================================================================
; far primitives
; ===========================================================================

; XBitTst: A = n -> A = 0/1, Z flag (in returned P) reflects A
XBitTst:
        php
        rep #$30
        jsr TstN
        beq @z
        lda #$0001
@z:     plp                     ; A = 0/1 (low byte valid in either width); flags = caller's
        rtl
        .a16
        .i16

XBitSet:
        php
        rep #$30
        pha
        jsr SetN
        pla
        plp
        rtl
        .a16
        .i16

XBitClr:
        php
        rep #$30
        pha
        jsr ClrN
        pla
        plp
        rtl
        .a16
        .i16

; XEqpN: A = equip-slot data offset relative to $161F (rec*37+slot) -> A = bit number n
XEqpN:
        php
        rep #$30
        jsr OfsToN
        plp
        rtl
        .a16
        .i16

; XValidExt: A = 16-bit id -> C=1 if a defined extended item ($100-$13F)
XValidExt:
        php
        rep #$30
        pha
        cmp #$0100
        bcc @no
        cmp #$0140
        bcs @no
        and #$00FF
        jsr ValidLo
        bra @ret
@no:    clc
@ret:   pla
        jsr RetC
        plp
        rtl
        .a16
        .i16

; ===========================================================================
; New Game / save load
; ===========================================================================

; ClearAll: zero XBITS and write the signature (A16/XY16, A/X destroyed)
ClearAll:
        ldx #$0000
        lda #$0000
@z:     sta f:XBITS,x
        inx
        inx
        cpx #NBITS_B
        bne @z
        lda #XSIG01
        sta f:XSIG
        lda #XSIG23
        sta f:XSIG+2
        rts
        .a16
        .i16

; XNewGame: (any mode) extended metadata = 0 + signature
XNewGame:
        php
        rep #$30
        pha
        phx
        jsr ClearAll
        plx
        pla
        plp
        rtl
        .a16
        .i16

; XSanitize: (any mode) called after a save slot has been copied to $1600-$1FFF and accepted.
;   no/legacy signature -> clear all extended metadata, write signature, vanilla bytes untouched
;   valid signature     -> drop stale bits (empty slot) and items whose extended id is not defined
XSanitize:
        php
        rep #$30
        pha
        phx
        phy
        lda f:XSIG
        cmp #XSIG01
        bne @legacy
        lda f:XSIG+2
        cmp #XSIG23
        beq @valid
@legacy:
        jsr ClearAll
        jmp @done
; inventory
@valid:
        ldx #$0000
@inv:   txa
        jsr TstN
        beq @inext
        lda f:INVID,x
        and #$00FF
        cmp #$00FF
        beq @iclr               ; empty slot: stale bit
        jsr ValidLo
        bcs @inext
        sep #$20                ; undefined extended id: remove the item, never truncate it
        .a8
        lda #$FF
        sta f:INVID,x
        lda #$00
        sta f:INVQTY,x
        rep #$20
        .a16
@iclr:  txa
        jsr ClrN
@inext: inx
        cpx #$0100
        bne @inv
; equipment: X = rec*37 + slot, Y = n
        ldx #$0000
        ldy #EQBIT0
@rec:   lda #$0006
        pha
@slot:  tya
        jsr TstN
        beq @snext
        lda f:EQP0,x
        and #$00FF
        cmp #$00FF
        beq @sclr
        jsr ValidLo
        bcs @snext
        sep #$20
        .a8
        lda #$FF
        sta f:EQP0,x
        rep #$20
        .a16
@sclr:  tya
        jsr ClrN
@snext: inx
        iny
        lda 1,s
        dec a
        sta 1,s
        bne @slot
        pla
        txa
        clc
        adc #37-6
        tax
        cpx #37*16
        bne @rec
@done:  ply
        plx
        pla
        plp
        rtl
        .a16
        .i16

; ===========================================================================
; extended give / take / has
; ===========================================================================

; FindInv: A = lo (0..$3F) -> C=1 and X = slot of the extended item $100|lo in inventory. A kept
FindInv:
        pha
        ldx #$0000
@l:     lda f:INVID,x
        and #$00FF
        cmp 1,s
        bne @n
        txa
        jsr TstN
        bne @hit
@n:     inx
        cpx #$0100
        bne @l
        pla
        clc
        rts
        .a16
        .i16
@hit:   pla
        sec
        rts
        .a16
        .i16

; XGiveExt: A = 16-bit id -> C=1 if added (stack +1, cap 99, or first empty slot)
XGiveExt:
        php
        rep #$30
        pha
        phx
        jsr XValidLocal
        bcc @ret
        and #$00FF
        jsr FindInv
        bcc @new
        sep #$20
        .a8
        lda f:INVQTY,x
        cmp #MAXQTY
        bcs @full
        inc a
        sta f:INVQTY,x
@full:  rep #$20
        .a16
        sec
        bra @ret
@new:   pha
        ldx #$0000
@e:     lda f:INVID,x
        and #$00FF
        cmp #$00FF
        beq @put
        inx
        cpx #$0100
        bne @e
        pla
        clc                     ; inventory full: nothing given (vanilla GiveItem would hang here)
        bra @ret
@put:   pla
        sep #$20
        .a8
        sta f:INVID,x
        lda #$01
        sta f:INVQTY,x
        rep #$20
        .a16
        txa
        jsr SetN
        sec
@ret:   plx
        pla
        jsr RetC
        plp
        rtl
        .a16
        .i16

; XValidLocal: like XValidExt (near, A16 kept, C result)
XValidLocal:
        pha
        cmp #$0100
        bcc @no
        cmp #$0140
        bcs @no
        and #$00FF
        jsr ValidLo
        pla
        rts
        .a16
        .i16
@no:    pla
        clc
        rts
        .a16
        .i16

; XTakeExt: A = 16-bit id -> C=1 if one was removed from the inventory (equipped copies are not touched)
XTakeExt:
        php
        rep #$30
        pha
        phx
        cmp #$0100
        bcc @no
        cmp #$0140
        bcs @no
        and #$00FF
        jsr FindInv
        bcc @ret
        sep #$20
        .a8
        lda f:INVQTY,x
        dec a
        sta f:INVQTY,x
        bne @kept
        lda #$FF
        sta f:INVID,x
        rep #$20
        .a16
        txa
        jsr ClrN
@kept:  rep #$20
        sec
        bra @ret
@no:    clc
@ret:   plx
        pla
        jsr RetC
        plp
        rtl
        .a16
        .i16

; XHasExt: A = 16-bit id -> C=1 if in the inventory or equipped in any of the 16 character records
XHasExt:
        php
        rep #$30
        pha
        phx
        phy
        cmp #$0100
        bcc @no
        cmp #$0140
        bcs @no
        and #$00FF
        jsr FindInv
        bcs @ret
        pha                     ; lo
        ldx #$0000              ; X = rec*37+slot, Y = n
        ldy #EQBIT0
@rec:   lda #$0006
        pha                     ; slot counter (1,s); lo = 3,s
@slot:  lda f:EQP0,x
        and #$00FF
        cmp 3,s
        bne @sn
        tya
        jsr TstN
        beq @sn
        pla
        pla
        sec
        bra @ret
@sn:    inx
        iny
        lda 1,s
        dec a
        sta 1,s
        bne @slot
        pla
        txa
        clc
        adc #37-6
        tax
        cpx #37*16
        bne @rec
        pla
@no:    clc
@ret:   ply
        plx
        pla
        jsr RetC
        plp
        rtl
        .a16
        .i16

; XEvSwitch: Y = event switch number, C = value -> set/clear event bit $1E80+(sw>>3)
XEvSwitch:
        php
        rep #$30
        pha
        phx
        php                     ; keep C
        tya
        lsr a
        lsr a
        lsr a
        tax
        tya
        and #$0007
        asl a
        phx
        tax
        lda f:XMaskW,x          ; A = mask
        plx
        plp
        sep #$20
        .a8
        bcs @set
        eor #$FF
        and f:EVBITS,x
        bra @st
@set:   ora f:EVBITS,x
@st:    sta f:EVBITS,x
        rep #$20
        .a16
        plx
        pla
        plp
        rtl
        .a16
        .i16

; ===========================================================================
; Arrange (item menu): replaces C3:267F JSR _c326b8 / JSR SortItemsByIcon. Same algorithm and the same
; temporary buffers as vanilla (7E:AA8D ids, 7E:AB8D quantities), with the high bit carried in bit 7 of
; the temporary quantity (quantities are <= 99). Order: ItemIconTbl C3:26F5 (17 icons), then inventory order.
; ===========================================================================
ItemIconTbl = $C326F5
XArrange:
        php
        rep #$30
        pha
        phx
        phy
        phb
        pea $7E7E
        plb
        plb
        ldx #$0000
@c:     sep #$20
        .a8
        lda $1869,x
        sta $AA8D,x
        lda #$FF
        sta $1869,x
        lda $1969,x
        sta $AB8D,x
        stz $1969,x
        rep #$20
        .a16
        txa
        jsr TstN
        beq @n
        sep #$20
        .a8
        lda $AB8D,x
        ora #$80
        sta $AB8D,x
        rep #$20
        .a16
@n:     inx
        cpx #$0100
        bne @c
        ldx #$0000
        lda #$0000
@z:     sta $1CF8,x
        inx
        inx
        cpx #$0020
        bne @z
        ldy #$0000
        ldx #$0000
@k:     phx
        lda f:ItemIconTbl,x
        and #$00FF
        pha                     ; target icon (1,s), icon index (3,s)
        ldx #$0000
@s:     lda $AA8D,x
        and #$00FF
        cmp #$00FF
        beq @nx
        jsr IconOf
        cmp 1,s
        bne @nx
        sep #$20
        .a8
        lda $AA8D,x
        sta $1869,y
        lda $AB8D,x
        and #$7F
        sta $1969,y
        lda $AB8D,x
        bpl @v
        rep #$20
        .a16
        tya
        jsr SetN
@v:     rep #$20
        .a16
        iny
@nx:    inx
        cpx #$0100
        bne @s
        pla
        plx
        inx
        cpx #17
        bne @k
        plb
        ply
        plx
        pla
        plp
        rtl
        .a16
        .i16

; IconOf (DB=$7E): X = buffer slot -> A = icon byte of $100*hi + id (XItemName byte 0). X,Y kept
IconOf:
        phx
        lda $AB8D,x
        and #$0080
        asl a
        pha
        lda $AA8D,x
        and #$00FF
        ora 1,s
        sta 1,s
        asl a
        asl a
        pha
        asl a
        clc
        adc 1,s
        adc 3,s
        tax
        pla
        pla
        lda f:XItemName,x
        and #$00FF
        plx
        rts

XMaskW: .word $01,$02,$04,$08,$10,$20,$40,$80
