; =============================================================================
; TECH v0.7.1 - bank C2 (battle + shared UpdateEquip) stubs (vanilla free space C2:6469-C2:67FF,
; claim ITEMX_C2_STUBS). Battle context: DB=$7E, D=$0000.
; =============================================================================

CopyItemProp    = $C254CD
SpearEffect     = $C21512
ItemTypeMaskTbl = $C25549
XBTLNAME        = $7E1E3E
XBITS_C2        = $7E1CF8           ; extension bitmap (core.s XBITS)           ; audited free saved byte, transient (battle item-menu hand names)
RHandItem       = $3CA8             ; wTargetProp2::RHandItem (+1 = LHandItem)
CharPtr         = $3010             ; w7e3010: character data offset (rec*37) per battle character (x2)
RHandList       = $2B86             ; wRHandItemList::ItemID (5 bytes per character, L-hand list +20)
ItemBuf         = $2E72             ; wItemPropBuf (5 bytes)
ActorMask       = $3A20             ; w7e3a20

.section XC2 $C26470
        .a8
        .i16

; ===========================================================================
; UpdateEquip (C2:0E77, shared by field, menus and battle)
; ===========================================================================
; replaces LDA $15FB,X in the 6-slot loop (X = rec*37 + $24 + slot): A = low byte, B = high bit
XC2_EqLoad:
        php
        rep #$30
        .a16
        jsr XC2_AnyEqBit        ; fast path: no extended equipment anywhere -> B = 0
        beq @w
        txa
        sec
        sbc #$0024
        jsl XJ_EqpN
        jsl XJ_BitTst
@w:     plp
        .a8
        .i16
        xba
        lda $15FB,x
        rts

