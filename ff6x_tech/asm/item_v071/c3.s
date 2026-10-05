; =============================================================================
; TECH v0.7.1 - bank C3 (menu) stubs (vanilla free space C3:F091-C3:FFFF, claim ITEMX_C3_STUBS)
; Menu context: .a8 .i16, DB=$00 or $7E (both map $0000-$1FFF to WRAM), D=$0000.
;
; Convention "ID16 in A": B (high byte of A) = extended high bit (0 vanilla / 1 extended), A low = id low.
; Loaders below set it; consumers below read it. Vanilla routines are never fed a B they did not expect:
; GetItemPropPtr / IncItemQty / DecItemQty keep their vanilla behaviour (high byte 0); ext-aware callers are
; redirected to the *B variants.
; =============================================================================

LoadSaveSlot    = $C31566
PopTimers       = $C31595
LoadItemDesc    = $C35738
IncItemQty      = $C39D5E
DecItemQty      = $C39D97
DrawItemList    = $C37F88
GetSelCharPropPtr = $C393F2
ImpItem         = $ED82E4
IMP_ITEM_COUNT  = 10
MENU_TYPE_SHOP  = 3
MENU_TYPE_COLO  = 7
COLON_CHAR      = $C1
XSCRATCH        = $7E1E3F           ; audited free saved byte, transient (SAVED_RAM_AUDIT_v0.7.1.md)
hM7A            = $211B
hM7B            = $211C
hMPYL           = $2134
hWMDATA         = $2180
hWMADDL         = $2181
hHVBJOY         = $4212
r0200           = $0200
INV             = $1869
QTY             = $1969

.section XC3 $C3F0A0
        .a8
        .i16

; ===========================================================================
; save compatibility
; ===========================================================================
; LoadSavedGame (C3:14FE, game-over restart path): replaces JSR PopTimers after the checksum passed
XC3_LoadOK:
        jsl XJ_Sanitize
        jmp PopTimers

; load menu (C3:29EB, title Continue): replaces JSR LoadSaveSlot; the slot checksum was validated when the
; menu was drawn and a cancelled load restores RAM with PopSRAM, so sanitising here is safe.
XC3_LoadSlotSan:
        jsr LoadSaveSlot
        jsl XJ_Sanitize
        rts

; ===========================================================================
; primitives
; ===========================================================================
; XC3_RetC: common tail for routines that did PHP / REP #$30: copy C into the PHP byte, PLP, RTS.
        .a16
        .i16
XC3_RetC:
        pha
        sep #$20
        .a8
        bcs @s
        lda 3,s
        and #$FE
        bra @w
@s:     lda 3,s
        ora #$01
@w:     sta 3,s
        rep #$20
        .a16
        pla
        plp
        rts
        .a8
        .i16

; XC3_IsExtY / XC3_IsExtX: C=1 if inventory slot Y / X holds an extended item. A(16), X, Y preserved.
XC3_IsExtY:
        php
        rep #$30
        .a16
        pha
        tya
        and #$00FF
        jsl XJ_BitTst
        lsr a
        pla
        jmp XC3_RetC
        .a8

XC3_IsExtX:
        php
        rep #$30
        .a16
        pha
        txa
        and #$00FF
        jsl XJ_BitTst
        lsr a
        pla
        jmp XC3_RetC
        .a8

; XC3_LdaInvY / X: replaces LDA $1869,Y / X (M8): A = low byte, B = high bit. N/Z from the low byte, C kept.
XC3_LdaInvY:
        php
        jsr XC3_IsExtY
        lda #$00
        rol a
        xba
        plp
        .a8
        .i16
        lda INV,y
        rts

XC3_LdaInvX:
        php
        jsr XC3_IsExtX
        lda #$00
        rol a
        xba
        plp
        .a8
        .i16
        lda INV,x
        rts

; masked loads: an extended slot reads as $FF (used where an extended item must not be selectable / matched)
XC3_LdaInvYMask:
        jsr XC3_IsExtY
        bcs @e
        lda INV,y
        rts
@e:     lda #$FF
        rts

XC3_LdaInvXMask:
        jsr XC3_IsExtX
        bcs @e
        lda INV,x
        rts
@e:     lda #$FF
        rts

; replaces CMP $1869,Y in vanilla "find the same item" searches: an extended slot never compares equal
; (Z=0 for any A, including $FF: vanilla IncItemQty/DecItemQty are also called with A=$FF for an empty
; equipment slot and would otherwise match it). Callers only test Z.
XC3_CmpInvYMask:
        jsr XC3_IsExtY
        bcs @e
        cmp INV,y
        rts
@e:     rep #$02
        rts

