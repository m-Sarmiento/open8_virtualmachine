#!/usr/bin/env python3
"""
Implementation of virtual machine for open8 assembly language in python
"""

__version__ = '1.0'

import array
import select
import sys
import termios
import tty
import time


UINT16_MAX = 2 ** 8
PC_START = 0x0000
DEBUG = True
is_running = 1
memory = None


def getchar():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    if ord(ch) == 3:
        # h&le keyboard interrupt
        exit(130)
    return ch

def set_bit(value, bit):
    return value | (1<<bit)

def clear_bit(value, bit):
    return value & ~(1<<bit)

class R:
    """Regisers"""
    R0          = 0
    R1          = 1
    R2          = 2
    R3          = 3
    R4          = 4
    R5          = 5
    R6          = 6
    R7          = 7
    PSR         = 8  # program status register
    STACK       = 9  # stack pointer register
    PC          = 10 # PROGRAM_COUNTER pointer to the currently executing instruction
    VECTOR_BASE = 11 # The implementation specific location of the interrupt vectors
    INTERRUPT_MASK_REGISTER = 12


class register_dict(dict):

    def __setitem__(self, key, value):
        super().__setitem__(key, value % UINT16_MAX)


reg = register_dict({i: 0 for i in range(R.INTERRUPT_MASK_REGISTER)})


class OP:
    """opcode"""
    INC = 0
    ADC = 1
    TX0 = 2
    OR  = 3
    AND = 4
    XOR = 5
    ROL = 6
    ROR = 7
    DEC = 8
    SBC = 9
    ADD = 10
    STP = 11
    BTT = 12
    CLP = 13
    T0X = 14
    CMP = 15
    PSH = 16
    POP = 17
    BR0 = 18
    BR1 = 19
    DBNZ= 20
    INT = 21
    MUL = 22
    SPECIAL = 23
    UPP = 24
    STA = 25
    STX = 26
    STO = 27
    LDI = 28
    LDA = 29
    LDO = 30
    LDX = 31

class FL:
    """flags"""
    ZRO = 1 << 0  # Zero flag
    CRY = 1 << 1  # Carry flag
    NEG = 1 << 2  # Negative flag
    INT = 1 << 3  # Interrupt enable


"""
OPs implementaion
"""


def bad_opcode(op):
    raise Exception(f'Bad opcode: {op}')


def inc(instr):
    # destination register
    rn = (instr) & 0x7
    reg[rn] = reg[rn] + 1
    update_flags_012(rn)
    reg[rn] = reg[rn] & 0xFF
    if (DEBUG == True):
        print( "inc " +"r"+str(rn)  )

def adc(instr):
    # destination register
    rn = (instr) & 0x7
    reg[0] = reg[0] + reg[rn] + ((reg[R.PSR] >> 1) & 0x1)
    update_flags_012(0)
    reg[0] = reg[rn] & 0xFF
    if (DEBUG == True):
        print( "adc " +"r"+str(rn)  )

def tx0(instr):
    # destination register
    rn = (instr) & 0x7
    reg[0] = reg[rn] 
    update_flags_02(0)
    reg[0] = reg[rn] & 0xFF
    if (DEBUG == True):
        print( "tx0 " +"r"+str(rn)  )

def or_(instr):
    # destination register
    rn = (instr) & 0x7
    reg[0] = reg[rn] | reg[0]
    update_flags_02(0)
    reg[0] = reg[rn] & 0xFF
    if (DEBUG == True):
        print( "or  " +"r"+str(rn)  )

def and_(instr):
    # destination register
    rn = (instr) & 0x7
    reg[0] = reg[rn] & reg[0]
    update_flags_02(0)
    reg[0] = reg[rn] & 0xFF
    if (DEBUG == True):
        print( "and " +"r"+str(rn)  )

def xor(instr):
    # destination register
    rn = (instr) & 0x7
    reg[0] = reg[rn] ^ reg[0]
    update_flags_02(0)
    reg[0] = reg[rn] & 0xFF
    if (DEBUG == True):
        print( "xor " +"r"+str(rn)  )

def rol(instr):
    # destination register
    rn = (instr) & 0x7
    tmp = (reg[rn] >> 7) & 0x1
    reg[rn] = (reg[rn] <<  1) | ((reg[R.PSR] >> 1) & 0x1)
    update_flags_02(rn)
    if (tmp):
        reg[R.PSR] |=  FL.CRY
    else:
        reg[R.PSR] = reg[R.PSR]  & ~FL.CRY
    reg[rn] = reg[rn] &  0xFF
    if (DEBUG == True):
        print( "rol " +"r"+str(rn)  )



