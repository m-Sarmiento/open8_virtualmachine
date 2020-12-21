/*------ C Linker ------*/
/*-- Only ram not rom --*/

OUTPUT_ARCH( "open8" )

MEMORY{  ram ( rx ) : ORIGIN = 0x0000, LENGTH = 4K	}

SECTIONS
{
  .memory : {
		. = 0x0000;
		*(.text);
		*(.rodata);
		*(.preinit_array);
		*(.init_array);
		*(.fini_array);
		*(.ctors);
		*(.dtors);
		. = ALIGN(4);
		*(.data);
		*(.bss);
		*(.stack);
		end = .;
	} > ram
}
