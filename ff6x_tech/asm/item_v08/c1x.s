; =============================================================================
; TECH v0.7.1 - battle far routines (bank FA): battle-end inventory reconciliation and the bank C1
; (btlgfx, no usable free space) hooks. C1 hooks are JSL sites; every routine preserves the registers the
; displaced vanilla instructions did not change.
; =============================================================================

XBTLNAME_L      = $7E1E3E
W62CA           = $7E62CA           ; current battle menu character (0-3)
W7B00           = $7E7B00           ; battle item menu: 1 = left hand selected, else right hand
W7B39           = $7E7B39           ; swap check: inventory item id
W7B3B           = $7E7B3B           ; swap check: hand item id
CHARPTR_L       = $7E3010
LHANDLIST_L     = $7E2B9A           ; wLHandItemList::ItemID
RHANDLIST_L     = $7E2B86
LISTTXT_L       = $7E5760           ; w7e5755 + 11
DENY_SEC_RTS    = $C18A07           ; "sec / rts" inside check_equip (_c189d5)

.section XFA_CODE $FA8000
        .a16
        .i16

; ===========================================================================
; battle end (replaces C2:4981-C2:499D, the copy of the battle inventory back to $1869/$1969)
; pass 1: vanilla slots are copied exactly as vanilla did; extended slots keep their saved contents
; pass 2: a vanilla item the battle placed at an extended slot's position (obtained / moved / unequipped
;         in battle) is merged into the inventory (same id, cap 99) or the first free vanilla slot.
; ===========================================================================
XBattleEndInv:
        php
        rep #$30
        pha
        phx
        phy
        phb
        pea $7E7E
        plb
        plb
        ldx #$00FF
        ldy #$04FB
@p1:    txa
        jsr TstN
        bne @x1
        sep #$20
        .a8
        lda $2686,y
        sta $1869,x
        inc a
        beq @e1
        lda $2689,y
@e1:    sta $1969,x
        rep #$20
        .a16
@x1:    tya
        sec
        sbc #$0005
        tay
        dex
        bpl @p1
        ldx #$0000
        ldy #$0000
@p2:    txa
        jsr TstN
        beq @n2
        sep #$20
        .a8
        lda $2686,y
        cmp #$FF
        beq @n2a
        jsr PutVanilla
@n2a:   rep #$20
        .a16
@n2:    tya
        clc
        adc #$0005
        tay
        inx
        cpx #$0100
        bne @p2
        plb
        ply
        plx
        pla
        plp
        rtl

; PutVanilla (DB=$7E, M8/X16): A = vanilla id, Y = battle list entry (quantity at $2689,Y)
        .a8
        .i16
PutVanilla:
        phx
        pha
        ldx #$0000
@f:     lda $1869,x
        cmp 1,s
        bne @fn
        rep #$20
        .a16
        txa
        jsr TstN
        sep #$20
        .a8
        bne @fn
        lda $1969,x
        clc
        adc $2689,y
        cmp #100
        bcc @ok
        lda #99
@ok:    sta $1969,x
        bra @done
@fn:    inx
        cpx #$0100
        bne @f
        ldx #$0000
@g:     lda $1869,x
        cmp #$FF
        bne @gn
        rep #$20
        .a16
        txa
        jsr TstN
        sep #$20
        .a8
        bne @gn
        lda 1,s
        sta $1869,x
        lda $2689,y
        sta $1969,x
        bra @done
@gn:    inx
        cpx #$0100
        bne @g
@done:  pla
        plx
        rts
        .a16

; ===========================================================================
; C1 hooks
; ===========================================================================
; CharHandN: A16 = hand (0 = R / weapon slot, 1 = L / shield slot) of the current battle menu character
; -> A16 = 0/1 (equipment high bit), Z set from A. X,Y kept.
CharHandN:
        phx
        pha
        lda f:W62CA
        and #$0003
        asl a
        tax
        lda f:CHARPTR_L,x
        clc
        adc 1,s
        jsl XJ_EqpN
        jsl XJ_BitTst
        sta 1,s
        pla
        plx
        cmp #$0000              ; PLX changed Z: callers branch on the bit
        rts

; C1:4BDA hand header of the battle Item menu: replaces LDA wLHandItemList::ItemID,Y / STA w7e5755+11.
; Builds the name queue XBTLNAME (one bit per non-empty hand, R then L, 1 = extended name) consumed by
; ListTextCmd_0e (XC1_NameIdx).
XC1_HandNames:
        php
        rep #$30
        pha
        phx
        sep #$20
        .a8
        tyx
        lda f:LHANDLIST_L,x
        sta f:LISTTXT_L
        rep #$20
        .a16
        lda #$0000
        pha                     ; queue (1,s), next bit (3,s)
        lda #$0001
        pha
        lda f:RHANDLIST_L,x
        and #$00FF
        cmp #$00FF
        beq @l
        lda #$0000
        jsr CharHandN
        beq @r0
        lda 1,s
        ora 3,s
        sta 3,s
@r0:    lda 1,s
        asl a
        sta 1,s
@l:     lda f:LHANDLIST_L,x
        and #$00FF
        cmp #$00FF
        beq @w
        lda #$0001
        jsr CharHandN
        beq @w
        lda 1,s
        ora 3,s
        sta 3,s
@w:     pla
        pla
        sep #$20
        .a8
        sta f:XBTLNAME_L
        rep #$20
        .a16
        plx
        pla
        plp
        rtl

