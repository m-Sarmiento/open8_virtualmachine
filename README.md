# Virtual Machine for Open8 assembly

This is implementation of own virtual machine (VM) for  Open8 assembly language in `python`, inspired by [this tutorial](https://github.com/justinmeiners/lc3-vm).

`software/` directory contains c files that can be compiled to test VM.

## Requirements

Numpy, to generate .csv memory dump files.

## Running the VM

```
./vm.py software/main.bin
# C-c to close
```
