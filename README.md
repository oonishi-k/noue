
Noue: C Language Emulator for Python
=====================================



What is Noue?
-------------
  Noue is a C Language emulator library for Python.  
  Noue parses a C source, and exports functions, types, and global variables for python.  
  If you use Noue, you need to know about python standard library, "ctypes".  



Requirements
------------
 * Python3.4 or later  
 * OS: Windows or Linux (64bit)  



Install
-------
  Download the zip, and run the supplied setup.py script.
```console
>cd ./noue
>python3 ./setup.py install
```




Sample
------

test.c:  
```c
#include <stdio.h>

typedef struct{
	double x,y,z;
}vector_t;

vector_t V0 = {0,0,0};

double innerproduct(vector_t* l, vector_t* r)
{
	return l->x*r->x + l->y*r->y + l->z*r->z;
}	

vector_t sub(const vector_t* l, const vector_t* r)
{
	vector_t res = *l;
	res.x -= r->x;
	res.y -= r->y;
	return res;
}

double triangle_area(const vector_t* v0
                   , const vector_t* v1
                   , const vector_t* v2)
{
	vector_t l = *v1, r = *v2;
	l = sub(&l, v0);
	r = sub(&r, v0);
	double res = (l.x*r.y + l.y*r.x)/2;
	/*@py:
		# pyhton code insertion 
		print('result=', res)
	*/
	return res;
}


void dump(const vector_t* v)
{
	printf("x=%lf y=%lf\n", v->x, v->y);
}
```


```python
>>> from noue.compiler import CCompiler

>>> # converting c source to python module
>>> test = CCompiler().compile('./test.c')


>>> # exporting c structure as ctypes.Structure object
>>> v = test.vector_t()
>>> print(v.x, v.y)
0.0 0.0

>>> # exporting global variable as ctypes object
>>> print(test.V0.x, test.V0.y)
0.0 0.0

>>> # exporting function
>>> # (parameters must be ctypes objects)
>>> from ctypes import *
>>> v1 = test.vector_t(1,0)
>>> v2 = test.vector_t(1,1)
>>> inner = test.innerproduct(pointer(v1), pointer(v2))
>>> print(inner)
1.0

>>> # Functions deculared as "extern" must be liked later.
>>> v3 = test.vector_t(2.0, 3.0)
>>> test.dump(pointer(v3))
Traceback (most recent call last):
  File "<pyshell#228>", line 1, in <module>
    test.dump(pointer(v3))
  File "./test.c", line 35, in dump
    printf("x=%lf y=%lf\n", v->x, v->y);
AttributeError: 'module' object has no attribute 'printf'

>>> # "printf" is linked from C standard Library using python ctypes module.
>>> libc = CDLL('libc.so.6')
>>> test.printf = libc.printf
>>> test.dump(pointer(v3))
x=0.000000 y=-1.000000

>>> # Python standard debugger, "pdb" is available.
>>> import pdb
>>> pdb.runcall(test.sub, pointer(v1), pointer(v2))
> ./test.c(14)sub()
-> vector_t res = *l;
(Pdb) n
> ./test.c(15)sub()
-> res.x -= r->x;
(Pdb) n
> ./test.c(16)sub()
-> res.y -= r->y;
(Pdb) n
> ./test.c(17)sub()
-> return res;
(Pdb) p res
<test.typedefas(vector_t) object at 0x00000000035206D8>
(Pdb) c
<test.typedefas(vector_t) object at 0x0000000003520748>

>>> # You can embed python source in c language source.
>>> area = test.triangle_area(pointer(test.V0), pointer(v1), pointer(v2))
result= c_double(0.5)
>>> print(area)
0.5

```





