; =============================================================================
; TECH v0.7.1 - bank C0 stubs (vanilla free space C0:D613-C0:DF9F, claim ITEMX_C0_STUBS)
; Field context: .a8 .i16, DB=$00, D=$0000 (every stub keeps the caller's P/registers unless stated).
; =============================================================================

IncEventPtrContinue = $C09B5C
INV1869 = $1869
EQP161F = $161F

.section XC0 $C0D620
        .a8
        .i16

; ---------------------------------------------------------------------------
; Event API (opcodes $66/$67/$68 were vanilla "unused / lock-up" commands -> EventCmdTbl retargeted)
;   $66 lo hi           GIVE_EXT_ITEM id      (+1, stacks to 99; no effect if inventory full / id undefined)
;   $67 lo hi           TAKE_EXT_ITEM id      (-1 from the inventory only; equipped copies untouched)
;   $68 lo hi sl sh     HAS_EXT_ITEM id, sw   (event switch sw := 1 if in inventory or equipped, else 0)
XC0_Ev66:
        rep #$20
        lda $eb
        jsl XJ_GiveExt
        sep #$20
        tdc                     ; B must be 0: ExecCmd does a 16-bit ASL of the next opcode
        lda #3
        jmp IncEventPtrContinue

XC0_Ev67:
        rep #$20
        lda $eb
        jsl XJ_TakeExt
        sep #$20
        tdc                     ; B must be 0: ExecCmd does a 16-bit ASL of the next opcode
        lda #3
        jmp IncEventPtrContinue

XC0_Ev68:
        rep #$20
        lda $eb
        jsl XJ_HasExt
        ldy $ed
        jsl XJ_EvSwitch
        sep #$20
        tdc
        lda #5
        jmp IncEventPtrContinue

; ---------------------------------------------------------------------------
; XC0_InvHi: X = inventory slot -> A = 0/1, Z set if vanilla slot. X,Y kept, C destroyed.
XC0_InvHi:
        php
        rep #$30
        txa
        and #$00FF
        jsl XJ_BitTst
        plp
        .a8
        .i16
        cmp #$00
        rts

; replaces LDA $1869,X in vanilla "find the same item" loops: an extended slot reads as $FF (never equal
; to a vanilla id 00-FE) so vanilla items are never merged into / taken from extended slots.
XC0_LdaInvXMask:
        jsr XC0_InvHi
        bne @ext
        lda INV1869,x
        rts
@ext:   lda #$FF
        rts

; replaces STA $1869,X where vanilla code puts a vanilla id into an empty slot: clear the slot's high bit
XC0_StaInvXClr:
        sta INV1869,x
        php
        rep #$30
        pha
        txa
        and #$00FF
        jsl XJ_BitClr
        pla
        plp
        rts

; EventCmd_8d (remove a character's equipment): replaces LDA $161F,X (X = rec*37+slot).
; extended slot -> the extended item goes back to the inventory, slot := $FF, bit cleared, returns $FF
; (so the vanilla code skips it); vanilla slot -> returns the vanilla byte.
XC0_8dLoad:
        php
        rep #$30
        txa
        jsl XJ_EqpN
        pha
        jsl XJ_BitTst
        cmp #$0000              ; XBitTst returns the caller's flags
        beq @van
        sep #$20
        .a8
        lda EQP161F,x
        rep #$20
        .a16
        and #$00FF
        ora #$0100
        jsl XJ_GiveExt
        pla
        jsl XJ_BitClr
        sep #$20
        .a8
        lda #$FF
        sta EQP161F,x
        plp
        .a8
        .i16
        lda #$FF
        rts
@van:   pla
        plp
        .a8
        .i16
        lda EQP161F,x
        rts

; character (re)initialisation from CharProp: replaces STA $161F,Y (Y = rec*37). The 6 equipment bytes
; are about to be written with vanilla ids -> clear the record's 6 high bits.
XC0_InitEqp:
        sta EQP161F,y
        php
        rep #$30
        pha
        phx
        tya
        jsl XJ_EqpN
        ldx #$0006
@l:     pha
        jsl XJ_BitClr
        pla
        inc a
        dex
        bne @l
        plx
        pla
        plp
        rts
