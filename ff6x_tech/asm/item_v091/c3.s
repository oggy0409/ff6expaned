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
XCURCMD_C3      = $7E1E36           ; TECH v0.9 transient bytes (core.s XTRANS)
XSHOPCURHI      = $7E1E3C
XRAREPAGE_C3    = $7E1E3D
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

; GetItemPropPtr with the high byte taken from B (vanilla writes 0): M7A = B:A, M7B = 30.
; TECH v0.8: returns with B = 0 like the vanilla path (where B is 0 after TDC/CLR_A): the id high bit must not
; leak into a later 16-bit TAX/TAY (SortValidEquip C3:A16C used it as the next slot index). A = 30, N/Z as vanilla.
XC3_PropPtrB:
        pha
@w:     lda hHVBJOY
        and #$40
        beq @w
        pla
        sta hM7A
        xba
        sta hM7A
        lda #$00
        xba
        lda #30
        sta hM7B
        sta hM7B
        rts

; replaces STZ $211B (high byte of a M7A multiplicand) with B; returns B = 0 (v0.8), A and N/Z unchanged
XC3_HiM7A:
        xba
        sta hM7A
        lda #$00
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
; XC3_ExclLo: A = low byte of an EXTENDED item -> C=1 if it is hidden in the current menu: always in the colosseum
; (no wager), in a shop unless it is a sellable extended consumable (TECH v0.9). A kept.
XC3_ExclLo:
        pha
        lda r0200
        cmp #MENU_TYPE_COLO
        beq @y
        cmp #MENU_TYPE_SHOP
        bne @n
        lda 1,s
        jsr XC3_SellableLo
        bcc @y
@n:     pla
        clc
        rts
@y:     pla
        sec
        rts

; XC3_SellableLo: A = low byte -> C=1 if $100|lo is a defined, sellable extended consumable (XExtFlags bits 0,2,3).
; A, X, Y kept.
XC3_SellableLo:
        php
        rep #$30
        .a16
        pha
        phx
        and #$00FF
        cmp #$0040
        bcs @no
        tax
        lda f:XExtFlags,x
        and #$000D
        cmp #$000D
        bra @r
@no:    clc
@r:     plx
        pla
        jmp XC3_RetC
        .a8

; LoadListItemName body (C3:80C7, WRAM address + hblank already set, Y = inventory slot):
; 13-byte name + ':' + 0, or 16 blanks + 0. Extended items use XItemName; in a shop / the colosseum an
; extended slot is drawn exactly like an empty slot (cannot be sold / wagered, never truncated).
XC3_ListNameY:
        jsr XC3_IsExtY
        bcc @van
        lda INV,y
        jsr XC3_ExclLo
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
        lda INV,y
        jsr XC3_ExclLo
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
        jsr XC3_ExclLo
        bcc XC3_DescExt
        lda #$FF
        jmp LoadItemDesc

; XC3_DescExt: A = low byte of an extended item, B = 0: its description (XDescPtr, absolute pointers in bank FA)
XC3_DescExt:
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
        jmp XC3_ClrB

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
        jmp XC3_ClrB

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
        jmp XC3_ClrB
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
        jmp XC3_ClrB

; TECH v0.8: B := 0 at the end of an id chain (vanilla has B = 0 there); A low byte and all flags preserved
XC3_ClrB:
        php
        xba
        lda #$00
        xba
        plp
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
        lda f:XSHOPCURHI
        bne @e                  ; TECH v0.9: the current shop item is an extended consumable (never equipped)
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

; ===========================================================================
; TECH v0.9: field use of extended consumables (Item menu)
; ===========================================================================
GetInvItemID    = $C38C2B           ; A = id low byte of the selected slot (zSelIndex), X = slot, B = 0
CheckMaxHP      = $C32B9A           ; Y = character -> C=0 if HP < max (clamps)
CheckMaxMP      = $C32BBC
hMPYL_C3        = $2134

; C3:8B25 (_c38b1a, before JSL CalcMagicEffect): replaces JSR GetInventoryItemID. XCURCMD := $FE when the selected
; slot holds an extended item (C2 XC2_PropCtx then reads the extended record), else 0.
XC3_GetIdCtx:
        jsr GetInvItemID
        pha
        jsr XC3_IsExtX
        lda #$00
        bcc @w
        lda #$FE
@w:     sta f:XCURCMD_C3
        pla
        rts

; C3:8C34 (_c38c33 HP / MP restore): replaces JSR GetInventoryItemID: A = low byte, B = high bit, X = slot
XC3_GetIdB:
        jsr GetInvItemID
        jmp XC3_LdaInvX

; C3:8B17 (_c38b11 tail): replaces JMP DecItemQty: one unit of the selected slot's item (9-bit id)
XC3_DecSel:
        jsr GetInvItemID
        jsr XC3_LdaInvX
        jmp XC3_DecQtyB

