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

int __divsi3(int a, int b) {
  const int bits_in_word_m1 = (int)(sizeof(int) * 8) - 1;
  int s_a = a >> bits_in_word_m1; // s_a = a < 0 ? -1 : 0
  int s_b = b >> bits_in_word_m1; // s_b = b < 0 ? -1 : 0
  a = (a ^ s_a) - s_a;               // negate if s_a == -1
  b = (b ^ s_b) - s_b;               // negate if s_b == -1
  s_a ^= s_b;                        // sign of quotient
  //
  // On CPUs without unsigned hardware division support,
  //  this calls __udivsi3 (notice the cast to su_int).
  // On CPUs with unsigned hardware division support,
  //  this uses the unsigned division instruction.
  //
  return ((int)a / (int)b ^ s_a) - s_a; // negate if s_a == -1
}

int __divmodsi4(int a, int b, int *rem) {
  int d = __divsi3(a, b);
  *rem = a - (d * b);
  return d;
}
// unsigned int b = 11;
int test_mult(){
	int b = 11;
	b = (b+1)%12;
	return b;
}
