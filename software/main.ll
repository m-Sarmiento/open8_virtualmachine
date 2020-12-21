; ModuleID = 'main.bc'
source_filename = "main.cpp"
target datalayout = "e-P1-p:16:8-i8:8-i16:8-i32:8-i64:8-f32:8-f64:8-n8-a:8"
target triple = "avr"

module asm ".section .progmem.data"
module asm ".globl _start"
module asm ".type _start,@function"
module asm "_start:"
module asm "inc r0"
module asm "inc r0"
module asm "xor r0"
module asm "ldi r0, 0xfc"
module asm "sta r0, 0xfa0"
module asm "ldi r0, 0x0f"
module asm "sta r0, 0xfa1"
module asm "ldi r0 0x0F"
module asm "sta r0 0x2000"
module asm "jmp main"
module asm "_labe1:"
module asm "ldi r0 0xF0"
module asm "sta r0 0x2000"
module asm "ldi r0, 0xf0"
module asm "sta r0, 0x2000"
module asm "jmp main"
module asm "jmp main"
module asm "jmp main"
module asm "jmp main"

; Function Attrs: noinline nounwind optnone
define dso_local void @_Z5delayv() #0 {
  %1 = alloca i8, align 1
  %2 = alloca i16, align 1
  %3 = alloca i16, align 1
  store i8 0, i8* %1, align 1
  store i16 0, i16* %2, align 1
  br label %4

; <label>:4:                                      ; preds = %20, %0
  %5 = load i16, i16* %2, align 1
  %6 = icmp ugt i16 %5, 200
  br i1 %6, label %7, label %23

; <label>:7:                                      ; preds = %4
  store i16 0, i16* %3, align 1
  br label %8

; <label>:8:                                      ; preds = %16, %7
  %9 = load i16, i16* %3, align 1
  %10 = icmp ugt i16 %9, 200
  br i1 %10, label %11, label %19

; <label>:11:                                     ; preds = %8
  %12 = load i8, i8* %1, align 1
  %13 = sext i8 %12 to i16
  %14 = add nsw i16 %13, 1
  %15 = trunc i16 %14 to i8
  store i8 %15, i8* %1, align 1
  br label %16

; <label>:16:                                     ; preds = %11
  %17 = load i16, i16* %3, align 1
  %18 = add i16 %17, 1
  store i16 %18, i16* %3, align 1
  br label %8

; <label>:19:                                     ; preds = %8
  br label %20

; <label>:20:                                     ; preds = %19
  %21 = load i16, i16* %2, align 1
  %22 = add i16 %21, 1
  store i16 %22, i16* %2, align 1
  br label %4

; <label>:23:                                     ; preds = %4
  ret void
}

; Function Attrs: noinline norecurse nounwind optnone
define dso_local i16 @main() #1 {
  %1 = alloca i16, align 1
  %2 = alloca i8, align 1
  %3 = alloca i8, align 1
  store i16 0, i16* %1, align 1
  br label %4

; <label>:4:                                      ; preds = %0, %4
  %5 = load i8, i8* inttoptr (i16 8448 to i8*), align 1
  store i8 %5, i8* %2, align 1
  %6 = load i8, i8* %2, align 1
  %7 = sext i8 %6 to i16
  %8 = add nsw i16 %7, 1
  %9 = trunc i16 %8 to i8
  store i8 %9, i8* inttoptr (i16 8192 to i8*), align 1
  br label %4
                                                  ; No predecessors!
  %11 = load i16, i16* %1, align 1
  ret i16 %11
}

attributes #0 = { noinline nounwind optnone "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-jump-tables"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #1 = { noinline norecurse nounwind optnone "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-jump-tables"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "unsafe-fp-math"="false" "use-soft-float"="false" }

!llvm.module.flags = !{!0}
!llvm.ident = !{!1}

!0 = !{i32 1, !"wchar_size", i32 2}
!1 = !{!"clang version 7.0.1-8+deb10u2 (tags/RELEASE_701/final)"}
