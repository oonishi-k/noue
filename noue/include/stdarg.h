#ifndef __STDARG_H__
#define __STDARG_H__
typedef char* va_list;

extern void  __noue_va_start( va_list list , ...);
extern void* __noue_va_arg  ( va_list list, size_t);
extern void  __noue_va_end  ( va_list list);

#define va_start(list, ...)   __noue_va_start(list, __VA_ARGS__)
#define va_arg(list, typ)     (typ)__noue_va_arg(list, sizeof(typ))
#define va_end                __noue_va_end  
#endif