; C1:656C ListTextCmd_0e: replaces LDX $30 / LDA $56 ($30 = id*13). Consumes one queue bit; an extended
; hand name is read at XItemName + ($100 + id) * 13.
XC1_NameIdx:
        php
        sep #$20
        .a8
        lda f:XBTLNAME_L
        lsr a
        sta f:XBTLNAME_L
        bcs @ext
        plp
        ldx $30
        lda $56
        rtl
@ext:   rep #$20
        .a16
        lda $30
        clc
        adc #$0D00
        tax
        plp
        .a8
        lda $56
        rtl
        .a16

; C1:89D2 check_equip (_c189d5): replaces LDA w7e7b39 / CMP #$FF. check_equip validates the new item against the
; OTHER hand (w7e7b3b); the hand that is REPLACED is identified by the caller (JSR return address):
;   C1:8A81 set_item_one (hand selected first)   -> hand = w7e7b00 - 1 (1 = R-hand, 2 = L-hand)
;   C1:8FB2 hand_r2item  (item selected first)   -> R-hand
;   C1:9079 hand_l2item  (item selected first)   -> L-hand
; If the replaced hand holds an extended item the change is refused exactly like a vanilla refusal (SEC / RTS at
; C1:8A07): it would be written back to $161F/$1620 with its low byte only. Unknown caller: refuse if either hand
; is extended.
RET_SETITEM     = $8A83
RET_R2ITEM      = $8FB4
RET_L2ITEM      = $907B
        .a8
XC1_SwapGuard:
        php
        rep #$30
        .a16
        pha
        lda 7,s                 ; JSR return address of the check_equip call (1,s A; 3,s P; 4-6,s JSL return)
        cmp #RET_SETITEM
        beq @sel
        cmp #RET_R2ITEM
        beq @r
        cmp #RET_L2ITEM
        beq @lh
        lda #$0000              ; unknown caller: R-hand first, then L-hand
        jsr CharHandN
        bne @deny
@lh:    lda #$0001
        bra @t
@sel:   lda f:W7B00
        dec a
        and #$0001
        bra @t
@r:     lda #$0000
@t:     jsr CharHandN
        bne @deny
        pla
        plp
        .a8
        lda f:W7B39
        cmp #$FF
        rtl
        .a16
@deny:  pla
        plp
        .a8
        pla
        pla
        pla
        jml DENY_SEC_RTS
        .a16

; C1:8E8F SelectEquipItem, R-hand <-> L-hand exchange (both hand entries already swapped): replaces
; LDX w7e7b05 / TDC. Swaps the character's two hand equipment bits so the battle write-back (C2:20AB, low bytes
; to $161F/$1620) and the hand names stay consistent; then does the displaced LDX / TDC (DB = $7E).
XC1_HandSwapBits:
        php
        rep #$30
        pha
        phx
        phy
        lda f:W62CA
        and #$0003
        asl a
        tax
        lda f:CHARPTR_L,x
        jsl XJ_EqpN             ; A = bit number of the R-hand slot
        tax
        jsl XJ_BitTst
        tay                     ; Y = R bit
        txa
        inc a
        jsl XJ_BitTst           ; A = L bit (XBitTst returns the caller's flags)
        cmp #$0000
        beq @r0
        txa
        jsl XJ_BitSet           ; R := old L
        bra @l
@r0:    txa
        jsl XJ_BitClr
@l:     txa
        inc a
        cpy #$0000
        beq @l0
        jsl XJ_BitSet           ; L := old R
        bra @d
@l0:    jsl XJ_BitClr
@d:     ply
        plx
        pla
        plp
        ldx $7B05
        tdc
        rtl
        .a16

; C1:BA47 / C1:BA41 Jump animation (Jump command, character attacker): replace LDA w[R|L]HandItemList::ItemID,X
; / INC (X = CharEquipPtrs[char] = char*5). Returns the ItemJumpThrowAnim index in A low byte (B and every other
; register preserved, flags restored): vanilla = id + 1 (8-bit), extended weapon = $80 + low byte (XJumpAnim).
        .a16
        .i16
XC1_JumpAnimR:
        php
        rep #$30
        pha
        phx
        pea $0000
        bra JumpAnimN
XC1_JumpAnimL:
        php
        rep #$30
        pha
        phx
        pea $0001
; stack: 1,s hand  3,s X  5,s A  7,s P
JumpAnimN:
        lda 3,s
        and #$00FF
        ldx #$0000
@d:     cmp #$0005
        bcc @c
        sbc #$0005
        inx
        inx
        bra @d
@c:     lda f:CHARPTR_L,x
        clc
        adc 1,s
        jsl XJ_EqpN
        jsl XJ_BitTst
        tay                     ; Y = 0/1 (extended)
        lda 3,s
        and #$00FF
        tax
        lda 1,s
        beq @r
        lda f:LHANDLIST_L,x
        bra @g
@r:     lda f:RHANDLIST_L,x
@g:     and #$00FF
        cpy #$0000
        bne @x
        inc a                   ; vanilla: id + 1, 8-bit wrap
        bra @w
@x:     clc
        adc #$0080              ; extended: $80 + low byte
@w:     sep #$20
        .a8
        sta 5,s                 ; low byte of the caller's A
        rep #$20
        .a16
        pla
        plx
        pla
        plp
        rtl
        .a16
