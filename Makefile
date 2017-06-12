
example1:
	nasm -f elf64 -o example1.o example1.asm
	ld -m elf_x86_64 -o /tmp/a --entry=start example1.o