; replaces STA $1869,Y where vanilla code puts a vanilla id into a free slot: high bit cleared
XC3_StaInvYClr:
        sta INV,y
        php
        rep #$30
        .a16
        pha
        tya
        and #$00FF
        jsl XJ_BitClr
        pla
        plp
        .a8
        .i16
        rts

; GetItemPropPtr with the high byte taken from B (vanilla writes 0): M7A = B:A, M7B = 30
XC3_PropPtrB:
        pha
@w:     lda hHVBJOY
        and #$40
        beq @w
        pla
        sta hM7A
        xba
        sta hM7A
        xba
        lda #30
        sta hM7B
        sta hM7B
        rts

; replaces STZ $211B (high byte of a M7A multiplicand) with B
XC3_HiM7A:
        xba
        sta hM7A
        xba
        rts

; XC3_Mul13: A16 = n -> X = n*13 (A destroyed; called with A16/X16)
        .a16
XC3_Mul13:
        pha
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
        rts
        .a8

; ===========================================================================
; item list / names / descriptions
; ===========================================================================
; XC3_Excluded: C=1 if the current menu is a shop or the colosseum (extended items hidden there). A kept
XC3_Excluded:
        pha
        lda r0200
        cmp #MENU_TYPE_SHOP
        beq @y
        cmp #MENU_TYPE_COLO
        beq @y
        pla
        clc
        rts
@y:     pla
        sec
        rts

; LoadListItemName body (C3:80C7, WRAM address + hblank already set, Y = inventory slot):
; 13-byte name + ':' + 0, or 16 blanks + 0. Extended items use XItemName; in a shop / the colosseum an
; extended slot is drawn exactly like an empty slot (cannot be sold / wagered, never truncated).
XC3_ListNameY:
        jsr XC3_IsExtY
        bcc @van
        jsr XC3_Excluded
        bcs @blank
        rep #$20
        .a16
        lda INV,y
        and #$00FF
        ora #$0100
        bra @idx
        .a8
@van:   lda INV,y
        cmp #$FF
        beq @blank
        rep #$20
        .a16
        and #$00FF
@idx:   jsr XC3_Mul13
        sep #$20
        .a8
        ldy #13
@l:     lda f:XItemName,x
        sta hWMDATA
        inx
        dey
        bne @l
        lda #COLON_CHAR
        sta hWMDATA
        stz hWMDATA
        rts
@blank: ldy #16
        lda #$FF
@b:     sta hWMDATA
        dey
        bne @b
        stz hWMDATA
        rts

; quantity column of the item list (C3:7FA8): an extended slot shows 0 in a shop / the colosseum
XC3_LdaQtyList:
        jsr XC3_IsExtY
        bcc @q
        jsr XC3_Excluded
        bcc @q
        lda #$00
        rts
@q:     lda QTY,y
        rts

; replaces JSR/JMP LoadItemDesc where A = low byte, B = high bit ([$E7] / [$EB] set by GetItemDescPtr)
XC3_ItemDescB:
        xba
        bne @ext
        xba
        jmp LoadItemDesc
@ext:   lda #$00
        xba                     ; A = low byte, B = 0
        jsr XC3_Excluded
        bcs @none
        phx
        ldx #XDescPtr & $FFFF
        stx $E7
        ldx #$0000
        stx $EB
        pha
        lda #^XDescPtr
        sta $E9
        sta $ED
        pla
        plx
        jmp LoadItemDesc
@none:  lda #$FF
        jmp LoadItemDesc

; ===========================================================================
; equipment slots  (Y = pointer to character data $1600+rec*37; operand $00XX,Y)
; ===========================================================================
; XC3_EqHiD: A16 = data offset relative to $161F (rec*37+slot) -> A16 = 0/1
        .a16
XC3_EqHiD:
        jsl XJ_EqpN
        jsl XJ_BitTst
        rts
        .a8

; XC3_LdaEqXX: replaces LDA $00XX,Y: A = low byte, B = high bit, N/Z from the low byte, C kept
XC3_LdaEq1E:
        php
        rep #$30
        .a16
        tya
        sec
        sbc #$1601
        jsr XC3_EqHiD
        plp
        .a8
        .i16
        xba
        lda $001E,y
        rts

XC3_LdaEq1F:
        php
        rep #$30
        .a16
        tya
        sec
        sbc #$1600
        jsr XC3_EqHiD
        plp
        .a8
        .i16
        xba
        lda $001F,y
        rts

XC3_LdaEq20:
        php
        rep #$30
        .a16
        tya
        sec
        sbc #$15FF
        jsr XC3_EqHiD
        plp
        .a8
        .i16
        xba
        lda $0020,y
        rts