; C3:8B3D CheckCanUseItem: replaces LDA $0014,Y (Y = character data). Extended item in the selected slot: validity
; from its ItemProp record (vanilla rules: revive only a fallen character; cure if the character has a status the
; item removes; HP / MP restore if below max and not wounded / petrified / zombie), returned to the caller of
; CheckCanUseItem (C=1 can use).
XC3_CanUse:
        jsr GetInvItemID
        jsr XC3_IsExtX
        bcs @ext
        lda $0014,y
        rts
@ext:   pla
        pla                     ; return straight to CheckCanUseItem's caller
        lda INV,x
        xba
        lda #$01
        xba
        jsr XC3_PropPtrB
        ldx hMPYL_C3            ; X = id9 * 30
        lda $0014,y
        bpl @alive
        lda f:XItemProp+19,x    ; fallen: only an item that removes Wound
        and #$20
        beq @no
        lda f:XItemProp+21,x
        bmi @yes
@no:    clc
        rts
@yes:   sec
        rts
@alive: lda f:XItemProp+19,x
        and #$20
        beq @hp
        lda f:XItemProp+21,x
        bmi @no                 ; revive item on a living character
        and $0014,y
        bne @yes
        lda f:XItemProp+24,x
        and $0015,y
        bne @yes
@hp:    lda $0014,y
        and #$C2                ; Wound / Petrify / Zombie: no HP / MP restore (vanilla rule)
        bne @no
        lda f:XItemProp+19,x
        and #$08
        beq @mp
        phx
        jsr CheckMaxHP
        plx
        bcc @yes
@mp:    lda f:XItemProp+19,x
        and #$10
        beq @no
        jsr CheckMaxMP
        bcc @yes
        bra @no

; ===========================================================================
; TECH v0.9: extended shops (XShopProp / XShopPropHi) and Sell of sellable extended consumables
; ===========================================================================
ShopCurItem     = $C3BFC2           ; _c3bfc2: A = item low byte of the current buy entry (z4b)
LoadItemName    = $C3C068
ShopBuyTail     = $C3B5EA           ; buy: total price / GP / sound (after the item is added)
InitRareItemList = $C3838B
UpdateRareCursor = $C37D4A
InitRareCursor  = $C37D4D
BigTextTask     = $C3A80E
TASK_CODEPTR    = $7E3249           ; wTaskProp::CodePtr (64 x 2)
TASK_STATE      = $7E3649           ; wTaskProp::State (same task offset as CodePtr, ExecTasks C3:11B0)

; XC3_ShopHiX: X = shop entry (0-7) -> A = 1 if that entry is an extended item (XShopPropHi[shop*9 + 1 + X]), B = 0
XC3_ShopHiX:
        php
        rep #$30
        .a16
        phx
        txa
        clc
        adc $67                 ; zSelCharPropPtr = shop * 9
        inc a
        tax
        lda f:XShopPropHi,x
        and #$00FF
        plx
        plp
        .a8
        rts

; C3:BFC6 (_c3bfc2) / C3:BCE1 / C3:C1B0: replaces LDA $7E9D89,X (X = entry): XSHOPCURHI := entry high bit;
; A = low byte, B = 0
XC3_ShopLdaX:
        jsr XC3_ShopHiX
        sta f:XSHOPCURHI
        lda f:$7E9D89,x
        rts

; C3:BFCF (_c3bfcb, Sell: Y = slot) / C3:B4FF (sell description, X = slot): replace LDA $1869,Y / X.
; XSHOPCURHI := slot high bit; an extended slot reads as $FF (cannot be sold) unless it is a sellable consumable.
XC3_SellLdaY:
        phx
        tyx
        jsr XC3_SellLdaX
        plx
        and #$FF                ; N / Z from the returned id, C kept (as LDA)
        rts

XC3_SellLdaX:
        php
        jsr XC3_IsExtX
        lda #$00
        rol a
        sta f:XSHOPCURHI
        beq @v
        lda INV,x
        jsr XC3_SellableLo
        bcs @v
        lda #$00
        sta f:XSHOPCURHI
        plp
        .a8
        .i16
        lda #$FF
        rts
@v:     plp
        .a8
        .i16
        lda INV,x
        rts

; C3:B4F5 / C3:B502 (buy / sell description): replaces JMP LoadItemDesc (A = low byte of the current item)
XC3_ItemDescCur:
        pha
        lda f:XSHOPCURHI
        beq @v
        pla
        jmp XC3_DescExt
@v:     pla
        jmp LoadItemDesc

; C3:B9BD (shop list row, entry zf1): replaces JSR LoadItemName (A = low byte)
XC3_ShopListName:
        pha
        phx
        ldx $F1
        jsr XC3_ShopHiX
        sta f:XSHOPCURHI
        plx
        pla
        jmp XC3_LoadItemNameCur

; C3:B9C9 (shop list row price, entry zf1): replaces JSR GetItemPropPtr (A = low byte)
XC3_ShopListPtr:
        pha
        phx
        ldx $F1
        jsr XC3_ShopHiX
        xba
        plx
        pla
        jmp XC3_PropPtrB

