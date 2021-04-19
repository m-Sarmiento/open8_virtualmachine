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
import numpy
import csv

#Global variables
UINT16_MAX   = 2 ** 16
DEBUG        = False
TERMINAL_OUT = True
is_running   = True
memory       = None
LIMIT        = False
ADDR_LIMIT   = 0x80ba
STEP         = False

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
    CLOCK_COUNTER = 13


class register_dict(dict):

    def __setitem__(self, key, value):
        super().__setitem__(key, value % UINT16_MAX)


reg = register_dict({i: 0 for i in range(R.CLOCK_COUNTER)})


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
    LDX = 30
    LDO = 31

class FL:
    """flags"""
    ZRO = 1 << 0  # Zero flag
    CRY = 1 << 1  # Carry flag
    NEG = 1 << 2  # Negative flag
    INT = 1 << 3  # Interrupt enable
    INT = 1 << 7  # Retrieve/Relocate Stack Pointer


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
    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +1

def adc(instr):
    # destination register
    rn = (instr) & 0x7
    reg[R.R0] = reg[R.R0] + reg[rn] + ((reg[R.PSR] >> 1) & 0x1)
    update_flags_012(R.R0)
    reg[R.R0] = reg[R.R0] & 0xFF
    if (DEBUG == True):
        print( "adc " +"r"+str(rn)  )
    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +1

def tx0(instr):
    # destination register
    rn = (instr) & 0x7
    reg[R.R0] = reg[rn] 
    update_flags_02(R.R0)
    reg[R.R0] = reg[R.R0] & 0xFF
    if (DEBUG == True):
        print( "tx0 " +"r"+str(rn)  )
    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +1

def or_(instr):
    # destination register
    rn = (instr) & 0x7
    reg[R.R0] = reg[rn] | reg[R.R0]
    update_flags_02(R.R0)
    reg[R.R0] = reg[R.R0] & 0xFF
    if (DEBUG == True):
        print( "or  " +"r"+str(rn)  )
    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +1

def and_(instr):
    # destination register
    rn = (instr) & 0x7
    reg[R.R0] = reg[rn] & reg[R.R0]
    update_flags_02(R.R0)
    reg[R.R0] = reg[R.R0] & 0xFF
    if (DEBUG == True):
        print( "and " +"r"+str(rn)  )
    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +1

def xor(instr):
    # destination register
    rn = (instr) & 0x7
    reg[R.R0] = reg[rn] ^ reg[R.R0]
    update_flags_02(R.R0)
    reg[R.R0] = reg[R.R0] & 0xFF
    if (DEBUG == True):
        print( "xor " +"r"+str(rn))
    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +1

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
    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +1



def ror(instr):
    # destination register
    rn = (instr) & 0x7
    tmp = reg[rn] & 0x1
    reg[rn] = (reg[rn] >>  1) | ((((reg[R.PSR] >> 1) & 0x1)) << 7) 
    update_flags_02(rn)
    if (tmp):
        reg[R.PSR] |=  FL.CRY
    else:
        reg[R.PSR] = reg[R.PSR] & ~FL.CRY
    reg[rn] = reg[rn] &  0xFF
    if (DEBUG == True):
        print( "ror " +"r"+str(rn)  )
    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +1

def dec(instr):
    # destination register
    rn = (instr) & 0x7
    reg[rn] = reg[rn] + 0xFF
    update_flags_012(rn)
    reg[rn] = reg[rn] &  0xFF
    if (DEBUG == True):
        print( "dec " +"r"+str(rn)  )
    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +1

def sbc(instr):
    # destination register
    rn = (instr) & 0x7
    reg[R.R0] = reg[R.R0] + (-reg[rn]) - ((reg[R.PSR] >> 1) & 0x1) 
    update_flags_012(R.R0)
    reg[R.R0] = reg[R.R0] & 0xFF
    if (DEBUG == True):
        print( "sbc " +"r"+str(rn)  )
    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +1

def add(instr):
    # destination register
    rn = (instr) & 0x7
    reg[R.R0] = reg[R.R0] + reg[rn]
    update_flags_012(R.R0)
    reg[R.R0] = reg[R.R0] & 0xFF
    if (DEBUG == True):
        print( "add " +"r"+str(rn)  )
    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +1

