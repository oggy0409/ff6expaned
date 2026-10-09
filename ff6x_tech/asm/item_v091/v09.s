; =============================================================================
; FF6 Expanded Edition - TECH v0.9 - consumables / extended shops / FF6X rare items (bank FA routines)
; TECH v0.9.1 copy (asm/item_v091): + item-action context (XSetItemCtx), cleared at dispatch / New Game / load
; =============================================================================
; Extended consumables are extended items ($100 | lo) whose XExtFlags byte has bit0 (defined) and bit2
; (consumable); bit3 = sellable. Their effect is ItemProp data run by the vanilla item code (C2 CalcItemEffect,
; C3 field menu); this file only routes the 9-bit id where the vanilla code would read the 8-bit alias.
;
; Battle context (TECH v0.9):
;   wItemList entry UsageFlags bit0 ($01, unused by vanilla) = EXTENDED CONSUMABLE MARKER. Every bank C1 search
;   by item id also compares the marker (an extended consumable and the vanilla item with the same low byte are
;   different entries).
;   XCURCMD  command of the attack whose target / effect is being initialised (C2 InitTarget), $FE = field menu
;   XATKX    bit0 = next item-name draw uses the extended name, bit1 = next item animation uses XItemAnimX
;   XHELD    per character (0-3): the item held by a queued Item command is an extended consumable
; The vanilla Item command can never use the vanilla items whose low byte an extended consumable uses
; (validated by the builder: they are not battle-usable), so (command = Item, low byte, XExtFlags) identifies
; an extended consumable without ambiguity.
;
; FF6X rare items: logical rare ids 0-19 = vanilla rare items (event bits $1D0-$1E3), 20-51 = FF6X rare items
; (XRARE bit id-20, defined ids in XRareDef). Rare menu: 20 entries per page (2 x 10), XRAREPAGE.
; =============================================================================

XCURCMD     = $7E1E36
XATKX       = $7E1E37
XHELD       = $7E1E38           ; 4 bytes
XSHOPCURHI  = $7E1E3C
XRAREPAGE   = $7E1E3D
XBTLNAME_V  = $7E1E3E
RARE_N      = 52                ; logical rare ids 0..51
RARE_VAN    = 20                ; vanilla rare items 0..19
ITEMLIST    = $7E2686           ; wItemList (256 x 5)
ITEMBUF     = $7E2E72           ; wItemPropBuf
ACTBUF      = $7E2BAF           ; wPlayerActionBuf::BattleCmd (+1 Attack)
GAINBUF     = $7E602D           ; obtained items (5 bytes each)
RARELIST    = $7E9D89
hWMDATA_L   = $002180
hRDMPYL_L   = $004216
ItemAnimPtrs = $D10000

.section XFA_CODE $FA8000
        .a16
        .i16

; ===========================================================================
; extended consumable test
; ===========================================================================
; XIsCons (far, any mode): A low byte = item low byte -> C=1 if $100|lo is a defined extended consumable.
; A, X, Y and every other flag preserved.
XIsCons:
        php
        rep #$30
        pha
        jsr IsConsN
        pla
        jsr RetC
        plp
        rtl
        .a16
        .i16

; IsConsN (near, A16/X16): A low byte -> C. A, X, Y kept.
IsConsN:
        pha
        phx
        and #$00FF
        cmp #$0040
        bcs @no
        tax
        lda f:XExtFlags,x
        and #$0005
        cmp #$0005
        bra @r
@no:    clc
@r:     plx
        pla
        rts
        .a16
        .i16

; XPropOfs (far): A = 9-bit id -> A16 = id * 30. Other registers / flags preserved.
XPropOfs:
        php
        rep #$30
        and #$01FF
        asl a
        pha
        asl a
        asl a
        asl a
        asl a
        sec
        sbc 1,s
        sta 1,s
        pla
        plp
        rtl
        .a16
        .i16