; CalcEquipEffect prologue (replaces XBA / LDA #$1E / JSR MultAB / TAX): X = (B:A) * 30
XC2_PropOfs:
        rep #$20
        .a16
        and #$01FF
        asl a
        pha
        asl a
        asl a
        asl a
        asl a
        sec
        sbc 1,s
        tax
        pla
        sep #$20
        .a8
        rts

; LearnItemMagic (C2:600C): A = equipment low byte, X = rec*37+slot -> C = id16 * 30 (then TAX)
XC2_LearnOfs:
        rep #$20
        .a16
        and #$00FF
        pha
        txa
        jsl XJ_EqpN
        jsl XJ_BitTst
        xba
        ora 1,s
        asl a
        sta 1,s
        asl a
        asl a
        asl a
        asl a
        sec
        sbc 1,s
        sta 1,s
        pla
        sep #$20
        .a8
        rts

; XC2_AnyEqBit (A16): A = OR of the 12 equipment-bitmap bytes ($1D18-$1D23); Z set if no equipment slot of any
; record holds an extended item (then every per-slot lookup can be skipped). X,Y kept.
        .a16
XC2_AnyEqBit:
        lda f:XBITS_C2+32
        ora f:XBITS_C2+34
        ora f:XBITS_C2+36
        ora f:XBITS_C2+38
        ora f:XBITS_C2+40
        ora f:XBITS_C2+42
        rts
        .a8

; ===========================================================================
; battle inventory init (C2:546E, A16/XY16)
; ===========================================================================
        .a16
        .i16
; hands: replaces LDA $1620,Y (L) / LDA $161F,Y (R), Y = rec*37. A = $01lo (extended) or $00lo
XC2_HandL:
        sep #$20
        .a8
        lda #$00
        sta f:XBTLNAME
        rep #$20
        .a16
        tya
        inc a
        jsr XC2_HandHiA
        pha
        lda $1620,y
        and #$00FF
        ora 1,s
        sta 1,s
        pla
        rts

XC2_HandR:
        tya
        jsr XC2_HandHiA
        pha
        lda $161F,y
        and #$00FF
        ora 1,s
        sta 1,s
        pla
        rts

; A = data offset rel. $161F -> A = $0100 if the slot is extended else 0 (low byte 0)
XC2_HandHiA:
        pha
        jsr XC2_AnyEqBit
        bne @full
        pla
        lda #$0000
        rts
@full:  pla
        jsl XJ_EqpN
        jsl XJ_BitTst
        xba
        and #$FF00
        rts

; replaces JSR CopyItemProp for the hand entries: A bit 8 set -> extended properties
XC2_CopyItemPropB:
        bit #$0100
        bne @ext
        and #$00FF
        jmp CopyItemProp
@ext:   phx
        jsr XC2_LoadItemPropX
        sep #$20
        .a8
        ldx #$0004
@c:     lda ItemBuf,x
        sta $0000,y
        dey
        dex
        bpl @c
        rep #$20
        .a16
        plx
        rts

; LoadItemProp for an extended id (A16 = $01lo): same fields as vanilla C2:54DC, read from XItemProp, but
; an extended item is never usable or throwable in battle (usage bits $80 kept, $20 never set).
XC2_LoadItemPropX:
        pha
        sep #$20
        .a8
        lda #$80
        sta ItemBuf+1
        lda #$FF
        sta ItemBuf+4
        lda 1,s
        sta ItemBuf
        rep #$20
        .a16
        pla
        and #$01FF
        asl a
        pha
        asl a
        asl a
        asl a
        asl a
        sec
        sbc 1,s
        tax
        pla
        sep #$20
        .a8
        lda f:XItemProp+14,x
        sta ItemBuf+2
        lda f:XItemProp,x
        and #$07
        phx
        rep #$20
        .a16
        and #$00FF
        tax
        sep #$20
        .a8
        lda f:ItemTypeMaskTbl,x
        plx
        asl a
        tsb ItemBuf+1
        bcs @done
        rep #$21
        .a16
        stz $EE
        lda f:XItemProp+1,x
        ldx #$0006
@m:     bit ActorMask,x
        bne @k
        sec
@k:     rol $EE
        dex
        dex
        bpl @m
        sep #$20
        .a8
        lda $EE
        sta ItemBuf+4
@done:  rep #$20
        .a16
        rts

; inventory: an extended slot is presented to the battle as an EMPTY slot (never usable / throwable /
; stealable-into / wagerable); C2:4981 (XBattleEndInv) restores it at battle end.
; C2:54B0 (replaces SEP #$30 / TDC after the vanilla copy loop, A16/XY16): the vanilla loop has copied every slot
; (extended slots with their alias properties); this pass re-copies each extended slot exactly as the vanilla loop
; copies an empty slot (qty 0, CopyItemProp($FF)). Bitmap bytes that are zero are skipped, so a save without
; extended items costs 32 byte tests (battle init timing unchanged).
        .a16
        .i16
XC2_ExtSlotsEmpty:
        ldx #$001F
@b:     lda f:XBITS_C2,x
        and #$00FF
        bne @slow
@n:     dex
        bpl @b
        sep #$30
        tdc
        rts
        .a16
        .i16
@slow:  phx
        pha                     ; remaining bits of this byte (1,s), processed bit 7 first
        txa
        asl a
        asl a
        asl a
        ora #$0007
        tax                     ; X = last slot of the byte (descending, as the vanilla loop)
@s:     lda 1,s
        asl a
        sta 1,s
        bit #$0100
        beq @ns
        phx
        txa
        asl a
        asl a
        clc
        adc 1,s                 ; 5 * slot
        adc #$268A              ; Y = last byte of wItemList[slot]
        tay
        stz $2E75               ; quantity 0 (as the vanilla loop stores it, 16-bit)
        lda #$00FF
        jsr CopyItemProp        ; id $FF, usage $80, equip $FF; Y -= 5 (MVP)
        sep #$20
        .a8
        lda $0008,y             ; targeting: LoadItemProp($FF) does not write it, so a vanilla empty slot keeps
        sta $0003,y             ; the byte of the entry processed just before (slot + 1, or the R-hand entry)
        rep #$20
        .a16
        plx
@ns:    dex
        lda 1,s
        and #$00FF
        bne @s
        pla
        plx
        jmp @n

; X = inventory slot -> A = 0/1 (Z), X,Y kept (A16/XY16)
XC2_InvHiX:
        txa
        and #$00FF
        jsl XJ_BitTst
        cmp #$0000
        rts
        .a8
        .i16

; colosseum wager removal (C2:49AD, CMP $1869,X, M8/X16): an extended slot never matches (Z=0; caller tests BNE)
XC2_CmpInvXMask:
        php
        rep #$30
        .a16
        pha
        jsr XC2_InvHiX
        bne @e
        pla
        plp
        .a8
        .i16
        cmp $1869,x
        rts
@e:     pla
        plp
        .a8
        .i16
        rep #$02                ; an extended slot never matches (Z=0)
        rts

; ===========================================================================
; battle: weapon animation index, spear jump x2, ogre nix   (M8 / X8)
; ===========================================================================
        .i8
; XC2_HandExt: X = battle character index (+1 = left hand) -> Z clear if that equipment slot is extended.
; P (M/X) preserved; A destroyed.
XC2_HandExt:
        php
        rep #$30
        .a16
        .i16
        jsr XC2_AnyEqBit
        beq @q
        phx
        txa
        and #$0001
        pha
        txa
        and #$00FE
        tax
        lda CharPtr,x
        clc
        adc 1,s
        jsl XJ_EqpN
        jsl XJ_BitTst
        sta 1,s
        pla
        plx
@q:     plp
        .a8
        .i8
        cmp #$00
        rts

; replaces LDA RHandItem,X before INC / STA $B7 (animation number = weapon id + 1)
; extended weapon -> $BF + low byte (INC -> $C0 + low byte: XWeaponAnimFull entries $C0-$FF)
XC2_AnimId:
        cpx #$08
        bcs @r
        lda RHandItem,x
        cmp #$FF
        beq @r
        jsr XC2_HandExt
        beq @r
        lda RHandItem,x
        clc
        adc #$BF
        rts
@r:     lda RHandItem,x
        rts

; replaces LDA RHandItem,X / JSR SpearEffect (R) and LDA LHandItem,X / JSR SpearEffect (L)
XC2_SpearR:
        jsr XC2_HandExt
        bne XC2_SpearExt
        lda RHandItem,x
        jmp SpearEffect

XC2_SpearL:
        inx
        jsr XC2_HandExt
        bne @ext
        dex
        lda RHandItem+1,x
        jmp SpearEffect
@ext:   jsr XC2_SpearExt
        dex
        rts

; X = attacker (+hand): extended spear (XExtFlags bit 1) -> damage multiplier 2 (as SpearEffect)
XC2_SpearExt:
        lda RHandItem,x
        cmp #$40
        bcs @n
        phx
        php
        rep #$30
        .a16
        .i16
        and #$003F
        tax
        sep #$20
        .a8
        lda f:XExtFlags,x
        plp
        .a8
        .i8
        plx
        and #$02
        beq @n
        lda #$02
        sta $BD
@n:     rts

; Ogre Nix break test (C2:3F0B, X = item-list offset of the hand: char*5, +20 for the left hand):
; an extended weapon is never broken (reads as $FF)
XC2_OgreLoad:
        php
        rep #$30
        .a16
        .i16
        phx
        txa
        and #$00FF
        ldx #$0000
        cmp #20
        bcc @r
        sbc #20
        inx
@r:     phx                     ; hand
        ldx #$0000
@d:     cmp #5
        bcc @c
        sbc #5
        inx
        inx
        bra @d
@c:     lda CharPtr,x
        clc
        adc 1,s
        jsl XJ_EqpN
        jsl XJ_BitTst
        sta 1,s
        pla
        plx
        plp
        .a8
        .i8
        cmp #$00
        bne @e
        lda RHandList,x
        rts
@e:     lda #$FF
        rts
        .i16