def stp(instr):
    # destination register
    n = (instr) & 0x7
    reg[R.PSR] = reg[R.PSR] | ( 1 << n )
    if (DEBUG == True):
        print( "stp " + str(n))
    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +1

def btt(instr):
    # destination register
    n = (instr) & 0x7
    if (((reg[R.R0] >> n) & 0x1) == 0):
        reg[R.PSR] |=  FL.ZRO
    else:
        reg[R.PSR] = reg[R.PSR] & ~FL.ZRO
    if (reg[R.R0] >> 7)  & 0x1:
        reg[R.PSR] |=  FL.NEG
    else:
        reg[R.PSR] = reg[R.PSR] & ~FL.NEG
    if (DEBUG == True):
        print( "btt " + str(n))
    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +1

def clp(instr):
    # destination register
    n = (instr) & 0x7
    reg[R.PSR] = reg[R.PSR] & ~( 1 << n )
    if (DEBUG == True):
        print( "clp " + str(n))
    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +1

def t0x(instr):
    # destination register
    rn = (instr) & 0x7
    reg[rn] = reg[R.R0] 
    update_flags_02(rn)
    reg[R.R0] = reg[R.R0] & 0xFF
    if (DEBUG == True):
        print( "t0x " +"r"+str(rn)  )
    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +1

def cmp_(instr):
    # destination register
    rn = (instr) & 0x7
    tmp= reg[R.R0] + (-reg[rn])
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
        print( "cmp " +"r"+str(rn)+"   psr "+bin(reg[R.PSR])  )
    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +1
    #input("Waiting...")

def psh(instr):
    rn = (instr) & 0x7
    reg[R.STACK] = reg[R.STACK] - 1
    mem_write(reg[R.STACK], reg[rn])
    #reg[R.STACK] = reg[R.STACK] - 1
    if (DEBUG == True):
        print( "psh " +"r"+str(rn)  +"  stack_pt="+str(reg[R.STACK]))
    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +3

def pop(instr):
    rn = (instr) & 0x7
    #reg[R.STACK] = reg[R.STACK] + 1
    reg[rn] = mem_read(reg[R.STACK])
    reg[R.STACK] = reg[R.STACK] + 1
    if (DEBUG == True):
        print( "pop " +"r"+str(rn)+"  stack_pt="+str(reg[R.STACK])  )
    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +3

def br0(instr):
    bit = (instr) & 0x7
    pc_offset = sign_extend((mem_read(reg[R.PC])) & 0xff, 8)
    if ((reg[R.PSR]>>bit) & 0x1) == 0:
        reg[R.PC] += (pc_offset-2)+1
    else:
        reg[R.PC] +=1
    if (DEBUG == True):
        print( "br0 " +str(bit)+" ."+str(pc_offset)  )
    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +3

def br1(instr):
    bit = (instr) & 0x7
    pc_offset = sign_extend((mem_read(reg[R.PC])) & 0xff, 8)
    if ((reg[R.PSR]>>bit) & 0x1) == 1:
        reg[R.PC] += (pc_offset-2)+1
    else:
        reg[R.PC] +=1
    if (DEBUG == True):
        print( "br1 " +str(bit)+" ."+str(pc_offset))
    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +3

def dbnz(instr):
    rn = (instr) & 0x7
    reg[rn] = reg[rn] + 0xFF
    update_flags_012(rn)
    reg[rn] = reg[rn] &  0xFF 
    pc_offset = sign_extend((mem_read(reg[R.PC])) & 0xff, 8)
    if ((reg[R.PSR]) & 0x1) == 1:
        reg[R.PC] += pc_offset
    if (DEBUG == True):
        print( "dbnz " +"r"+str(rn)+" "+str(pc_offset)  )
    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +3