def ror(instr):
    # destination register
    rn = (instr) & 0x7
    tmp = reg[rn] & 0x1
    reg[rn] = (reg[rn] >>  1) | ((reg[R.PSR] << 7) & 0xFF) 
    update_flags_02(0)
    if (tmp):
        reg[R.PSR] |=  FL.CRY
    else:
        reg[R.PSR] = reg[R.PSR] & ~FL.CRY
    reg[rn] = reg[rn] &  0xFF
    if (DEBUG == True):
        print( "ror " +"r"+str(rn)  )

def dec(instr):
    # destination register
    rn = (instr) & 0x7
    reg[rn] = reg[rn] + 0xFF
    update_flags_012(rn)
    reg[rn] = reg[rn] &  0xFF
    if (DEBUG == True):
        print( "dec " +"r"+str(rn)  )

def sbc(instr):
    # destination register
    rn = (instr) & 0x7
    reg[0] = reg[0] + (-reg[rn]) + ((reg[R.PSR] >> 1) & 0x1) 
    update_flags_012(0)
    reg[0] = reg[0] & 0xFF
    if (DEBUG == True):
        print( "sbc " +"r"+str(rn)  )

def add(instr):
    # destination register
    rn = (instr) & 0x7
    reg[0] = reg[0] + reg[rn]
    update_flags_012(0)
    reg[0] = reg[0] & 0xFF
    if (DEBUG == True):
        print( "add " +"r"+str(rn)  )

def stp(instr):
    # destination register
    n = (instr) & 0x7
    reg[R.PSR] = reg[R.PSR] | ( 1 << n )
    if (DEBUG == True):
        print( "dont yet")

def btt(instr):
    # destination register
    n = (instr) & 0x7
    if ~((reg[0] >> n) & 0x1):
        reg[R.PSR] |=  FL.ZRO
    else:
        reg[R.PSR] = reg[R.PSR] & ~FL.ZRO
    if (reg[0] >> 7)  & 0x1:
        reg[R.PSR] |=  FL.NEG
    else:
        reg[R.PSR] = reg[R.PSR] & ~FL.NEG
    if (DEBUG == True):
        print( "dont yet")

def clp(instr):
    # destination register
    n = (instr) & 0x7
    reg[R.PSR] = reg[R.PSR] & ~( 1 << n )
    if (DEBUG == True):
        print( "dont yet")

def t0x(instr):
    # destination register
    rn = (instr) & 0x7
    reg[rn] = reg[0] 
    update_flags_02(rn)
    reg[0] = reg[R.PSR] & 0xFF
    if (DEBUG == True):
        print( "dont yet")

def cmp_(instr):
    # destination register
    rn = (instr) & 0x7
    tmp= reg[0] + (-reg[rn])
    if tmp == 0:
        reg[R.PSR] |=  FL.ZRO
    else:
        reg[R.PSR] = reg[R.PSR] & ~FL.ZRO
    if (tmp >> 8)  & 0x1:
        reg[R.PSR] |=  FL.CRY
    else:
        reg[R.PSR] = reg[R.PSR] & ~FL.CRY
    if (tmp >> 7)  & 0x1:
        reg[R.PSR] |=  FL.NEG
    else:
        reg[R.PSR] = reg[R.PSR] & ~FL.NEG
    if (DEBUG == True):
        print( "dont yet")

def psh(instr):
    rn = (instr) & 0x7
    mem_write(reg[R.STACK], reg[rn])
    reg[R.STACK] = reg[R.STACK] - 1
    if (DEBUG == True):
        print( "dont yet")

def pop(instr):
    rn = (instr) & 0x7
    reg[rn] = mem_read(reg[R.STACK])
    reg[R.STACK] = reg[R.STACK] + 1
    if (DEBUG == True):
        print( "dont yet")

def br0(instr):
    bit = (instr) & 0x7
    pc_offset = sign_extend((mem_read(reg[R.PC])) & 0xff, 8)
    if ((reg[R.PSR]>>bit) & 0x1) == 0:
        reg[R.PC] += pc_offset
    if (DEBUG == True):
        print( "dont yet")

