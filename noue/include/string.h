#ifndef STRING_H
#define STRING_H
// dummy
extern int strlen(const char*);
extern int strcmp(const char*, const char*);
extern int strcpy(char*, const char*);
extern int sprintf(char*, const char*, ...);
extern int strncmp(const char*, const char*, size_t);
extern int strcat(char*, const char*);
extern char* strstr(const char*, const char*);
extern int strcasecmp(const char *s1, const char *s2);
extern int strncasecmp(const char *s1, const char *s2, size_t n);
extern int strncmp(const char*, const char*, size_t);
extern char* strncpy(char*, const char*, size_t);
#endif
