
Noue: C Language Emulator for Python
====================
[[English](README.md)]


Noueとは
--------
  Noueはpython用のC言語エミュレーターライブラリです。  
  C言語ソースにふくまれる関数、型、グローバル変数をピュアPythonオブジェクトに変換します。  
  C言語開発における、関数単位のテスト、デバッグをPython上で行うことを目的としています。  
  (実行効率はPythonで普通に書いた場合と同等かそれ以下ですので、実行環境には不向きです)  
  
  使用にはPythonの標準ライブラリ「ctypes」の知識が必要になります。



動作環境
--------
 * Python3.4以降  
 * OS: Windows or Linux (64bit)  



インストール
------------
  ソース一式をダウンロード後、setup.pyを実行する  
```console
>cd ./noue
>python3 ./setup.py install
```




サンプル
---------

test.c:  
```c
#include <stdio.h>

typedef struct{
	double x,y;
}vector_t;

vector_t V0 = {0,0};

double innerproduct(vector_t* l, vector_t* r)
{
	return l->x*r->x + l->y*r->y;
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

>>> # cソースをpythonモジュールに変換
>>> test = CCompiler().compile('./test.c')


>>> # 構造体をctypes.Structureオブジェクトとしてエクスポート
>>> v = test.vector_t()
>>> print(v.x, v.y)
0.0 0.0

>>> # グローバル変数をctypesオブジェクトとしてエクスポート
>>> print(test.V0.x, test.V0.y)
0.0 0.0

>>> # 関数をエクスポート
>>> # ※引数はctypesオブジェクトでなければならない
>>> from ctypes import *
>>> v1 = test.vector_t(1,0)
>>> v2 = test.vector_t(1,1)
>>> inner = test.innerproduct(pointer(v1), pointer(v2))
>>> print(inner)
1.0

>>> # externとして宣言された関数は
>>> # 別途リンクする必要がある
>>> v3 = test.vector_t(2.0, 3.0)
>>> test.dump(pointer(v3))
Traceback (most recent call last):
  File "<pyshell#228>", line 1, in <module>
    test.dump(pointer(v3))
  File "./test.c", line 35, in dump
    printf("x=%lf y=%lf\n", v->x, v->y);
AttributeError: 'module' object has no attribute 'printf'

>>> # ctypesを利用して、標準ライブラリからprintfをリンク
>>> libc = CDLL('libc.so.6')
>>> test.printf = libc.printf
>>> test.dump(pointer(v3))
x=0.000000 y=-1.000000

>>> #pythonの標準デバッガ"pdb"が利用可能
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

>>> # C言語ソースにpythonコードの埋め込みが可能
>>> area = test.triangle_area(pointer(test.V0), pointer(v1), pointer(v2))
result= c_double(0.5)
>>> print(area)
0.5

```