def br1(instr):
    bit = (instr) & 0x7
    pc_offset = sign_extend((mem_read(reg[R.PC])) & 0xff, 8)
    if ((reg[R.PSR]>>bit) & 0x1) == 1:
        reg[R.PC] += pc_offset
    if (DEBUG == True):
        print( "dont yet")

def dbnz(instr):
    rn = (instr) & 0x7
    reg[rn] = reg[rn] + 0xFF
    update_flags_012(rn)
    reg[rn] = reg[rn] &  0xFF 
    pc_offset = sign_extend((mem_read(reg[R.PC])) & 0xff, 8)
    if ((reg[R.PSR]) & 0x1) == 1:
        reg[R.PC] += pc_offset
    if (DEBUG == True):
        print( "dont yet")

def int_(instr):
    n = (instr) & 0x7
    if (DEBUG == True):
        print( "dont yet")
    pass
    #if (n == 0) | ((((reg[R.PSR]>>3) & 0x1) == 1) & (((reg[R.INTERRUPT_MASK_REGISTER]>>n) & 0x1 )==1)):
    #    mem_write(reg[R.STACK],reg[R.PSR])
    #    reg[R.STACK] -= 1
    #    mem_write(reg[R.STACK],(reg[R.PC]>>8)&0xFF)
    #    reg[R.STACK] -= 1
    #    mem_write(reg[R.STACK],reg[R.PC]&0xFF)
    #    reg[R.STACK] -= 1
    #    hi8 = mem_read(reg[R.VECTOR_BASE]+(n*2)+1)
    #    lo8 = mem_read(reg[R.VECTOR_BASE]+(n*2))
    #    reg[R.PC] = (hi8 << 8) | lo8

def mul(instr):
    rn = (instr) & 0x7
    tmp = reg[rn] * reg[0]
    reg[R.R1] = (tmp >> 8 ) & 0xFF
    reg[R.R0] = (tmp ) & 0xFF
    if tmp == 0:
        reg[R.PSR] |=  FL.ZRO
    else:
        reg[R.PSR] = reg[R.PSR] & ~FL.ZRO
    if (DEBUG == True):
        print( "dont yet")

def special (instr):
    select = (instr) & 0x7
    if select == 0:
                    if (Allow_Stack_Address_Move):
                        reg[R.STACK] = reg[1] << 8 | reg[0]
                    else:
                        reg[R.STACK] = 0x007F
            #RTS
    elif select == 1:  
                    reg[R.PC] = (mem_read(reg[R.STACK]+1) << 8) | mem_read(reg[R.STACK])
                    reg[R.STACK] += 2
            #RTI
    elif select == 2: 
                    reg[R.PC] = (mem_read(reg[R.STACK]+1) << 8) | mem_read(reg[R.STACK])
                    reg[R.PSR] = mem_read(reg[R.STACK]+2)
                    reg[R.STACK] += 3
            #BRK
    elif select == 3: 
                    pass
            #JMP
    elif select == 4: 
                    hi8 = mem_read(reg[R.PC])
                    lo8 = mem_read(reg[R.PC]+1)
                    reg[R.PC] = (hi8 << 8) | lo8
                    if (DEBUG == True):
                        print( "dont yet")
            #SMSK
    elif select == 5: 
                    if (DEBUG == True):
                        print( "dont yet")
                    pass
            #GMSK
    elif select == 6: 
                    if (DEBUG == True):
                        print( "dont yet")
                    pass
            #JSR
    elif select == 7: 
                    tmp = reg[R.PC]+2
                    hi8 = mem_read(reg[R.PC])
                    lo8 = mem_read(reg[R.PC]+1)
                    mem_write(reg[R.STACK],(tmp >> 8) & 0xFF)
                    reg[R.STACK] -= 1
                    mem_write(reg[R.STACK],(tmp >> 8) & 0xFF)
                    reg[R.STACK] -= 1
                    reg[R.PC] = (hi8 << 8) | lo8
                    if (DEBUG == True):
                        print( "dont yet")
    else: 
                    pass

def upp(instr):
    rn = (instr) & 0x7
    tmp =(( reg[rn+1]<<8 ) | reg[rn]) + 1
    reg[rn+1] = (tmp >> 8) & 0xFF 
    reg[rn]   = (tmp >> 0) & 0xFF 
    if (tmp >> 16)  & 0x1:
        reg[R.PSR] |=  FL.CRY
    else:
        reg[R.PSR] = reg[R.PSR] & ~FL.CRY
    if (DEBUG == True):
        print( "dont yet")

