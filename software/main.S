	.text
	.file	"main.cpp"
                                        ; Start of file scope inline assembly
	.section	.progmem.data,"a",@progbits
	.globl	_start
	.type	_start,@function
_start:
	inc	r0
	inc	r0
	clr
	ldi	r0, 252
	sta	r0, 4000
	ldi	r0, 15
	sta	r0, 4001
	ldi	r0, 15
	sta	r0, 8192
	jmp	main
_labe1:
	ldi	r0, 240
	sta	r0, 8192
	ldi	r0, 240
	sta	r0, 8192
	jmp	main
	jmp	main
	jmp	main
	jmp	main

                                        ; End of file scope inline assembly
	.globl	_Z5delayv               ; -- Begin function _Z5delayv
	.p2align	1
	.type	_Z5delayv,@function
_Z5delayv:                              ; @_Z5delayv
; %bb.0:
	psh	r6
	psh	r7
	lda	r6, 4000
	lda	r7, 4001
	ldi	r2, 5
	ldi	r3, 0
	tx0	r6
	clc
	sbc	r2
	t0x	r6
	lda	r0, 4002
	cli
	sta	r7, 4001
	sta	r0, 4002
	sta	r6, 4000
	ldi	r5, 0
	tx0	r5
	sto	r6, 5
	ldi	r4, 0
	ldi	r5, 0
	tx0	r4
	sto	r6, 3
	tx0	r5
	sto	r6, 4
	jmp	LBB0_1
LBB0_1:                                 ; =>This Loop Header: Depth=1
                                        ;     Child Loop BB0_3 Depth 2
	ldo	r6, 3
	t0x	r4
	ldo	r6, 4
	t0x	r5
	ldi	r2, 201
	ldi	r3, 0
	tx0	r2
	cmp	r4
	tx0	r3
	cmp	r5
	brc	LBB0_8
	jmp	LBB0_2
LBB0_2:                                 ;   in Loop: Header=BB0_1 Depth=1
	ldi	r4, 0
	ldi	r5, 0
	tx0	r4
	sto	r6, 1
	tx0	r5
	sto	r6, 2
	jmp	LBB0_3
LBB0_3:                                 ;   Parent Loop BB0_1 Depth=1
                                        ; =>  This Inner Loop Header: Depth=2
	ldo	r6, 1
	t0x	r4
	ldo	r6, 2
	t0x	r5
	ldi	r2, 201
	ldi	r3, 0
	tx0	r2
	cmp	r4
	tx0	r3
	cmp	r5
	brc	LBB0_6
	jmp	LBB0_4
LBB0_4:                                 ;   in Loop: Header=BB0_3 Depth=2
	ldo	r6, 5
	t0x	r5
	inc	r5
	tx0	r5
	sto	r6, 5
	jmp	LBB0_5
LBB0_5:                                 ;   in Loop: Header=BB0_3 Depth=2
	ldo	r6, 1
	t0x	r4
	ldo	r6, 2
	t0x	r5
	ldi	r2, 1
	ldi	r3, 0
	tx0	r4
	add	r2
	t0x	r4
	tx0	r5
	adc	r3
	t0x	r5
	tx0	r4
	sto	r6, 1
	tx0	r5
	sto	r6, 2
	jmp	LBB0_3
LBB0_6:                                 ;   in Loop: Header=BB0_1 Depth=1
	jmp	LBB0_7
LBB0_7:                                 ;   in Loop: Header=BB0_1 Depth=1
	ldo	r6, 3
	t0x	r4
	ldo	r6, 4
	t0x	r5
	ldi	r2, 1
	ldi	r3, 0
	tx0	r4
	add	r2
	t0x	r4
	tx0	r5
	adc	r3
	t0x	r5
	tx0	r4
	sto	r6, 3
	tx0	r5
	sto	r6, 4
	jmp	LBB0_1
LBB0_8:
	ldi	r0, 5
	ldi	r1, 0
	tx0	r6
	add	r0
	t0x	r6
	tx0	r7
	adc	r1
	t0x	r7
	lda	r0, 4002
	cli
	sta	r7, 4001
	sta	r0, 4002
	sta	r6, 4000
	pop	r7
	pop	r6
	rts
.Lfunc_end0:
	.size	_Z5delayv, .Lfunc_end0-_Z5delayv
                                        ; -- End function
	.globl	main                    ; -- Begin function main
	.p2align	1
	.type	main,@function
main:                                   ; @main
; %bb.0:
	psh	r6
	psh	r7
	lda	r6, 4000
	lda	r7, 4001
	ldi	r2, 4
	ldi	r3, 0
	tx0	r6
	clc
	sbc	r2
	t0x	r6
	lda	r0, 4002
	cli
	sta	r7, 4001
	sta	r0, 4002
	sta	r6, 4000
	ldi	r4, 0
	ldi	r5, 0
	tx0	r4
	sto	r6, 3
	tx0	r5
	sto	r6, 4
	jmp	LBB1_1
LBB1_1:                                 ; =>This Inner Loop Header: Depth=1
	lda	r5, 8448
	tx0	r5
	sto	r6, 2
	ldo	r6, 2
	t0x	r5
	inc	r5
	sta	r5, 8192
	jmp	LBB1_1
.Lfunc_end1:
	.size	main, .Lfunc_end1-main
                                        ; -- End function
	; Declaring this symbol tells the CRT that it should
	;copy all variables from program memory to RAM on startup
	.globl	__do_copy_data
	; Declaring this symbol tells the CRT that it should
	;clear the zeroed data section on startup
	.globl	__do_clear_bss
