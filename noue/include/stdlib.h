// dummy
#ifndef STDLIB_H
#define STDLIB_H

#define M_PI 3.14
int  atoi(const char*);
long atol(const char*);
int  qsort(void*, size_t, size_t, int(*)(void*,void*));
void* bsearch(void*, void*, size_t, size_t, int(*)(void*,void*));
int abs(int);
void memcpy(void*, const void*, size_t);
int memcmp(const void*, const void*, size_t);
int memset(void*, int value, size_t size);
int isdigit(int);
int isalpha(int);
int isnan(double);
double atof(const char*);
double atan2(double, double);
double sin(double);
double cos(double);
double tan(double);
const char* getenv(const char*);

#endif
