#define RAM_Address              0x0000 //System RAM
#define ALU_Address              0x1000 //ALU16 coprocessor
#define RTC_Address              0x1100 //System Timer / RT Clock
#define ETC_Address              0x1200 //Epoch Timer/Alarm Clock
#define TMR_Address              0x1400 //PIT timer
#define SDLC_Address             0x1800 //LCD serial interface
#define LED_Address              0x2000 //LED Display
#define DSW_Address              0x2100 //Dip Switches
#define BTN_Address              0x2200 //Push Buttons
#define SER_Address              0x2400 //UART interface
#define MAX_Address              0x2800 //Max 7221 base address
#define VEC_Address              0x3000 //Vector RX base address
#define CHR_Address              0x3100 //Elapsed Time / Chronometer
#define ROM_Address              0x8000 //Application ROM
#define ISR_Start_Addr           0xFFF0 //ISR Vector Table

/*asm(".section .progmem.data");
asm(".globl _start");
asm(".type _start,@function");
asm("_start:");
asm("inc r0");
asm("inc r0");
asm("xor r0");
asm("ldi r0, 0xfc");
asm("sta r0, 0xfa0");
asm("ldi r0, 0x0f");
asm("sta r0, 0xfa1");
asm("jmp main");*/
/*asm(".section .progmem.data");
asm(".globl _start");
asm(".type _start,@function");
asm("_start:");
asm("ldi r2 0xff");
asm("tx0 r2");
asm("t0x r0");
asm("clc");
asm("rol r0");
asm("sbc r0");
asm("t0x r3");*/

/*char factorial(char n) {
   //base case
   if(n == 0) {
      return 1;
   } else {
      return n * factorial(n-1);
   }
}*/

int main()
{
char x = 2;
char y;
const char str[]="hello world!\n";
//*(char*)SER_Address = '\n';
	for (char i = 0; i<33; i++){
		//y = x * i;
		//*(char*)SER_Address = i;
		*(char*)SER_Address = i+33;
		//*(char*)SER_Address = str[i];
	}
while(1){}
	return 0;
}
