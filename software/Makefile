LINKER = open8_1.x
#LINKER = rom.lds

.PRECIOUS: %.o %.elf %.bin %.bc

CC = clang
DIS = llvm-dis
#LLC = $(abspath ../..)/build/bin/llc
LLC = llc

#LD = $(abspath ..)/build/ld/ld-new
#LD = $(abspath ../..)/build/bin/ld.lld
LD = ld.lld

#AS = $(abspath ..)/build/gas/as-new
#AS = $(abspath ../..)/build/bin/llvm-mc
AS = llvm-mc

#OBJCOPY = $(abspath ..)/build/binutils/objcopy 
#OBJCOPY = $(abspath ../..)/build/bin/llvm-objcopy 
OBJCOPY = llvm-objcopy

#OBJDUMP = $(abspath ..)/build/binutils/objdump
#OBJDUMP = $(abspath ../..)/build/bin/llvm-objdump 
OBJDUMP = llvm-objdump

.DEFAULT_GOAL := default

default: main.bc
	make main.mem

avr: main.cpp
	$(CC) -target avr -c $^ -emit-llvm -o avr.bc
	$(DIS) avr.bc -o avr.ll
	$(LLC) -march=avr -relocation-model=pic -filetype=asm avr.bc -o avr.S

%.bc : %.cpp
	$(CC) -target avr -c $^ -emit-llvm -o $@
	$(DIS) $@ -o main.ll

#%.S: %.bc
#	$(LLC) -march=urisc -relocation-model=pic -filetype=asm $^ -o $@ 
#-debug

%.o: %.bc
	$(LLC) -march=urisc -relocation-model=pic -filetype=asm $^ -o $(^:.bc=.S) 
#-debug
	$(LLC) -march=urisc -relocation-model=pic -filetype=obj $^ -o $@

#%.o: %.S
#	$(AS) -arch=urisc -filetype=obj $^ -o $@
#	$(AS) $^ -o $@

%.elf: %.o
	$(OBJDUMP) -D $^ > main_nold.dump
	$(LD) -b elf $^ -T $(LINKER) -o $@
#	$(LD) -b elf32-open8 $^ -T $(LINKER) -o $@

%.bin: %.elf
	$(OBJDUMP) -D $^ > $(^:.elf=.dump)
	cat $(^:.elf=.dump)
	$(OBJDUMP) -D $^ > $(^:.elf=noaliases.dump)
	$(OBJCOPY) -O binary $^ $@ 
#   --only-section=.text
#	$(OBJCOPY) -O binary $^ $@ --only-section=.data

%.mem: %.bin
	od -t x1 -An -w1 -v $^ > $@
#	od -t x1 -An -w1 -v ram.bin > ram.mem

move: main.mem
	cp $^ /home/marco/open8/open8_urisc_scala/sim/verilator/emulator/rom.mem
#	cp ram.mem /home/marco/open8/open8_urisc_scala/sim/verilator/emulator/ram.mem

clean:
	-rm -rf *.mem *.bin *.elf *.o *.noaliases.dump *.dump *.S *.bc *.txt *.ll *.map *.ihex *.HEX
.PHONY: clean 
.PHONY: move