; XLoadPropX (far, any mode): A low byte = low byte of an extended consumable. Fills wItemPropBuf like the vanilla
; LoadItemProp (C2:54DC) does from the XItemProp record: id, usage ($80 unless usable in battle; never throwable;
; + marker $01), targeting, equip flags ($0F: no battle character can equip a consumable). Quantity ($2E75) untouched.
; All registers preserved.
XLoadPropX:
        php
        rep #$30
        pha
        phx
        and #$00FF
        pha                     ; lo (1,s)
        ora #$0100
        asl a
        pha
        asl a
        asl a
        asl a
        asl a
        sec
        sbc 1,s
        tax                     ; X = id9 * 30
        pla
        sep #$20
        .a8
        lda 1,s
        sta f:ITEMBUF
        lda f:XItemProp+14,x
        sta f:ITEMBUF+2
        lda f:XItemProp,x
        and #$20                ; usable in battle
        eor #$20
        asl a
        asl a                   ; $00 usable / $80 unusable
        ora #$01                ; extended consumable marker
        sta f:ITEMBUF+1
        lda #$0F
        sta f:ITEMBUF+4
        rep #$20
        .a16
        pla
        plx
        pla
        plp
        rtl
        .a16
        .i16

; ===========================================================================
; battle (C2) hooks: DB = $7E, D = 0; entered with the caller's M / X (8-bit unless stated), all far
; ===========================================================================
; XB_PropCtx (C2:271D InitItemTarget, C2:2A60 CalcItemEffect; replaces JSR GetItemPropPtr, A = item id):
; returns C (16 bits) = id9 * 30 like GetItemPropPtr / MultAB, every flag (carry!) as at entry. id9 = $100 | id when
; XCURCMD = Item and the id is an extended consumable, or XCURCMD = $FE (field menu use of an extended slot; consumed).
XB_PropCtx:
        php
        rep #$30
        phx
        and #$00FF
        pha                     ; id (1,s)
        lda f:XCURCMD
        and #$00FF
        cmp #$00FE
        beq @menu
        cmp #$0001
        bne @van
@chk:   lda 1,s
        jsr IsConsN
        bcc @van
        pla
        ora #$0100
        bra @mul
@menu:  sep #$20
        .a8
        lda #$00
        sta f:XCURCMD
        rep #$20
        .a16
        bra @chk
@van:   pla
@mul:   and #$01FF
        jsr XSetItemCtx         ; TECH v0.9.1: XFIXAMT / XHYBEL for this item action (A kept)
        asl a
        pha
        asl a
        asl a
        asl a
        asl a
        sec
        sbc 1,s
        sta 1,s
        pla
        plx
        plp
        rtl
        .a16
        .i16

; XB_ItemTgtC (C2:273C, A8 = item id): the vanilla CMP #$E6 (carry = item does not cast a spell), with the carry set
; for an extended consumable of the Item command. A kept.
        .a8
XB_ItemTgtC:
        cmp #$E6
        bcs @r
        pha
        lda f:XCURCMD
        cmp #$01
        bne @n
        lda 1,s
        jsl XIsCons
        pla
        rtl
@n:     pla
        clc
@r:     rtl

