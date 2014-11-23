=================
Introduction
=================
[English](../eng/01.introduction.rst)


はじめに
-------------

「Noue」はPython用のC言語パーサ・エミュレーターです。  
C言語ソースコードを解析し、関数、変数、型をPython上にエクスポートします。  
C言語ソースのユニットテストを、Python上で行うためのツールとして  開発しています。  
使用には、C言語とPythonの言語知識、特にPythonの標準ライブラリ「ctypes」の知識が必要になります。  


test.c  
```c

    #include<stdio.h>
    
    void hello()
    {
        printf("HelloWorld\n");
    }
```

test.py  
```python

    from noue.compiler import CCompiler
    
    # test.cをpythonコードに変換
    test = CCompiler().compile('test.c')
    
    import ctypes
    
    # 外部関数"printf"をリンク
    test.printf = ctypes.cdll.msvcrt.printf
    
    test.hello()
```
	
	
出力  
```console
    >HelloWorld
```



