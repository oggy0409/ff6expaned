; =============================================================================
; FF6 Expanded Edition - TECH v0.9.1 - item data alignment engine additions (bank FA + C2 / C3 stubs)
; =============================================================================
; Locked consumable values that the vanilla item code cannot express, for EXTENDED consumables only
; (every vanilla item keeps its vanilla behaviour: the tables below are indexed by the extended low byte and the
; context is cleared for every id < $100):
;
;   XFixAmt  FA:7E00  64 x 2  fixed amount (0 = vanilla power rule): HP / MP restored by a restoring item (Gaia
;                              Tonic 1500 HP, Iron Ration 600 HP, Aether Flask 100 MP: no battle variance) / total
;                              damage before the split of a hybrid item (Magitek Cell).
;   XHybrid  FA:7E80  64 x 1  hybrid element (0 = none): the damage is split in two halves, the first half takes
;                              the target's reaction to that element, the second half is non-elemental.
;                              Magitek Cell = Lightning.
;   XShopCap FA:7EC0  64 x 1  shop purchase cap (owned + bought <= cap; 0 = vanilla 99). Magitek Cell = 3.
;   XCtxFlags FA:7F00 64 x 1  bit0: the record removes Vanish and that removal is applied (Null Dust, Beacon Flare).
;                              The vanilla Item command clears zb3 bit7, which makes MagicStatusEffect (C2:4418)
;                              cancel any Vanish removal by an item; v0.9.1 keeps that rule for every other item.
;
; Battle: XB_PropCtx (C2 InitItemTarget / CalcItemEffect) stores the context of the item action in
;   XFIXAMT ($1E23-$1E24) / XHYBEL ($1E25) / XVANOK ($1E26); XB_ExecCmd (C2:13FA ExecCmd, every battle command:
;   Regen / Poison ticks, counters, monster actions included) and XB_Dispatch (C2:1559, AI-translated commands)
;   clear it before the command runs, so it can never leak into another action; ClrTrans clears it at New Game / load. The single battle hook is C2:0BD3 (CalcTargetDmg, start of the element block, after
;   CalcDmgMod and after the undead / zombie heal inversion):
;     fixed heal : $11A4 bit0 (restores HP or MP) and XFIXAMT != 0 -> heal amount $F0 := XFIXAMT
;     hybrid     : D = XFIXAMT (or $F0 when 0) -> L = D/2 (element), N = D - L (non-elemental); L follows the vanilla element order
;                  (force field -> 0, absorb, null -> 0, half, weak x2); absorb: net = N - L, a negative net heals;
;                  the vanilla element block is skipped (its test value A := 0). The 9999 cap (CalcMaxDmg) applies.
;     the action element $11A1 stays Lightning (AI element tests and battle messages see a Lightning item).
; Field (C3 _c38ccd, the HP / MP amount of a menu item): XFixAmt of the extended record replaces the power byte.
; Shop (C3 _c3b82f / _b83e): the buy limit of an extended entry is XShopCap (owned count includes every unit the
;   party holds, so leaving / re-entering the shop or saving cannot bypass it).
; =============================================================================

XFIXAMT     = $7E1E23           ; word: fixed HP amount of the current item action (0 = none)
XHYBEL      = $7E1E25           ; byte: hybrid element of the current item action (0 = none)
XVANOK      = $7E1E26           ; byte: the current item action may remove Vanish (XCtxFlags bit0)

.section XFA_CODE $FA8000
        .a16
        .i16

; XSetItemCtx (near, A16 X16, A = 9-bit item id): XFIXAMT / XHYBEL for this item action. A, X kept.
XSetItemCtx:
        pha
        phx
        cmp #$0100
        bcc @clr
        and #$003F
        tax
        sep #$20
        .a8
        lda f:XHybrid,x
        sta f:XHYBEL
        lda f:XCtxFlags,x
        and #$01
        sta f:XVANOK
        rep #$20
        .a16
        txa
        asl a
        tax
        lda f:XFixAmt,x
        sta f:XFIXAMT
        bra @r
@clr:   lda #$0000
        sta f:XFIXAMT
        sta f:XHYBEL            ; + XVANOK
@r:     plx
        pla
        rts

; XB_ExecCmd (far; C2:13FA ExecCmd via XJ_ExecCmd; A8 X8): replaces LDA $B5 / ASL / TAX. Clears the item-action
; context, then A = X = command * 2 as vanilla.
        .a8
XB_ExecCmd:
        lda #$00
        sta f:XFIXAMT
        sta f:XFIXAMT+1
        sta f:XHYBEL
        sta f:XVANOK
        lda $B5
        asl a
        tax
        rtl

; XB_ElemA (far; C2:0BD3 via XC2_ElemA; A8, any index size; DB = $7E, D = 0; Y = target):
; replaces LDA $11A1 (the element test). Applies the fixed heal / hybrid split to $F0 (and $F2 for a hybrid absorb),
; then returns A = $11A1, or A = 0 for a hybrid action (vanilla element block skipped), N/Z from that load.
        .a8
