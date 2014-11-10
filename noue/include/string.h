#ifndef STRING_H
#define STRING_H
// dummy
int strlen(const char*);
int strcmp(const char*, const char*);
int strcpy(char*, const char*);
int sprintf(char*, const char*, ...);
int strncmp(const char*, const char*, size_t);
int strcat(char*, const char*);
char* strstr(const char*, const char*);
int strcasecmp(const char *s1, const char *s2);
int strncasecmp(const char *s1, const char *s2, size_t n);
#endif