def int_(instr):
    n = (instr) & 0x7
    if (DEBUG == True):
        print( "int")
    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +7
    pass
    #TODO: complete
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
    tmp = reg[rn] * reg[R.R0]
    reg[R.R1] = (tmp >> 8 ) & 0xFF
    reg[R.R0] = (tmp ) & 0xFF
    if tmp == 0:
        reg[R.PSR] |=  FL.ZRO
    else:
        reg[R.PSR] = reg[R.PSR] & ~FL.ZRO
    if (DEBUG == True):
        print( "mul " +str(rn))
    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +2

def special (instr):
    select = (instr) & 0x7
    if select == 0:
                    if (Allow_Stack_Address_Move):
                        if ((reg[R.PSR])>> 7) & 0x1:
                            reg[R.STACK] = reg[R.R1] << 8 | reg[R.R0]
                        else:
                            tmp = reg[R.STACK] 
                            reg[R.R1]= (tmp >> 8) & 0xFF
                            reg[R.R0]= (tmp >> 0) & 0xFF
                    else:
                        reg[R.STACK] = 0x007F
                    if (DEBUG == True):
                        print( "rsp ")
                    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +5 # due to retrive restore
            #RSP
    elif select == 1:
                    addr = (mem_read(reg[R.STACK]+1) << 8) | mem_read(reg[R.STACK])
                    reg[R.PC] = addr
                    reg[R.STACK] += 2
                    if (DEBUG == True):
                        print( "rts "+str(addr))
                    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +5
            #RTS
    elif select == 2: 
                    reg[R.PC] = (mem_read(reg[R.STACK]+1) << 8) | mem_read(reg[R.STACK])
                    reg[R.PSR] = mem_read(reg[R.STACK]+2)
                    reg[R.STACK] += 3
                    if (DEBUG == True):
                        print( "rti ")
                    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +5
            #RTI
    elif select == 3: 
                    if (DEBUG == True):
                        print( "brk ")
                    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +1
                    pass
            #BRK
    elif select == 4: 
                    lo8 = mem_read(reg[R.PC])
                    hi8 = mem_read(reg[R.PC]+1)
                    addr = (hi8 << 8) | lo8
                    reg[R.PC] = addr
                    if (DEBUG == True):
                        print( "jmp "+str(addr))
                    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +3
            #JMP
    elif select == 5: 
                    if (DEBUG == True):
                        print( "smsk")
                    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +1
                    pass
            #SMSK
    elif select == 6: 
                    if (DEBUG == True):
                        print( "gmsk")
                    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +1
                    pass
            #GMSK
    elif select == 7: 
                    tmp = reg[R.PC]+2
                    lo8 = mem_read(reg[R.PC])
                    hi8 = mem_read(reg[R.PC]+1)
                    addr = (hi8 << 8) | lo8
                    reg[R.STACK] -= 1
                    mem_write(reg[R.STACK],(tmp >> 8) & 0xFF)
                    reg[R.STACK] -= 1
                    mem_write(reg[R.STACK],(tmp) & 0xFF)
                    reg[R.PC] = addr
                    if (DEBUG == True):
                        print( "jsr "+str(addr))
                    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +5
            #JSR
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
        print( "upp "+"r"+str(rn))
    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +2

def sta(instr):
    rn = (instr) & 0x7
    lo8 = mem_read(reg[R.PC])
    hi8 = mem_read(reg[R.PC]+1)
    addr = (hi8<<8) | lo8
    mem_write(addr,reg[rn])
    reg[R.PC] += 2
    if (DEBUG == True):
        print( "sta " +"r"+str(rn)+" "+str(addr)  )
    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +4

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
        if (a == 0):
            print( "stx " +"r"+str(rn) )
        else:
            print( "stx " +"r"+str(rn)+"++"  )
    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +3

def sto(instr):
    rn = (instr) & 0x6
    a = (instr) & 0x1
    offset = mem_read(reg[R.PC])
    hi8 = reg[rn+1]
    lo8 = reg[rn]
    addr = (hi8<<8) | lo8
    faddr=addr+offset
    mem_write(faddr,reg[R.R0])
    addr += a
    reg[rn+1] = (addr >> 8) & 0xFF
    reg[rn] = addr & 0xFF
    reg[R.PC] += 1
    if (DEBUG == True):
        if (a == 0):
            print( "sto " +"r"+str(rn)+"   "+str(offset)+"  addr:"+str(faddr) )
        else:
            print( "sto " +"r"+str(rn)+"++ "+str(offset)+"  addr:"+str(faddr))
    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +4

