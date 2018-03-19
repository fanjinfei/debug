; using NASM syntax

section .data
	msg db "0x00000000",10

section .text
global _start
_start:
	mov eax,1
	cpuid
	bt ecx,30
	mov edi,1 ; exit code: failure
	jnc .exit

	; rdrand sets CF=0 if no random number
	; was available. Intel documentation
	; recommends 10 retries in a tight loop
	mov ecx,11
.loop1:
	sub ecx, 1
	jz .exit ; exit code is set already
	rdrand eax
	jnc .loop1

	; convert the number to ASCII
	mov edi,msg+9
	mov ecx,8
.loop2:
	mov edx,eax
	and edx,0Fh
	; add 7 to nibbles of 0xA and above
	; to align with ASCII code for 'A'
	; ('A' - '0') - 10 = 7
	xor r9d, r9d
        lea r8d, [r9+7] ; r8=7
	cmp dl,9
	cmova r9,r8
	add edx,r9d
	add [rdi],dl
	shr eax,4
	sub edi, 1
	sub ecx, 1
        jnz .loop2

	mov eax,1 ; SYS_WRITE
	mov edi,eax ; stdout=SYS_WRITE=1
	mov esi,msg
	mov edx,11
	syscall

	xor edi,edi ; exit code zero: success
.exit:
	mov eax,60 ; SYS_EXIT
	syscall