; C3:BD13 (per-entry stats, X = entry): replaces JSR GetItemPropPtr
XC3_ShopPtrX:
        pha
        jsr XC3_ShopHiX
        xba
        pla
        jmp XC3_PropPtrB

; C3:B7E9 / BAF8 / BB68 / BCE5 / C1B4: replaces JSR GetItemPropPtr for the current shop item (XSHOPCURHI)
XC3_PropPtrCur:
        pha
        lda f:XSHOPCURHI
        xba
        pla
        jmp XC3_PropPtrB

; C3:BAC6 / BADF (and XC3_ShopListName): LoadItemName (C3:C068) for the current shop item: 13-byte name of
; $100*XSHOPCURHI + A at 7E:9E8B, 0-terminated. Returns B = 0.
XC3_LoadItemNameCur:
        pha
        ldx #$9E8B
        stx hWMADDL
        lda f:XSHOPCURHI
        xba
        pla
        rep #$20
        .a16
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
        jmp XC3_ClrB

; C3:B5B7 (buy confirmed, zSelIndex = quantity): replaces JSR _c3bfc2. Extended entry: the quantity is given with
; the extended give (stack / first free slot), then the vanilla tail (price, GP, sound) runs. If the item has no
; stack and the inventory is full nothing is bought and no GP is taken.
XC3_ShopBuy:
        jsr ShopCurItem
        pha
        lda f:XSHOPCURHI
        bne @ext
        pla
        rts
@ext:   pla
        php
        rep #$30
        .a16
        and #$00FF
        ora #$0100
        pha                     ; id (1,s)
        lda $28                 ; zSelIndex = quantity
        and #$00FF
        tax
        beq @done
        lda 1,s
        jsl XJ_GiveExt
        bcc @full
@more:  dex
        beq @done
        lda 1,s
        jsl XJ_GiveExt
        bra @more
@done:  pla
        plp
        .a8
        pla
        pla                     ; drop the return address (C3:B5BA, vanilla search)
        jmp ShopBuyTail
        .a16
@full:  pla
        plp
        .a8
        pla
        pla
        rts                     ; return from _c3b5b7: nothing bought

; ===========================================================================
; TECH v0.9: Rare Items menu (52 logical rare ids, 20 per page)
; ===========================================================================
; C3:838E (InitRareItemList): replaces JSR GetRareItemList
XC3_RareListS:
        jsl XJ_RareList
        rts

; C3:834C (InitRareItemDesc): replaces JSR CountRareItems: z64 = number of owned rare items (all pages)
XC3_RareCount:
        jsl XJ_RareCount
        sta $64
        rts

; C3:26A0 (open the Rare Items list): replaces JSR InitRareItemList: page 0
XC3_RareInit:
        lda #$00
        sta f:XRAREPAGE_C3
        jmp InitRareItemList

; C3:2748 (menu state ITEM_RARE): replaces JSR UpdateRareItemCursor. Down on the last row / Up on the first row
; turn the page (the cursor wraps to the first / last row of the new page); R / L = next / previous page.
XC3_RarePage:
        lda $0B                 ; zRepCtrlState_H
        bit #$04                ; down
        beq @up
        lda $4E
        cmp #9
        bne @mv
        jsl XJ_RareNext
        bcc @mv
        jsr UpdateRareCursor
        lda f:XRAREPAGE_C3
        inc a
        bra @set
@up:    bit #$08                ; up
        beq @lr
        lda $4E
        bne @mv
        lda f:XRAREPAGE_C3
        beq @mv
        jsr UpdateRareCursor
        lda f:XRAREPAGE_C3
        dec a
        bra @set
@lr:    lda $08                 ; zNewCtrlState_L
        bit #$10                ; R
        beq @l
        jsl XJ_RareNext
        bcc @mv
        lda f:XRAREPAGE_C3
        inc a
        bra @set2
@l:     bit #$20                ; L
        beq @mv
        lda f:XRAREPAGE_C3
        beq @mv
        dec a
        bra @set2
@mv:    jmp UpdateRareCursor
@set:   sta f:XRAREPAGE_C3
        jsr XC3_BigTextReset
        jmp InitRareItemList
@set2:  sta f:XRAREPAGE_C3
        jsr XC3_BigTextReset
        jsr InitRareItemList
        jmp InitRareCursor

; XC3_BigTextReset: the description task (BigTextTask) restarts from its state 0 (clear + redraw), as it does when a
; direction button is held; L / R page flips change the item under an unmoved cursor. A, X destroyed.
XC3_BigTextReset:
        php
        rep #$30
        .a16
        ldx #$0000
@f:     lda f:TASK_CODEPTR,x
        cmp #BigTextTask & $FFFF
        beq @hit
        inx
        inx
        cpx #$0080
        bne @f
        plp
        .a8
        rts
        .a16
@hit:   sep #$20
        .a8
        lda #$00
        sta f:TASK_STATE,x
        plp
        .a8
        rts