def ldi(instr):
    rn = (instr) & 0x7
    imm = mem_read(reg[R.PC])
    reg[rn] = imm
    update_flags_02(rn)
    reg[R.PC] += 1
    if (DEBUG == True):
        print( "ldi " +"r"+str(rn)+" "+str(imm)  )
    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +2

def lda(instr):
    rn = (instr) & 0x7
    lo8 = mem_read(reg[R.PC])
    hi8 = mem_read(reg[R.PC]+1)
    addr = (hi8<<8) | lo8
    reg[rn] = mem_read(addr)
    update_flags_02(rn)
    reg[R.PC] += 2
    if (DEBUG == True):
        print( "lda " +"r"+str(rn)+" "+str(addr)+" "+ str(reg[rn]) )
    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +4

def ldx(instr):
    rn = (instr) & 0x6
    a = (instr) & 0x1
    hi8 = reg[rn+1]
    lo8 = reg[rn]
    addr = (hi8<<8) | lo8
    reg[R.R0] = mem_read(addr) 
    update_flags_02(R.R0)
    addr += a
    reg[rn+1] = (addr >> 8) & 0xFF
    reg[rn] = addr & 0xFF
    if (DEBUG == True):
        if (a == 0):
            print( "ldx " +"r"+str(rn) )
        else:
            print( "ldx " +"r"+str(rn)+"++"  )
    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +3

def ldo(instr):
    rn = (instr) & 0x6
    a = (instr) & 0x1
    offset = mem_read(reg[R.PC])
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
        if (a == 0):
            print( "ldo " +"r"+str(rn)+" "+str(offset)+" addr:"+str(addr+offset) )
        else:
            print( "ldo " +"r"+str(rn)+"++ "+str(offset)+" addr:"+str(addr+offset) )
    reg[R.CLOCK_COUNTER]=reg[R.CLOCK_COUNTER] +4

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
    is_running = False


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
    OP.LDX: ldx,
    OP.LDO: ldo
}

class memory_map:
    RAM_Address              = 0x0000 ### System RAM
    ALU_Address              = 0x1000 ### ALU16 coprocessor
    RTC_Address              = 0x1100 ### System Timer / RT Clock
    ETC_Address              = 0x1200 ### Epoch Timer/Alarm Clock
    TMR_Address              = 0x1400 ### PIT timer
    SDLC_Address             = 0x1800 ### LCD serial interface
    LED_Address              = 0x2000 ### LED Display
    DSW_Address              = 0x2100 ### Dip Switches
    BTN_Address              = 0x2200 ### Push Buttons
    SER_Address              = 0x2400 ### UART interface
    MAX_Address              = 0x2800 ### Max 7221 base address
    VEC_Address              = 0x3000 ### Vector RX base address
    CHR_Address              = 0x3100 ### Elapsed Time / Chronometer
    ROM_Address              = 0x8000 ### Application ROM
    ISR_Start_Addr           = 0xFFF0 ### ISR Vector Table

class Mr:
    KBSR = memory_map.SER_Address
    KBDR = memory_map.SER_Address

def check_key():
    _, o, _ = select.select([], [sys.stdin], [], 0)
    for s in o:
        if s == sys.stdin:
            return True
    return False


def mem_write(address, val):
    global is_running
    address = address % UINT16_MAX
    global TERMINAL_OUT
    if (address == memory_map.SER_Address ):
        if TERMINAL_OUT:
            sys.stdout.write(chr(val))
            sys.stdout.flush()
    """if ((address >= memory_map.ROM_Address) & (address <= memory_map.ISR_Start_Addr)):
        is_running = False
        print("Try to write rom memory in "+hex(address))"""
    memory[address] = val