XC3_LdaEq21:
        php
        rep #$30
        .a16
        tya
        sec
        sbc #$15FE
        jsr XC3_EqHiD
        plp
        .a8
        .i16
        xba
        lda $0021,y
        rts

XC3_LdaEq22:
        php
        rep #$30
        .a16
        tya
        sec
        sbc #$15FD
        jsr XC3_EqHiD
        plp
        .a8
        .i16
        xba
        lda $0022,y
        rts

XC3_LdaEq23:
        php
        rep #$30
        .a16
        tya
        sec
        sbc #$15FC
        jsr XC3_EqHiD
        plp
        .a8
        .i16
        xba
        lda $0023,y
        rts

XC3_LdaEq24:
        php
        rep #$30
        .a16
        tya
        sec
        sbc #$15FB
        jsr XC3_EqHiD
        plp
        .a8
        .i16
        xba
        lda $0024,y
        rts

; masked equipment loads (shop "already equipped" equality tests): extended -> $FF
XC3_LdaEqM1F:
        jsr XC3_LdaEq1F
        xba
        bne @e
        xba
        rts
@e:     lda #$00
        xba
        lda #$FF
        rts

XC3_LdaEqM20:
        jsr XC3_LdaEq20
        xba
        bne @e
        xba
        rts
@e:     lda #$00
        xba
        lda #$FF
        rts

; XC3_StaEqXX: replaces STA $00XX,Y: store A; equipment high bit := (A != $FF) and B
XC3_StaEq1F:
        sta $001F,y
        php
        rep #$30
        .a16
        pha
        phx
        tya
        sec
        sbc #$1600
        jsr XC3_EqPutBit
        plx
        pla
        plp
        .a8
        .i16
        rts

XC3_StaEq20:
        sta $0020,y
        php
        rep #$30
        .a16
        pha
        phx
        tya
        sec
        sbc #$15FF
        jsr XC3_EqPutBit
        plx
        pla
        plp
        .a8
        .i16
        rts

XC3_StaEq21:
        sta $0021,y
        php
        rep #$30
        .a16
        pha
        phx
        tya
        sec
        sbc #$15FE
        jsr XC3_EqPutBit
        plx
        pla
        plp
        .a8
        .i16
        rts

XC3_StaEq22:
        sta $0022,y
        php
        rep #$30
        .a16
        pha
        phx
        tya
        sec
        sbc #$15FD
        jsr XC3_EqPutBit
        plx
        pla
        plp
        .a8
        .i16
        rts

XC3_StaEq23:
        sta $0023,y
        php
        rep #$30
        .a16
        pha
        phx
        tya
        sec
        sbc #$15FC
        jsr XC3_EqPutBit
        plx
        pla
        plp
        .a8
        .i16
        rts

; XC3_EqPutBit: A16 = data offset; 7,s (after the PHA below) = caller A16 (B:lo)
        .a16
XC3_EqPutBit:
        jsl XJ_EqpN
        pha
        lda 7,s
        and #$00FF
        cmp #$00FF
        beq @clr
        lda 7,s
        and #$0100
        beq @clr
        pla
        jsl XJ_BitSet
        rts
@clr:   pla
        jsl XJ_BitClr
        rts
        .a8

; ===========================================================================
; inventory quantity with the high bit
; ===========================================================================
XC3_IncQtyB:
        xba
        bne @ext
        xba
        jmp IncItemQty
@ext:   xba
        php
        rep #$30
        .a16
        pha
        jsl XJ_GiveExt
        pla
        plp
        .a8
        .i16
        rts

XC3_DecQtyB:
        xba
        bne @ext
        xba
        jmp DecItemQty
@ext:   xba
        php
        rep #$30
        .a16
        pha
        jsl XJ_TakeExt
        pla
        plp
        .a8
        .i16
        rts

; ===========================================================================
; equip menu
; ===========================================================================
; EquipRemoveAll (C3:96A8) replacement: weapon, shield, helmet, armor back to the inventory with full ids
XC3_RemoveAll:
        jsr GetSelCharPropPtr
        jsr XC3_LdaEq1F
        jsr XC3_IncQtyB
        jsr XC3_LdaEq20
        jsr XC3_IncQtyB
        jsr XC3_LdaEq21
        jsr XC3_IncQtyB
        jsr XC3_LdaEq22
        jsr XC3_IncQtyB
        lda #$00
        xba
        lda #$FF
        jsr XC3_StaEq1F
        jsr XC3_StaEq20
        jsr XC3_StaEq21
        jsr XC3_StaEq22
        rts

; GetBestEquip (C3:9819) replacement: first candidate of the sorted list that is not an imp item.
; Returns A = low byte, B = high bit; Y preserved (as vanilla). Extended items are never imp items.
XC3_GetBestEquip:
        phy
        ldy #$0000
