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

asm(".section .progmem.data");
asm(".globl _start");
asm(".type _start,@function");
asm("_start:");
asm("inc r0");
asm("inc r0");
asm("xor r0");
asm("jmp main");
/*asm("br1 0 5");
asm("br1 1 5");
asm("br1 2 5");
asm("br1 3 5");
asm("br0 0 5");
asm("br0 1 5");
asm("br0 2 5");
asm("br0 3 5");*/
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

#define INT_DIGITS 19		/* enough for 64 bit integer */

/*char *itoa(int i)
{
  // Room for INT_DIGITS digits, - and '\0' 
  static char buf[INT_DIGITS + 2];
  char *p = buf + INT_DIGITS + 1;	//points to terminating '\0' 
  if (i >= 0) {
    do {
      *--p = '0' + (i % 10);
      i /= 10;
    } while (i != 0);
    return p;
  }
  else {			// i < 0 
    do {
      *--p = '0' - (i % 10);
      i /= 10;
    } while (i != 0);
    *--p = '-';
  }
  return p;
}*/

char factorial(char n) {
   //base case
   if(n == 0) {
      return 1;
   } else {
      return n * factorial(n-1);
   }
}

void puts(char n) {
   *(char*)SER_Address = n;
}

void print_string(const char *str){
  const char *p;
  for (p = str; *p != '\0'; p++)
	puts(*p);
	puts(*p);
	puts('\n');
  return;
}

void print_hex(int num){
	int a = num & 0x0F;
	if (a > 9){
		a = a+55;
	}else{
		a = a + 48;
	}
	puts((char)a);
}

int main()
{
	/*int x = 257;
	int y = 87;
	y += x;*/
	
//char x = 2;
char k = 'A';
char* p;
int a[3] = {1,2,3};
p=&k;
char j = 4 % 3;
char y;
//long yy = 0x41FFFFFE;
//float num = 1.5;
int hh = 90; 
int nmr = 0xFA;
char kk = '0'; 
char str[]="hello world!\n";
*(char*)SER_Address = '\n';
	for (int i = 0; i<-5; i--){
		//y = factorial(i);
		//y = i%2;
		//yy = yy + 1;
		//num = num + 31.5;
		//*(char*)SER_Address = (char)(yy>>24);
		puts(':');
		//*(char*)SER_Address = str[i];
		//*(char*)SER_Address = str[i];
		//puts((char)(y+33));
		//print_hex(nmr);
		//hh--;
	}

	print_string(str);
	*(char*)SER_Address = '_';
	print_hex(nmr);
	*(char*)SER_Address = '\n';
while(1){
	y =*(char*)SER_Address;
	//puts(y);
	//if (y == 65){
	//	puts('Z');
	//}
}
	return 0;
}
