#ifndef STDIO_H
#define STDIO_H
// dummy
typedef struct _file{
	int n;
} FILE;
extern FILE* fopen(const char*, const char*);
extern void  fclose(FILE*);
extern void  printf(const char*, ...);
//extern FILE* fopen(const char*, const char*);
extern FILE *stdout, *stdin, *stderr;
extern void  fflush(FILE*);
extern void  exit(int);
extern int   fgets(char*, size_t, FILE*);
extern void  fprintf(FILE* fp, const char*, ...);

#define NULL (void*)0

#endif
