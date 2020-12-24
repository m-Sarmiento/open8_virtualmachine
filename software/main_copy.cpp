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
// check br instruction
/*asm("ldi r2 0x42");
asm("psh r2");
asm("pop r3");
asm("sta r3 0x2400");*/
/*asm("stp 0");
asm("br1 0 5");
asm("inc r0");
asm("inc r1");
asm("inc r2");
asm("inc r3");
asm("inc r4");
asm("inc r5");
asm("inc r6");
asm("inc r7");*/
//chech all instructions
/*asm("inc r1");
asm("adc r2");
asm("tx0 r3");
asm("or r4");
asm("and r5");
asm("xor r6");
asm("rol r7");
asm("ror r6");
asm("dec r5");
asm("sbc r4");
asm("add r3");
asm("stp 3");
asm("btt 5");
asm("clp 3");
asm("tx0 r2");
asm("cmp r1");
asm("psh r3");
asm("pop r4");
asm("br0 2 5");
asm("br1 2 4");
asm("dbnz r4 4");*/
//asm("int 3");
//asm("rti");


asm("smsk");
/*asm("sta r0 0x1100");
asm("ldi r0 0x48");
asm("sta r0 0x2400");
asm("ldi r0 0x45");
asm("sta r0 0x2400");
asm("ldi r0 0x59");
asm("sta r0 0x2400");
asm("ldi r0 0x0A");
asm("ldi r0, 0xfc");
asm("sta r0, 0xfa0");
asm("ldi r0, 0x0f");
asm("sta r0, 0xfa1");*/
/*asm("jsr _labe1");
asm("ldi r0 0x0F");
asm("sta r0 0x2000");*/

asm("ldi r0, 0xfc");
asm("sta r0, 0x0fa0");
asm("ldi r0, 0x0f");
asm("sta r0, 0x0fa1");
asm("jmp main");
/*asm("_labe1:");
asm("psh r0");
asm("psh r0");
asm("pop r0");
asm("pop r0");
asm("rts");
asm("ldi r0 0x0F");
asm("sta r0 0x2000");
asm("ldi r0, 0xf0");
asm("sta r0, 0x2000");

asm("jmp main");
asm("jmp main");
asm("jmp main");
asm("jmp main");*/

/*void puts(char a){
	*(char*)SER_Address = a;
}*/

/*void print_string(const char *str)
{
const char *p;
for (p = str; *p != '\0'; p++)
puts(*p);
puts(*p);
puts('\n');
return;
}*/

/*char popt(){
	return *(char*)SER_Address;
}*/

/*int factorial(int n) {
   //base case
   if(n == 0) {
      return 1;
   } else {
      return n * factorial(n-1);
   }
}*/

/*void delay(){
	char a =0;
	for(char i = 0; i>2; i++){
		for(char j = 0; j>200; j++){
				a = a + 1;
		}
	}
}*/

int main()
{
//char led = 1;
//char read;
//char a;
const char str[]="you\n";
//unsigned int b = 200;
*(char*)SER_Address = '\n';
	for (char i = 0; i!=1; i++){
		*(char*)SER_Address = i+33;
		*(char*)SER_Address = str[i];
	}
while(1){

	/**(char*)SER_Address = str[0];
	*(char*)SER_Address = str[1];
	*(char*)SER_Address = str[2];
	*(char*)SER_Address = str[3];*/

	//delay();
	//read = *(char*)DSW_Address;
	//*(char*)LED_Address = read + 1;
	//for (unsigned int i = 0; i>4; i++){
	
	//read = popt();
	//print_string(str);
	


	
	/*puts('M');
	delay();
	puts('A');
	delay();
	puts('R');
	delay();
	puts('C');
	delay();
	puts('O');
	delay();
	puts('\n');
	delay();*/
	// }
	
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