def sta(instr):
    rn = (instr) & 0x7
    lo8 = mem_read(reg[R.PC])
    hi8 = mem_read(reg[R.PC]+1)
    addr = (hi8<<8) | lo8
    mem_write(addr,reg[rn])
    reg[R.PC] += 2
    if (DEBUG == True):
        print( "sta " +"r"+str(rn)+" "+str(addr)  )

def stx(instr):
    rn = (instr) & 0x6
    a = (instr) & 0x1
    hi8 = reg[rn+1]
    lo8 = reg[rn]
    addr = (hi8<<8) | lo8
    mem_write(addr,reg[R.R0])
    addr += a
    reg[rn+1] = (addr >> 8) & 0xFF
    reg[rn] = addr & 0xFF
    if (DEBUG == True):
        print( "dont yet")

def sto(instr):
    rn = (instr) & 0x6
    a = (instr) & 0x1
    offset = reg[R.PC]
    hi8 = reg[rn+1]
    lo8 = reg[rn]
    addr = (hi8<<8) | lo8
    mem_write(addr+offset,reg[R.R0])
    addr += a
    reg[rn+1] = (addr >> 8) & 0xFF
    reg[rn] = addr & 0xFF
    reg[R.PC] += 1
    if (DEBUG == True):
        print( "dont yet")

def ldi(instr):
    rn = (instr) & 0x7
    imm = mem_read(reg[R.PC])
    reg[rn] = imm
    update_flags_02(rn)
    reg[R.PC] += 1
    if (DEBUG == True):
        print( "ldi " +"r"+str(rn)+" "+str(imm)  )

def lda(instr):
    rn = (instr) & 0x7
    hi8 = mem_read(reg[R.PC])
    lo8 = mem_read(reg[R.PC]+1)
    addr = (hi8<<8) | lo8
    reg[rn] = mem_read(addr)
    update_flags_02(rn)
    reg[R.PC] += 2
    if (DEBUG == True):
        print( "dont yet")

def ldx(instr):
    rn = (instr) & 0x6
    a = (instr) & 0x1
    hi8 = reg[rn+1]
    lo8 = reg[rn]
    addr = (hi8<<8) | lo8
    reg[R.R0] = mem_read(addr) 
    update_flags_02(R.R0)
    mem_write(addr,reg[R.R0])
    addr += a
    reg[rn+1] = (addr >> 8) & 0xFF
    reg[rn] = addr & 0xFF
    if (DEBUG == True):
        print( "dont yet")

def ldo(instr):
    rn = (instr) & 0x6
    a = (instr) & 0x1
    offset = reg[R.PC]
    hi8 = reg[rn+1]
    lo8 = reg[rn]
    addr = (hi8<<8) | lo8
    reg[R.R0] = mem_read(addr+offset)
    update_flags_02(R.R0)
    addr += a
    reg[rn+1] = (addr >> 8) & 0xFF
    reg[rn] = addr & 0xFF
    reg[R.PC] += 1
    if (DEBUG == True):
        print( "dont yet")

"""
TRAPs implementation
"""


class Trap:
    GETC = 0x20  # get character from keyboard
    OUT = 0x21  # output a character
    PUTS = 0x22  # output a word string
    IN = 0x23  # input a string
    PUTSP = 0x24  # output a byte string
    HALT = 0x25  # halt the program


def trap(instr):
    traps.get(instr & 0xFF)()


def trap_putc():
    i = reg[R.R0]
    c = memory[i]
    while c != 0:
        sys.stdout.write(c)
        i += 1
        c = memory[i]
    sys.stdout.flush()


def trap_getc():
    reg[R.R0] = ord(getchar())


def trap_out():
    sys.stdout.write(chr(reg[R.R0]))
    sys.stdout.flush()


def trap_in():
    sys.stdout.write("Enter a character: ")
    sys.stdout.flush()
    reg[R.R0] = sys.stdout.read(1)


def trap_puts():
    for i in range(reg[R.R0], len(memory)):
        c = memory[i]
        if c == 0:
            break
        sys.stdout.write(chr(c))
    sys.stdout.flush()


def trap_putsp():
    for i in range(reg[R.R0], len(memory)):
        c = memory[i]
        if c == 0:
            break
        sys.stdout.write(chr(c & 0xFF))
        char = c >> 8
        if char:
            sys.stdout.write(chr(char))
    sys.stdout.flush()


