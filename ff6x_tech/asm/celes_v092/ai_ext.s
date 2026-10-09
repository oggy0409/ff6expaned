; =============================================================================
; FF6 Expanded Edition - TECH v0.9.2 - Celes enablers E2-E4: battle AI extension (QA target only)
; =============================================================================
; The vanilla AI interpreter has no bounds check on its condition ($FC) and misc-effect ($FB) indices. Two hooks route
; indices >= $40 to the routines below; every index < $40 takes the exact vanilla path (same table, same registers).
;
;   C2:1A91  AI command $FC (condition) dispatch    LDA $3A2D / ASL / TAX / JSR ($1D55,X)  -> JSR XE2_Cond (+NOP)
;   C2:1E5E  battle command $30 (AI $FB) dispatch   LDA $B6 / ASL / TAX / LDA $B8 / JMP ($1F09,X) -> JMP XE2_Misc
;
; Extension conditions (FC cc p1 p2; Y = the monster running the script; C = result):
;   $40 HP_PCT_LE       own current HP <= p1 % of own max HP (p1 1..100; exact integer arithmetic, 16-bit HP)
;   $41 LIGHTNING_COUNT p1 = element mask, p2 = field turns. If the last action that hit the monster carried an element
;                       of p1 (vanilla IF_ELEMENT $04, called unchanged) and the Grounding Field is down, the hit is
;                       counted (battle var 0); the 3rd counted hit resets the count, makes the element NULL and not
;                       weak for the monster (battle RAM $3BCD,y / $3BE0,y) and sets battle var 1 = p2 field turns.
;                       Always returns false (pure bookkeeping inside the counter script: no action is queued).
; Extension misc effects (FB ss p; executed as battle command $30 in the monster's queued action):
;   $42 OVERLOAD        Defense ($3BB8,y) := p; the monster's sprite palette (battle palette buffer $7E7F00 + slot*32,
;                       slot from C1 $80DB) := XE_OverloadPal (placeholder overload colours, D-14). HP untouched.
;   $43 GROUNDING_TICK  p = element mask. If battle var 1 > 0: var1 -= 1; reaching 0 restores the element weakness
;                       and removes the null (the Praetor's locked reactions: weak Lightning, Lightning not null).
; Battle vars 0-2 ($3EB0-$3EB2) are PER-BATTLE: zeroed at every battle start (InitBattle C2:23ED, wInitZeroBlock1)
; and never saved. (Vars 4-23 are the GLOBAL battle variables: restored from / saved to SRAM $1DC9-$1DDC at battle
; start / end - never used here.) Nothing here writes outside battle RAM: nothing persists after the battle.

VAR_LCOUNT  = $3EB0             ; battle var 0 (per battle)
VAR_GTURNS  = $3EB1             ; battle var 1 (per battle)
ELEM_NULL   = $3BCD
ELEM_WEAK   = $3BE0
DEFENSE     = $3BB8
CUR_HP      = $3BF4
MAX_HP      = $3C1C
AIP1        = $3A2E
AIP2        = $3A2F
MON_PALIDX  = $80DB             ; C1 LoadMonsterPal: per monster slot (x2) palette slot * 2
SPR_PALBUF  = $7F00             ; w7e7e00::_8 (sprite palettes, uploaded to CGRAM every NMI)
hWRDIVL     = $004204
hWRDIVB     = $004206
hRDDIVL     = $004214

.section XE_F0 $F04000
        .a8
        .i8
; XE_CondExt (far; A8 I8, A = condition index >= $40 except $41, Y = monster): C = result. X destroyed.
XE_CondExt:
        cmp #$40
        beq HpPct
        clc
        rtl

HpPct:
        php
        rep #$30
        .a16
        .i16
        phx
        phy
        tya
        and #$00FF
        tay
        lda MAX_HP,y            ; threshold = (max / 100) * p + ((max % 100) * p) / 100
        sta f:hWRDIVL
        sep #$20
        .a8
        lda #100
        sta f:hWRDIVB
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        rep #$20
        .a16
        lda f:hRDDIVL+2         ; remainder
        pha
        lda f:hRDDIVL           ; quotient
        pha                     ; Q 1,s / R 3,s
        lda AIP1
        and #$00FF
        tax
        lda #$0000
@m1:    cpx #$0000
        beq @m1d
        clc
        adc 1,s
        dex
        bra @m1
@m1d:   sta 1,s                 ; Q * p
        lda AIP1
        and #$00FF
        tax
        lda #$0000
@m2:    cpx #$0000
        beq @m2d
        clc
        adc 3,s
        dex
        bra @m2
@m2d:   sta f:hWRDIVL           ; R * p (<= 9900)
        sep #$20
        .a8
        lda #100
        sta f:hWRDIVB
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        rep #$20
        .a16
        lda f:hRDDIVL
        clc
        adc 1,s                 ; threshold
        cmp CUR_HP,y            ; C = threshold >= HP
        pla
        pla
        ply
        plx
        bcs @t
        plp
        clc
        rtl
@t:     plp
        sec
        rtl

        .a8
        .i8
; XE_LightCount (far; A8 I8; C = vanilla IF_ELEMENT result for the element mask in $3A2E; Y = monster): see header.
XE_LightCount:
        bcc @no
        lda VAR_GTURNS
        bne @no                 ; field up: Lightning is null, the hit does not count
        lda VAR_LCOUNT
        inc a
        sta VAR_LCOUNT
        cmp #3
        bcc @no
        lda #$00
        sta VAR_LCOUNT
        lda AIP1
        eor #$FF
        and ELEM_WEAK,y
        sta ELEM_WEAK,y
        lda AIP1
        ora ELEM_NULL,y
        sta ELEM_NULL,y
        lda AIP2
        sta VAR_GTURNS
@no:    clc
        rtl

; XE_MiscExt (far; A8 I8, A = misc effect index >= $40, $B8 = parameter, Y = monster): see header.
XE_MiscExt:
        cmp #$42
        beq Overload
        cmp #$43
        beq GTick
        rtl

Overload:
        lda $B8
        sta DEFENSE,y
        php
        rep #$30
        .a16
        .i16
        phx
        phy
        tya
        and #$00FF
        sec
        sbc #$0008              ; monster slot * 2
        tax
        lda MON_PALIDX,x
        and #$0006              ; palette slot * 2 (0, 2, 4)
        asl a
        asl a
        asl a
        asl a                   ; * 16 = slot * 32
        tay
        ldx #$0000
@cp:    lda f:XE_OverloadPal,x
        sta SPR_PALBUF,y
        iny
        iny
        inx
        inx
        cpx #$0020
        bne @cp
        ply
        plx
        plp
        rtl

        .a8
        .i8
GTick:
        lda VAR_GTURNS
        beq @r
        dec a
        sta VAR_GTURNS
        bne @r
        lda $B8
        ora ELEM_WEAK,y
        sta ELEM_WEAK,y
        lda $B8
        eor #$FF
        and ELEM_NULL,y
        sta ELEM_NULL,y
@r:     rtl

; ===========================================================================
; bank C2 stubs (ITEMX_C2_STUBS claim, C2:6780-C2:67FF, after the item engine stubs)
; ===========================================================================
.section XE_C2 $C26780
        .a8
        .i8
; C2:1A91: replaces LDA $3A2D / ASL / TAX / JSR ($1D55,X); returns to C2:1A94 (NOPs) -> BCS DoNextAICmd
XE2_Cond:
        lda $3A2D
        cmp #$40
        bcs @ext
        asl a
        tax
        jmp ($1D55,x)           ; vanilla AICondTbl; the condition's RTS returns to the hook site
@ext:   cmp #$41
        beq @lc
        jsl XE_CondExt
        rts
@lc:    phy
        clc                     ; (vanilla dispatch reaches IF_ELEMENT with C = 0: TYA / ADC #21)
        jsr $1C5E               ; vanilla AI_COND IF_ELEMENT (unchanged): C = hit by an element of $3A2E
        sep #$20                ; its success path returns with A16 (LONGA at C2:1C55)
        ply
        jsl XE_LightCount
        rts

; C2:1E5E (battle command $30 = AI $FB): replaces LDA $B6 / ASL / TAX / LDA $B8 / JMP ($1F09,X)
XE2_Misc:
        lda $B6
        cmp #$40
        bcs @ext
        asl a
        tax
        lda $B8
        jmp ($1F09,x)           ; vanilla MiscAIEffectTbl
@ext:   jsl XE_MiscExt
        rts