@cand:  tyx
        lda f:$7E9D8A,x
        rep #$20
        .a16
        and #$00FF
        tax
        sep #$20
        .a8
        jsr XC3_IsExtX
        bcc @van
        lda f:$7E1869,x
        xba
        lda #$01
        xba
        ply
        rts
@van:   lda f:$7E1869,x
        ldx #$0000
@imp:   cmp f:ImpItem,x
        beq @isimp
        inx
        cpx #IMP_ITEM_COUNT
        bne @imp
        xba
        lda #$00
        xba
        ply
        rts
@isimp: iny
        bra @cand

; GetBest2Hand (C3:983F) replacement (same order as vanilla; extended candidates use their own properties)
XC3_GetBest2Hand:
        lda f:$7E9D89
        bne @go
        lda #$00
        xba
        lda #$FF
        rts
@go:    sta $CB
        stz $CC
        ldy #$0000
@cand:  tyx
        lda f:$7E9D8A,x
        rep #$20
        .a16
        and #$00FF
        tax
        sep #$20
        .a8
        jsr XC3_IsExtX
        bcs @ext
        lda f:$7E1869,x
        ldx #$0000
@imp:   cmp f:ImpItem,x
        beq @skip
        inx
        cpx #IMP_ITEM_COUNT
        bne @imp
        xba
        lda #$00
        xba
        bra @chk
@ext:   lda f:$7E1869,x
        xba
        lda #$01
        xba
@chk:   sta $C9
        jsr XC3_PropPtrB
        ldx hMPYL
        lda f:XItemProp+19,x
        and #$40
        beq @skip
        lda $C9
        rts
@skip:  iny
        cpy $CB
        bne @cand
        jmp XC3_GetBestEquip

; _c38fe1 replacement (equipped item name, no colon). A = low byte, B = high bit; $E0 != 0 -> draw even $FF
XC3_EqpName:
        rep #$20
        .a16
        pha
        sep #$20
        .a8
        ldx #$9E8B
        stx hWMADDL
@w:     lda hHVBJOY
        and #$40
        beq @w
        lda $E0
        bne @draw
        lda 1,s
        cmp #$FF
        beq @blank
@draw:  rep #$20
        .a16
        pla
        and #$01FF
        jsr XC3_Mul13
        sep #$20
        .a8
        ldy #13
@l:     lda f:XItemName,x
        sta hWMDATA
        inx
        dey
        bne @l
        stz hWMDATA
        rts
@blank: rep #$20
        .a16
        pla
        sep #$20
        .a8
        ldy #13
        lda #$FF
@b:     sta hWMDATA
        dey
        bne @b
        stz hWMDATA
        rts

; equip preview (_c39233): save / restore the slot's full id around the temporary candidate store
XC3_PrevSave:
        jsr XC3_LdaEq1F
        sta $64
        xba
        sta f:XSCRATCH
        xba
        rts

XC3_PrevRestore:
        lda f:XSCRATCH
        xba
        lda $64
        jmp XC3_StaEq1F

; ===========================================================================
; shop
; ===========================================================================
; replaces LDA [$E7],Y / CMP $E0 in the "how many equipped" count ($E7 = $161F + rec*37, Y = slot 0-5):
; an extended slot never equals the (vanilla) item in $E0
XC3_ShopEqCmp:
        php
        rep #$30
        .a16
        tya
        clc
        adc $E7
        sec
        sbc #$161F
        jsr XC3_EqHiD
        plp
        .a8
        .i16
        cmp #$00
        bne @e
        lda [$E7],y
        cmp $E0
        rts
@e:     lda #$FF
        rep #$02                ; never equal
        rts

; ===========================================================================
; item move (swap two slots) / arrange
; ===========================================================================
; replaces JMP DrawItemList at the end of the item swap (C3:27DE): X, Y = the two swapped slots
XC3_SwapBits:
        php
        rep #$30
        .a16
        txa
        and #$00FF
        jsl XJ_BitTst
        pha                     ; old bit(X)  -> 3,s after the next PHA
        tya
        and #$00FF
        jsl XJ_BitTst
        pha                     ; old bit(Y)  -> 1,s
        lda 1,s                 ; bit(X) := old bit(Y)
        beq @cx
        txa
        and #$00FF
        jsl XJ_BitSet
        bra @y
@cx:    txa
        and #$00FF
        jsl XJ_BitClr
@y:     lda 3,s                 ; bit(Y) := old bit(X)
        beq @cy
        tya
        and #$00FF
        jsl XJ_BitSet
        bra @done
@cy:    tya
        and #$00FF
        jsl XJ_BitClr
@done:  pla
        pla
        plp
        .a8
        .i16
        jmp DrawItemList
        .a8