def mem_read(address):
    address = address % UINT16_MAX
    if address == Mr.KBDR:
        if check_key():
            #memory[Mr.KBSR] = 1 << 15
            memory[Mr.KBDR] = ord(getchar())
        else:
            #memory[Mr.KBSR] = 0
            memory[Mr.KBDR] = 0
    if address == memory_map.RTC_Address:
        memory[address] = (reg[R.CLOCK_COUNTER] >> 8) & 0xFF
    if address == memory_map.RTC_Address+1:
        memory[address] = reg[R.CLOCK_COUNTER] & 0xFF
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
        origin = memory_map.ROM_Address #int.from_bytes(f.read(1), byteorder='big')
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

def dump_memory(file_name):
    global memory
    #print(memory)
    a = numpy.asarray(memory)
    numpy.savetxt(file_name+".csv", a, delimiter=",")

def dump_regfile():
    global reg
    print(reg)
    with open('regfile.csv', 'w') as f:  
        w = csv.DictWriter(f, reg.keys())
        w.writeheader()
        w.writerow(reg)
def print_register():
    global reg
    print("r0  "+str(reg[R.R0])+" "+hex(reg[R.R0]))
    print("r1  "+str(reg[R.R1])+" "+hex(reg[R.R1]))
    print("r2  "+str(reg[R.R2])+" "+hex(reg[R.R2]))
    print("r3  "+str(reg[R.R3])+" "+hex(reg[R.R3]))
    print("r4  "+str(reg[R.R4])+" "+hex(reg[R.R4]))
    print("r5  "+str(reg[R.R5])+" "+hex(reg[R.R5]))
    print("r6  "+str(reg[R.R6])+" "+hex(reg[R.R6]))
    print("r7  "+str(reg[R.R7])+" "+hex(reg[R.R7]))
    print("PSR "+str(reg[R.PSR])+" "+hex(reg[R.PSR])+" "+bin(reg[R.PSR]))
    print("PC+ "+str(reg[R.PC])+" "+hex(reg[R.PC]))
    print("STK "+str(reg[R.STACK])+" "+hex(reg[R.STACK]))
    print("VEC "+str(reg[R.VECTOR_BASE])+" "+hex(reg[R.VECTOR_BASE]))
    print("CLOCK "+str(reg[R.CLOCK_COUNTER])+" "+hex(reg[R.CLOCK_COUNTER]))

Program_Start_Addr       = memory_map.ROM_Address 
ISR_Start_Addr           = 0xFFFF
Stack_Start_Addr         = 0x0FFE
Allow_Stack_Address_Move = True
Enable_Auto_Increment    = True
BRK_Implements_WAI       = True
Enable_NMI               = True
Sequential_Interrupts    = True
RTI_Ignores_GP_Flags     = True
Default_Interrupt_Mask   = 0x00
Clock_Frequency          = 100000000.0


def main():
    if len(sys.argv) < 2:
        print('vm.py [obj-file]')
        exit(2)
    global DEBUG
    global TERMINAL_OUT
    global is_running
    global ADDR_LIMIT
    global LIMIT
    global STEP
    file_path = sys.argv[1]
    read_image_file(file_path)
    reg[R.PC] = Program_Start_Addr
    reg[R.STACK] = Stack_Start_Addr
    reg[R.CLOCK_COUNTER]=0
    dump_memory("initial")
    while is_running:
    #for i in range(15):
        #print(reg)
        if (reg[R.CLOCK_COUNTER] > 0xffff):
            reg[R.CLOCK_COUNTER] = 0;
        if (reg[R.STACK] > 0xfff):
            is_running = False;
            print("stack overflow")
        if (DEBUG == True):
            print(hex(reg[R.PC]), end="  ")
        instr = mem_read(reg[R.PC])
        reg[R.PC] += 1
        op = instr >> 3
        fun = ops.get(op, bad_opcode)
        fun(instr)
        if (DEBUG == True):
            print_register()
        if(STEP):
            input("Waiting...")
            dump_memory("final")
        #dump_memory("final")
        if (reg[R.PC] == ADDR_LIMIT) & LIMIT:
            STEP = True
            LIMIT = False
            #print_register()
            input("Waiting...")
            dump_memory("final")
           
       
    dump_memory("final")
    #dump_regfile()
    #print_register() 


if __name__ == '__main__':
    main()
