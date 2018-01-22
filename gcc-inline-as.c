/*
  gcc gcc-inline-as.c -o /tmp/gi
*/

static inline char * strcpy(char * dest,const char *src)
{
    int d0, d1, d2;
    __asm__ __volatile__(  "1: lodsb\n"
                       "stosb\n"
                       "testb %%al,%%al\n"
                       "jne 1b"
                     : "=&S" (d0), "=&D" (d1), "=&a" (d2)
                     : "0" (src),"1" (dest) 
                     : "memory");
    return dest;
}

#define mov_blk(src, dest, numwords) \
__asm__ __volatile__ (                                          \
                   "cld\n\t"                                \
                   "rep\n\t"                                \
                   "movsl"                                  \
                   :                                        \
                   : "S" (src), "D" (dest), "c" (numwords)  \
                   : "%ecx", "%esi", "%edi"                 \
                   )

#define _syscall3(type,name,type1,arg1,type2,arg2,type3,arg3) \
type name(type1 arg1,type2 arg2,type3 arg3) \
{ \
    long __res; \
    __asm__ volatile (  "int $0x80" \
                  : "=a" (__res) \
                  : "0" (__NR_##name),"b" ((long)(arg1)),"c" ((long)(arg2)), \
                    "d" ((long)(arg3))); \
    __syscall_return(type,__res); \
}

// Exit syscall; if not ::: extended asm, no double % for eax, just single as %eax
int main()
{
        __asm__ ("movl $1,%%eax\n"        /* SYS_exit is 1 */
            "xorl %%ebx,%%ebx\n"      /* Argument is in ebx, it is 0 */
            "int  $0x80"            /* Enter kernel mode */
             : : :"eax", "ebx"
             );
}

