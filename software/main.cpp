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

/*int test_local_pointer()
{
unsigned int b = 3;
unsigned int* p = &b;
//return *p;
//return 0;
}*/

asm(".section .progmem.data");
asm(".globl _start");
asm(".type _start,@function");
asm("_start:");
asm("inc r0");
asm("inc r0");
asm("xor r0");
/*asm("smsk");
asm("sta r0 0x1100");
asm("ldi r0 0x48");
asm("sta r0 0x2400");
asm("ldi r0 0x45");
asm("sta r0 0x2400");
asm("ldi r0 0x59");
asm("sta r0 0x2400");
asm("ldi r0 0x0A");*/
asm("ldi r0, 0xfc");
asm("sta r0, 0xfa0");
asm("ldi r0, 0x0f");
asm("sta r0, 0xfa1");
//asm("jsr _labe1");
asm("ldi r0 0x0F");
asm("sta r0 0x2000");
asm("jmp main");
asm("_labe1:");
asm("ldi r0 0xF0");
asm("sta r0 0x2000");
//asm("rts");
/*asm("ldi r0 0x0F");
asm("sta r0 0x2000");*/
asm("ldi r0, 0xf0");
asm("sta r0, 0x2000");
asm("jmp main");
asm("jmp main");
asm("jmp main");
asm("jmp main");

void delay(){
	char a = 0;
	for(unsigned int i = 0; i>200; i++)
	{
		for(unsigned int j = 0; j>200; j++)
		{
				a = a + 1;
		}
	}	
}
int main()
{
//char led = 1;
char read;
char a;
//unsigned int b = 200;
while(1){
	read = *(char*)DSW_Address;
	*(char*)LED_Address = read + 1;
	
	/**(char*)LED_Address = 1;
	delay();*/
	/*for(unsigned int i = 0; i>200; i++)
	{
		for(unsigned int j = 0; j>200; j++)
		{
				a = a + 1;
		}
	}*/
	/**(char*)LED_Address = 0;
	delay();*/
	//delay();	
	//*(char*)LED_Address = 1;	
	//delay();	
}
	return 0;
}