def trap_halt():
    global is_running
    print('HALT')
    is_running = 0


traps = {
    Trap.GETC: trap_getc,
    Trap.OUT: trap_out,
    Trap.PUTS: trap_puts,
    Trap.IN: trap_in,
    Trap.PUTSP: trap_putsp,
    Trap.HALT: trap_halt,
}


ops = {
    OP.INC: inc,
    OP.ADC: adc,
    OP.TX0: tx0,
    OP.OR : or_ ,
    OP.AND: and_,
    OP.XOR: xor,
    OP.ROL: rol,
    OP.ROR: ror,
    OP.DEC: dec,
    OP.SBC: sbc,
    OP.ADD: add,
    OP.STP: stp,
    OP.BTT: btt,
    OP.CLP: clp,
    OP.T0X: t0x,
    OP.CMP: cmp_,
    OP.PSH: psh,
    OP.POP: pop,
    OP.BR0: br0,
    OP.BR1: br1,
    OP.DBNZ: dbnz,
    OP.INT: int_,
    OP.MUL: mul,
    OP.SPECIAL:special,
    OP.UPP: upp,
    OP.STA: sta,
    OP.STX: stx,
    OP.STO: sto,
    OP.LDI: ldi,
    OP.LDA: lda,
    OP.LDO: ldo,
    OP.LDX: ldx
}


class Mr:
    KBSR = 0x2400  # keyboard status //uart
    KBDR = 0x2402  # keyboard data   //

def check_key():
    _, o, _ = select.select([], [sys.stdin], [], 0)
    for s in o:
        if s == sys.stdin:
            return True
    return False


def mem_write(address, val):
    address = address % UINT16_MAX
    memory[address] = val


def mem_read(address):
    address = address % UINT16_MAX
    if address == Mr.KBSR:
        if check_key():
            memory[Mr.KBSR] = 1 << 15
            memory[Mr.KBDR] = ord(getchar())
        else:
            memory[Mr.KBSR] = 0
    return memory[address]


def sign_extend(x, bit_count):
    if (x >> (bit_count - 1)) & 1:
        x |= 0xFFFF << bit_count
    return x & 0xffff


def update_flags_012(r):
    if reg[r] == 0:
        reg[R.PSR] |=  FL.ZRO
    else:
        reg[R.PSR] = reg[R.PSR] & ~FL.ZRO
    if (reg[r] >> 8)  & 0x1:
        reg[R.PSR] |=  FL.CRY
    else:
        reg[R.PSR] = reg[R.PSR] & ~FL.CRY
    if (reg[r] >> 7)  & 0x1:
        reg[R.PSR] |=  FL.NEG
    else:
        reg[R.PSR] = reg[R.PSR] & ~FL.NEG

def update_flags_02(r):
    if reg[r] == 0:
        reg[R.PSR] |=  FL.ZRO
    else:
        reg[R.PSR] = reg[R.PSR] & ~FL.ZRO
    if (reg[r] >> 7)  & 0x1:
        reg[R.PSR] |=  FL.NEG
    else:
        reg[R.PSR] = reg[R.PSR] & ~FL.NEG


def read_image_file(file_name):
    global memory
    with open(file_name, 'rb') as f:
        origin = 0 #int.from_bytes(f.read(1), byteorder='big')
        memory = array.array("B", [0] * origin)
        max_read = UINT16_MAX - origin
        memory.frombytes(f.read(max_read))
        memory.byteswap()
        memory.fromlist([0]*(UINT16_MAX - len(memory)))
    #with open(file_name, 'rb') as f:
    #    origin = int.from_bytes(f.read(1), byteorder='big')
    #    memory = array.array("B", [0] * origin)
    #    max_read = UINT16_MAX - origin
    #    memory.frombytes(f.read(max_read))
    #    memory.byteswap()
    #    memory.fromlist([0]*(UINT16_MAX - len(memory)))
        print(memory)


def main():
    Allow_Stack_Address_Move = 0
    if len(sys.argv) < 2:
        print('vm.py [obj-file]')
        exit(2)

    file_path = sys.argv[1]
    read_image_file(file_path)

    reg[R.PC] = PC_START

    #while is_running:
    for i in range(15):
        instr = mem_read(reg[R.PC])
        reg[R.PC] += 1
        op = instr >> 3
        fun = ops.get(op, bad_opcode)
        fun(instr)



if __name__ == '__main__':
    main()