; XB_ItemCmd (C2:189F Item / Throw command, X8 = attacker; replaces LDA #$01 / STA $3412): attack name type 1,
; XATKX := 3 (extended name + animation) for a character's Item command with an extended consumable, else 0.
        .i8
XB_ItemCmd:
        lda #$01
        sta $3412
        lda #$00
        cpx #$08
        bcs @w
        lda $B5
        cmp #$01
        bne @z
        lda $3A7D
        jsl XIsCons
        lda #$00
        bcc @w
        lda #$03
        bra @w
@z:     lda #$00
@w:     sta f:XATKX
        rtl

; XB_Dispatch (C2:1559 command dispatch; replaces STA $B5 / ASL / TAX): XATKX cleared before every command
XB_Dispatch:
        sta $B5
        pha
        lda #$00
        sta f:XATKX
        sta f:XFIXAMT           ; TECH v0.9.1: no fixed-amount / hybrid context outside an item action
        sta f:XFIXAMT+1
        sta f:XHYBEL
        sta f:XVANOK
        pla
        asl a
        tax
        rtl

; XB_Consume (C2:18B0, X8 = attacker; replaces LDA #$FF / STA $32F4,X): the held item is used up: XHELD cleared.
; P preserved (the vanilla code branches on the InitTarget carry after this hook), A = $FF as vanilla.
XB_Consume:
        php                     ; the carry from InitTarget is tested by the vanilla code after this hook (C2:18BD)
        lda #$FF
        sta $32F4,x
        jsr HeldClr
        plp
        .a8
        .i8
        lda #$FF
        rtl

; XB_StaHeldVan (C2:39EC steal / C2:3A7C metamorph; replaces STA $32F4,X): a vanilla item becomes the held /
; obtained item: XHELD cleared. A and P kept.
XB_StaHeldVan:
        sta $32F4,x
        php
        pha
        jsr HeldClr
        pla
        plp
        .a8
        .i8
        rtl

; HeldClr (near, M8 X8): XHELD[X / 2] := 0 for a character (X < 8). A destroyed, X kept.
HeldClr:
        cpx #$08
        bcs @r
        phx
        txa
        lsr a
        tax
        lda #$00
        sta f:XHELD,x
        plx
@r:     rts

; XB_Hold (C2:4DB0 FixPlayerAttack, Item / Throw queued: A = item id, B = command, Y8 = character; replaces
; STA $32F4,Y): XHELD[character] := (command = Item and extended consumable). A (16 bits) kept.
XB_Hold:
        sta $32F4,y
        php
        rep #$20
        .a16
        pha
        sep #$20
        .a8
        phx
        cpy #$08
        bcs @r
        tya
        lsr a
        tax
        lda 3,s                 ; command (1,s X, 2,s id, 3,s command)
        cmp #$01
        bne @no
        lda 2,s
        jsl XIsCons
        lda #$00
        rol a
        bra @st
@no:    lda #$00
@st:    sta f:XHELD,x
@r:     plx
        rep #$20
        .a16
        pla
        plp
        .a8
        .i8
        rtl

; XB_LoadHeld (C2:62D8, A = id, X8 = character): held extended consumable -> XHELD cleared, wItemPropBuf built with
; the extended properties + marker, C=1. Otherwise C=0 (the caller runs the vanilla LoadItemProp). A, X kept.
XB_LoadHeld:
        cpx #$08
        bcs @v
        pha
        phx
        txa
        lsr a
        tax
        lda f:XHELD,x
        beq @v2
        lda #$00
        sta f:XHELD,x
        plx
        pla
        jsl XLoadPropX
        sec
        rtl
@v2:    plx
        pla
@v:     clc
        rtl

; XB_ConsEntry (C2:54B0 XC2_ExtSlotsEmpty, A16/X16: X = inventory slot holding an extended item, Y = last byte of its
; wItemList entry): extended consumable -> the 5-byte entry (id, usage + marker, targeting, quantity, equip flags),
; Y -= 5, C=1. Otherwise C=0, nothing written. A destroyed, X kept.
        .a16
        .i16
XB_ConsEntry:
        lda $1869,x
        jsr IsConsN
        bcc @r
        jsl XLoadPropX
        sep #$20
        .a8
        lda $1969,x
        sta $2E75
        phx
        ldx #$0004
@cp:    lda f:ITEMBUF,x
        sta $0000,y
        dey
        dex
        bpl @cp
        plx
        rep #$21
        .a16
        sec
@r:     rtl
        .a16
        .i16

; ===========================================================================
; FF6X rare items
; ===========================================================================
; RareLoc (near, A16/X16): A = rare id 0..51 -> X = WRAM address (bank $7E) of its bit, A = mask
RareLoc:
        cmp #RARE_VAN
        bcs @ff
        clc
        adc #$01D0              ; vanilla rare item = event bit $1D0 + id
        pha
        lsr a
        lsr a
        lsr a
        clc
        adc #$1E80
        tax
        pla
        bra @m
@ff:    sec
        sbc #RARE_VAN
        pha
        lsr a
        lsr a
        lsr a
        clc
        adc #XRARE & $FFFF
        tax
        pla
@m:     and #$0007
        asl a
        phx
        tax
        lda f:XMaskW,x
        plx
        rts
        .a16
        .i16

; RareTst (near): A = rare id -> A = 0 / mask, Z set if not owned. X, Y kept.
RareTst:
        phx
        jsr RareLoc
        and f:$7E0000,x
        plx
        and #$00FF
        rts
        .a16
        .i16

; RareDef (near): A = rare id -> C=1 if the id exists (vanilla 0..19, or FF6X id defined in XRareDef). A, X kept.
RareDef:
        cmp #RARE_N
        bcs @no
        cmp #RARE_VAN
        bcc @yes
        pha
        phx
        sec
        sbc #RARE_VAN
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
        and f:XRareDef,x
        and #$00FF
        plx
        cmp #$0001              ; C=1 if the bit is set
        pla
        rts
@no:    clc
        rts
@yes:   sec
        rts
        .a16
        .i16

; RareSign (near): XRSIG := 'R', XRARE0^XRARE1^XRARE2^XRARE3^$A5. A destroyed.
RareSign:
        lda f:XRARE
        eor f:XRARE+2
        pha
        xba
        eor 1,s
        eor #$00A5
        xba
        and #$FF00
        ora #$0052
        sta f:XRSIG
        pla
        rts
        .a16
        .i16

; RareCheck (near, load): invalid rare-block signature -> FF6X rare items cleared; valid -> undefined ids dropped.
RareCheck:
        lda f:XRSIG
        pha
        jsr RareSign
        pla
        cmp f:XRSIG
        beq @ok
        lda #$0000
        sta f:XRARE
        sta f:XRARE+2
        jmp RareSign
@ok:    lda f:XRARE
        and f:XRareDef
        sta f:XRARE
        lda f:XRARE+2
        and f:XRareDef+2
        sta f:XRARE+2
        jmp RareSign
        .a16
        .i16

; ClrTrans (near): zero the transient bytes $1E36-$1E3D. A destroyed.
ClrTrans:
        lda #$0000
        sta f:XTRANS
        sta f:XTRANS+2
        sta f:XTRANS+4
        sta f:XTRANS+6
        sta f:XFIXAMT           ; TECH v0.9.1: $1E23-$1E26 (XFIXAMT, XHYBEL, XVANOK)
        sta f:XFIXAMT+2
        rts
        .a16
        .i16

; XRareGive / XRareTake (far, any mode): A low byte = rare id. C=1 if the id exists (state then set / cleared).
XRareGive:
        php
        rep #$30
        pha
        phx
        and #$00FF
        jsr RareDef
        bcc @r
        pha
        jsr RareLoc
        sep #$20
        .a8
        ora f:$7E0000,x
        sta f:$7E0000,x
        rep #$20
        .a16
        pla
        jsr RareSign
        sec
@r:     plx
        pla
        jsr RetC
        plp
        rtl
        .a16
        .i16

XRareTake:
        php
        rep #$30
        pha
        phx
        and #$00FF
        jsr RareDef
        bcc @r
        pha
        jsr RareLoc
        sep #$20
        .a8
        eor #$FF
        and f:$7E0000,x
        sta f:$7E0000,x
        rep #$20
        .a16
        pla
        jsr RareSign
        sec
@r:     plx
        pla
        jsr RetC
        plp
        rtl
        .a16
        .i16

; XRareHas (far, any mode): A low byte = rare id -> C=1 if owned
XRareHas:
        php
        rep #$30
        pha
        and #$00FF
        cmp #RARE_N
        bcs @no
        jsr RareTst
        beq @no
        sec
        bra @r
@no:    clc
@r:     pla
        jsr RetC
        plp
        rtl
        .a16
        .i16

; RareCountN (near): A = number of owned rare items (0..52). X, Y kept.
RareCountN:
        phx
        phy
        ldy #$0000
        ldx #$0000
@l:     txa
        jsr RareTst
        beq @n
        iny
@n:     inx
        cpx #RARE_N
        bne @l
        tya
        ply
        plx
        rts
        .a16
        .i16

; XRareCount (far, menu M8): A low byte = number of owned rare items (B kept). X, Y, flags kept.
XRareCount:
        php
        rep #$30
        pha
        jsr RareCountN
        sep #$20
        .a8
        sta 1,s
        rep #$20
        .a16
        pla
        plp
        rtl
        .a16
        .i16

; XRareNext (far): C=1 if a page after XRAREPAGE exists (count > (page + 1) * 20). Registers kept.
XRareNext:
        php
        rep #$30
        pha
        lda f:XRAREPAGE
        and #$00FF
        inc a
        asl a
        asl a
        pha
        asl a
        asl a
        clc
        adc 1,s
        sta 1,s                 ; (page + 1) * 20
        jsr RareCountN
        cmp 1,s
        beq @no                 ; count = (page + 1) * 20: no further page
        pla                     ; C = count >= (page + 1) * 20
        pla
        jsr RetC
        plp
        rtl
@no:    pla
        pla
        clc
        jsr RetC
        plp
        rtl
        .a16
        .i16

; XRareList (far, any mode): the rare item list of page XRAREPAGE at 7E:9D89 (20 entries, $FF = none) + $FF at
; 7E:9D9D (CountRareItems / DrawRareItemList read up to the terminator). Order: rare id. Registers kept.
XRareList:
        php
        rep #$30
        pha
        phx
        phy
        sep #$20
        .a8
        ldx #$0000
        lda #$FF
@f:     sta f:RARELIST,x
        inx
        cpx #21
        bne @f
        rep #$20
        .a16
        lda f:XRAREPAGE
        and #$00FF
        asl a
        asl a
        pha
        asl a
        asl a
        clc
        adc 1,s
        sta 1,s                 ; first list index of the page (1,s)
        ldy #$0000              ; owned items seen
        ldx #$0000              ; rare id
@id:    txa
        jsr RareTst
        beq @n
        tya
        sec
        sbc 1,s
        bcc @k                  ; before this page
        cmp #20
        bcs @k                  ; after this page
        phx
        tax
        lda 1,s                 ; rare id
        sep #$20
        .a8
        sta f:RARELIST,x
        rep #$20
        .a16
        plx
@k:     iny
@n:     inx
        cpx #RARE_N
        bne @id
        pla
        ply
        plx
        pla
        plp
        rtl
        .a16
        .i16

; ===========================================================================
; extended shops
; ===========================================================================
; XShopOwned (far, menu; replaces the owned-count loop of _c3bc57 C3:BC5D, WMADD already = 7E:9DC9):
; for each of the 8 shop entries writes the owned quantity of exactly that item (vanilla id: vanilla slot only;
; extended entry: extended slot only). Registers kept.
XShopOwned:
        php
        rep #$30
        pha
        phx
        phy
        ldy #$0000              ; entry
@e:     tya
        clc
        adc $67                 ; zSelCharPropPtr = shop * 9
        inc a
        tax
        lda f:XShopPropHi,x
        and #$00FF
        pha                     ; wanted high bit (3,s after the next PHA)
        tyx
        lda f:RARELIST,x        ; 7E:9D89 + entry = shop item low byte
        and #$00FF
        pha                     ; low byte (1,s)
        ldx #$0000
@f:     lda f:INVID,x
        and #$00FF
        cmp 1,s
        bne @fn
        txa
        jsr TstN
        beq @v
        lda #$0001
@v:     cmp 3,s
        beq @hit
@fn:    inx
        cpx #$0100
        bne @f
        lda #$0000
        bra @w
@hit:   lda f:INVQTY,x
@w:     sep #$20
        .a8
        sta f:hWMDATA_L
        rep #$20
        .a16
        pla
        pla
        iny
        cpy #$0008
        bne @e
        ply
        plx
        pla
        plp
        rtl
        .a16
        .i16

; ===========================================================================
; bank C1 (battle menu / graphics) hooks
; ===========================================================================
; C1:4CA5 DrawItemListText: replaces LDA wItemList::ItemID,Y / STA w7e5755+5 / STA w7e5755+12 (M8 X16).
; XBTLNAME := marker of the entry (consumed by ListTextCmd_0e, XC1_NameIdx, when this row's name is drawn).
; w7e5755+12 follows the EN template's unused command $12 and is drawn as a text code: $FF (blank) for an extended
; consumable.
        .a8
XC1_ListRow:
        php
        phx
        sep #$20
        tyx
        lda f:ITEMLIST,x
        sta f:$7E575A
        sta f:$7E5761
        lda f:ITEMLIST+1,x
        and #$01
        sta f:XBTLNAME_V
        beq @v
        lda #$FF                ; extended consumable: blank after the quantity (the EN template draws the id byte
        sta f:$7E5761           ; at +12 as a text code: vanilla $E8-$FF items are blank there)
@v:     plx
        plp
        .a8
        .i16
        rtl

; C1:7164 (item used / thrown from the list, Y = player action buffer): finds the list entry of the selected item:
; same id and marker = (command is Item and the id is an extended consumable). C=1 + X = entry, C=0 not found.
XC1_DecFind:
        php
        sep #$20
        tyx
        lda #$00
        pha                     ; wanted marker (1,s)
        lda f:ACTBUF,x
        cmp #$01
        bne @w
        lda f:ACTBUF+1,x
        jsl XIsCons
        bcc @w
        lda #$01
        sta 1,s
@w:     lda f:ACTBUF+1,x
        ldx #$0000
@l:     cmp f:ITEMLIST,x
        bne @n
        pha
        lda f:ITEMLIST+1,x
        and #$01
        cmp 2,s
        bne @n0
        pla
        pla
        plp
        .a8
        .i16
        sec
        rtl
@n0:    pla
@n:     inx
        inx
        inx
        inx
        inx
        cpx #$0500
        bne @l
        pla
        plp
        .a8
        .i16
        clc
        rtl

; C1:4458 (an obtained / returned item is added to the list; A = id, Y = obtained-item offset): same id and same
; marker. C=1 + X = entry, C=0 not found (the caller then uses the first empty entry).
XC1_AddFind:
        php
        sep #$20
        pha                     ; id
        phx
        tyx
        lda f:GAINBUF+1,x
        plx
        and #$01
        pha                     ; wanted marker (1,s), id (2,s)
        ldx #$0000
@l:     lda f:ITEMLIST,x
        cmp 2,s
        bne @n
        lda f:ITEMLIST+1,x
        and #$01
        cmp 1,s
        beq @hit
@n:     inx
        inx
        inx
        inx
        inx
        cpx #$0500
        bne @l
        pla
        pla
        plp
        .a8
        .i16
        clc
        rtl
@hit:   pla
        pla
        plp
        .a8
        .i16
        sec
        rtl

; C1:8CBC FindInventoryItem (A = id of a hand item going back to the list, X = 0): vanilla entries only
; (marker 0). C=0 + X = entry, C=1 not found (vanilla convention).
XC1_FindVan:
        php
        sep #$20
        pha
        ldx #$0000
@l:     lda f:ITEMLIST,x
        cmp 1,s
        bne @n
        lda f:ITEMLIST+1,x
        and #$01
        beq @hit
@n:     inx
        inx
        inx
        inx
        inx
        cpx #$0500
        bne @l
        pla
        plp
        .a8
        .i16
        sec
        rtl
@hit:   pla
        plp
        .a8
        .i16
        clc
        rtl

; C1:605B (attack name of an item: id * 13 just multiplied): replaces LDA f:hRDMPYL / TAX (M16). If the current
; Item command uses an extended consumable (XATKX bit0, set by C2 XC2_ItemCmd), the name is read from
; XItemName + $D00 (= ($100 + id) * 13) and the flag is consumed.
        .a16
XC1_AtkNameX:
        lda f:hRDMPYL_L
        pha
        sep #$20
        .a8
        lda f:XATKX
        lsr a
        bcc @v
        asl a
        sta f:XATKX
        rep #$20
        .a16
        pla
        clc
        adc #$0D00
        tax
        rtl
@v:     rep #$20
        .a16
        pla
        tax
        rtl

; C1:BC58 (item animation, A8 = item number): replaces the ItemAnimPtrs lookup (CMP #$E0 .. LDA f:ItemAnimPtrs,X /
; TAX). Returns X = animation, M = 16-bit (as the vanilla code at C1:BC6C). Extended consumable of the current
; Item command (XATKX bit1, consumed): XItemAnimX[lo].
        .a8
XC1_ItemAnim:
        pha
        lda f:XATKX
        and #$02
        beq @van
        lda f:XATKX
        and #$FD
        sta f:XATKX
        lda 1,s
        jsl XIsCons
        bcc @van
        pla
        rep #$30
        .a16
        and #$003F
        asl a
        tax
        lda f:XItemAnimX,x
        tax
        rtl
        .a8
@van:   pla
        cmp #$E0
        bcc @lo
        sec
        sbc #$E0
        bra @g
@lo:    lda #$E0
@g:     rep #$20
        .a16
        asl a
        tax
        lda f:ItemAnimPtrs,x
        tax
        rtl
        .a16