XB_ElemA:
        php
        rep #$30
        .a16
        .i16
        phx
        phy
        lda f:XHYBEL
        and #$00FF
        beq @fix
        jsr HybridDmg
        bra @out
@fix:   lda f:XFIXAMT
        beq @out
        sep #$20
        .a8
        lda $11A4
        lsr a                   ; bit0: the action restores HP / MP (CalcItemEffect)
        rep #$20
        .a16
        bcc @out
        lda f:XFIXAMT
        sta $F0
@out:   ply
        plx
        plp
        .a8
        lda f:XHYBEL
        bne @h
        lda $11A1
        rtl
@h:     lda #$00
        rtl

; HybridDmg (near, A16 X16, Y = target): see the header.
        .a16
        .i16
HybridDmg:
        lda f:XFIXAMT           ; fixed base amount of the hybrid item (0 = the computed damage)
        beq @d
        sta $F0
@d:     lda $F0
        lsr a
        pha                     ; L (element half)          3,s after the next push
        eor #$FFFF
        sec
        adc $F0
        pha                     ; N = D - L (non-elemental)  1,s
        sep #$20
        .a8
        lda $3EC8               ; Force Field: blocked elements (bit set = nullified for everyone)
        and f:XHYBEL
        bne @zero
        lda $3BCC,y             ; absorb
        and f:XHYBEL
        bne @abs
        lda $3BCD,y             ; null
        and f:XHYBEL
        bne @zero
        lda $3BE1,y             ; half
        and f:XHYBEL
        bne @half
        lda $3BE0,y             ; weak
        and f:XHYBEL
        bne @weak
        rep #$20
        .a16
        bra @sum
        .a8
@zero:  rep #$20
        .a16
        lda #$0000
        sta 3,s
        bra @sum
        .a8
@half:  rep #$20
        .a16
        lda 3,s
        lsr a
        sta 3,s
        bra @sum
        .a8
@weak:  rep #$20
        .a16
        lda 3,s
        asl a
        sta 3,s
@sum:   lda 1,s
        clc
        adc 3,s
        sta $F0
        bra @done
        .a8
@abs:   rep #$20
        .a16
        lda 1,s
        sec
        sbc 3,s
        bcs @pos
        eor #$FFFF
        inc a
        sta $F0
        sep #$20
        .a8
        lda $F2
        eor #$01
        sta $F2
        rep #$20
        .a16
        bra @done
@pos:   sta $F0
@done:  pla
        pla
        rts

; XC3_FixPowF (far; C3:8CD1 via XJ_FixPow; A8 = power byte, X16 = 9-bit id * 30): replaces STA $B2 / STZ $B3.
; zb2 := power, or XFixAmt of an extended record when defined. A, X, P kept.
        .a8
        .i16
XC3_FixPowF:
        sta $B2
        stz $B3
        php
        rep #$30
        .a16
        pha
        phx
        txa
        sec
        sbc #$1E00              ; $100 * 30
        bcc @done
        ldx #$0000
@div:   cmp #30
        bcc @q
        sbc #30
        inx
        bra @div
@q:     txa
        and #$003F
        asl a
        tax
        lda f:XFixAmt,x
        beq @done
        sta $B2
@done:  plx
        pla
        plp
        rtl

; XShopCapA (far; A8 = low byte of the current shop entry, XSHOPCURHI = its high bit): A8 := purchase cap
; (XShopCap of an extended entry, else 99). X, P kept; B destroyed.
        .a8
XShopCapA:
        php
        rep #$30
        .a16
        phx
        and #$003F
        tax
        sep #$20
        .a8
        lda f:XSHOPCURHI
        beq @d
        lda f:XShopCap,x
        bne @r
@d:     lda #$63
@r:     plx
        plp
        rtl

; ===========================================================================
; same-bank stubs
; ===========================================================================
.section XC2 $C26470
        .a8
        .i8
; C2:0BD3 CalcTargetDmg: replaces LDA $11A1
XC2_ElemA:
        jsl XJ_ElemA
        rts

; C2:4418 MagicStatusEffect: replaces LDA $B3 / BMI +4 / LDA #$10 / TRB $F4 (cancel a Vanish removal unless zb3
; bit7): the removal is also kept for an extended consumable whose record removes Vanish (XVANOK). A destroyed.
XC2_VanTrb:
        lda $B3
        bmi @r
        lda f:XVANOK
        bne @r
        lda #$10
        trb $F4
@r:     rts

.section XC3 $C3F0A0
        .a8
        .i16
; C3:B836 _c3b82f: replaces LDA #$63 / SEC: A = purchase cap of the current entry, C = 1
XC3_ShopCap:
        jsr ShopCurItem
        jsl XJ_ShopCap
        sec
        rts

; C3:B83E _b83e: replaces LDA $69 / CMP #$63 (+ NOP): C = (owned >= cap); A = cap (unused by the vanilla code)
XC3_ShopTooMany:
        jsr ShopCurItem
        jsl XJ_ShopCap
        pha
        lda $69
        cmp 1,s
        pla
        rts
