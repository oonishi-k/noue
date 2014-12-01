#coding: utf8
import sys
from copy import deepcopy

try:
	from .preprocessor import *
	from .syntaxtree   import *
	from .parser       import *
	from .coresyntax   import *
	from .codegenerator import *
	from .savecache     import *
except SystemError:
	import imp
	noue = imp.load_source('noue', './__init__.py')
	from noue.preprocessor import *
	from noue.syntaxtree   import *
	from noue.parser       import *
	from noue.coresyntax   import *
	from noue.codegenerator import *
	from noue.savecache     import *

class CompilerBase:
	default_include = [os.path.abspath(os.path.join(os.path.dirname(__file__), 'include'))]
	def __init__(me, encoding=sys.getdefaultencoding()
					, includes=[], ignore_warnings=[]
					, D=''):
		me.encoding = encoding
		me.compiler = ExecodeGeneratorLLP64()
		me.core = SyntaxCore(me.compiler)
		me.parser = Parser(me.core)
		me.preprocessor = Preprocessor(Tokenizer(), includes=me.default_include + includes, D=D)
		me.ignore_warnings = ignore_warnings
		
	def compile(me, file, encoding=None, printerror=True):
		try:
			with warnings.catch_warnings(record=True) as r:
				for iw in me.ignore_warnings:
					warnings.filterwarnings('ignore', category=iw)

				with open(file, encoding=encoding or me.encoding) as f:
					src = f.read()
					res = me.compile_source(src, file, 1, encoding=encoding or me.encoding)
			return res
		finally:
			if printerror:
				errcnt = 0
				wrncnt = 0
				for w in r:
					print(w.message.message())
					print()
					if isinstance(w.message, NoueError):
						errcnt += 1
					elif isinstance(w.message, NoueWarning):
						wrncnt += 1
				print('error :%d, warning :%d'%(errcnt, wrncnt))
			else:
				for w in r:
					warnings.warn_explicit(w.message, w.category, w.filename, w.lineno)#, r.module, r.registry)
		
				
	def parse(me, file, encoding=None, printerror=True):
		with warnings.catch_warnings(record=True) as r:
			for iw in me.ignore_warnings:
				warnings.filterwarnings('ignore', category=iw)

			with open(file, encoding=encoding or me.encoding) as f:
				src = f.read()
				res =  me.parse_source(src, file, 1, encoding=encoding or me.encoding)
		
		if printerror:
			errcnt = 0
			wrncnt = 0
			for w in r:
				print(w.message.message())
				print()
				if isinstance(w.message, NoueError):
					errcnt += 1
				elif isinstance(w.message, NoueWarning):
					wrncnt += 1
			print('error count:%d, warning count:%d'%(errcnt, wrncnt))
		else:
			for w in r:
				warnings.warn_explicit(w.message, w.category, w.filename, w.lineno)#, r.module, r.registry)
		return res
			
	
	def compile_source(me, src, filename, lineno, encoding=None):
		module = me.parse_source(src, filename, lineno, encoding or me.encoding)
		
		compiler = deepcopy(me.compiler)
		mod = compiler.compile(module)	

		return mod
		
		
	def parse_source(me, src, filename, lineno, encoding):
		parser = deepcopy(me.parser)
		p = parser.parse_global(filename)
		
		preprocessor = deepcopy(me.preprocessor)
		
		tok = preprocessor.proccess(src, filename, lineno)
		
		next(p)
		#with warnings.catch_warnings(record = True) as rec:
		#	warnings.filterwarnings('always')
		if 1:
			try:
				for t in tok:
					if t and t[0].type == 'MC':
						p.throw(parser.InsertComment(t[0]))
						continue
					p.send(t)
				p.send([END(filename)])
				p.throw(parser.FileEnd())
			except StopIteration as stop:
				module = stop.args[0]
			
		#for w in rec:
		#	print(w.message.message())

		return module
		
	def savecache(me, pymod, cachename = ''):
		s = caches(pymod)
		import os.path
		if not cachename:
			cachename = os.path.splitext(pymod.__file__)[0] + '.noue_cache'
		with open(cachename, 'wb') as f:
			f.write(s)
		return
		
	def loadcache(me, cachename):
		with open(cachename, 'rb') as f:
			s = f.read()
		return loads(s)
		
		
class GCC(CompilerBase):
	_defined_macro = """
#define __DBL_MIN_EXP__ (-1021)
#define __UINT_LEAST16_MAX__ 65535
#define __ATOMIC_ACQUIRE 2
#define __FLT_MIN__ 1.17549435082228750797e-38F
#define __UINT_LEAST8_TYPE__ unsigned char
#define __INTMAX_C(c) c ## L
#define __CHAR_BIT__ 8
#define __UINT8_MAX__ 255
#define __WINT_MAX__ 4294967295U
#define __ORDER_LITTLE_ENDIAN__ 1234
#define __SIZE_MAX__ 18446744073709551615UL
#define __WCHAR_MAX__ 65535
#define __GCC_HAVE_SYNC_COMPARE_AND_SWAP_1 1
#define __GCC_HAVE_SYNC_COMPARE_AND_SWAP_2 1
#define __GCC_HAVE_SYNC_COMPARE_AND_SWAP_4 1
#define __DBL_DENORM_MIN__ ((double)4.94065645841246544177e-324L)
#define __GCC_HAVE_SYNC_COMPARE_AND_SWAP_8 1
#define __GCC_ATOMIC_CHAR_LOCK_FREE 2
#define __FLT_EVAL_METHOD__ 0
#define __unix__ 1
#define __GCC_ATOMIC_CHAR32_T_LOCK_FREE 2
#define __x86_64 1
#define __UINT_FAST64_MAX__ 18446744073709551615UL
#define __SIG_ATOMIC_TYPE__ int
#define __DBL_MIN_10_EXP__ (-307)
#define __FINITE_MATH_ONLY__ 0
#define __GNUC_PATCHLEVEL__ 3
#define __UINT_FAST8_MAX__ 255
#define _stdcall __attribute__((__stdcall__))
#define __DEC64_MAX_EXP__ 385
#define __INT8_C(c) c
#define __UINT_LEAST64_MAX__ 18446744073709551615UL
#define __SHRT_MAX__ 32767
#define __LDBL_MAX__ 1.18973149535723176502e+4932L
#define __UINT_LEAST8_MAX__ 255
#define __GCC_ATOMIC_BOOL_LOCK_FREE 2
#define __UINTMAX_TYPE__ long unsigned int
#define __DEC32_EPSILON__ 1E-6DF
#define __unix 1
#define __UINT32_MAX__ 4294967295U
#define __LDBL_MAX_EXP__ 16384
#define __WINT_MIN__ 0U
#define __SCHAR_MAX__ 127
#define __WCHAR_MIN__ 0
#define __INT64_C(c) c ## L
#define __DBL_DIG__ 15
#define __GCC_ATOMIC_POINTER_LOCK_FREE 2
#define __SIZEOF_INT__ 4
#define __SIZEOF_POINTER__ 8
#define __USER_LABEL_PREFIX__
#define __STDC_HOSTED__ 1
#define __LDBL_HAS_INFINITY__ 1
#define __FLT_EPSILON__ 1.19209289550781250000e-7F
#define __LDBL_MIN__ 3.36210314311209350626e-4932L
#define __DEC32_MAX__ 9.999999E96DF
#define __INT32_MAX__ 2147483647
#define __SIZEOF_LONG__ 8
#define __UINT16_C(c) c
#define __DECIMAL_DIG__ 21
#define __LDBL_HAS_QUIET_NAN__ 1
#define __GNUC__ 4
#define _cdecl __attribute__((__cdecl__))
#define __MMX__ 1
#define __FLT_HAS_DENORM__ 1
#define __SIZEOF_LONG_DOUBLE__ 16
#define __BIGGEST_ALIGNMENT__ 16
#define __DBL_MAX__ ((double)1.79769313486231570815e+308L)
#define _thiscall __attribute__((__thiscall__))
#define __INT_FAST32_MAX__ 9223372036854775807L
#define __DBL_HAS_INFINITY__ 1
#define __DEC32_MIN_EXP__ (-94)
#define __INT_FAST16_TYPE__ long int
#define _fastcall __attribute__((__fastcall__))
#define __LDBL_HAS_DENORM__ 1
#define __DEC128_MAX__ 9.999999999999999999999999999999999E6144DL
#define __INT_LEAST32_MAX__ 2147483647
#define __DEC32_MIN__ 1E-95DF
#define __DBL_MAX_EXP__ 1024
#define __DEC128_EPSILON__ 1E-33DL
#define __SSE2_MATH__ 1
#define __ATOMIC_HLE_RELEASE 131072
#define __PTRDIFF_MAX__ 9223372036854775807L
#define __amd64 1
#define __ATOMIC_HLE_ACQUIRE 65536
#define __LONG_LONG_MAX__ 9223372036854775807LL
#define __SIZEOF_SIZE_T__ 8
#define __SIZEOF_WINT_T__ 4
#define __GXX_ABI_VERSION 1002
#define __FLT_MIN_EXP__ (-125)
#define __INT_FAST64_TYPE__ long int
#define __DBL_MIN__ ((double)2.22507385850720138309e-308L)
#define __LP64__ 1
#define __DECIMAL_BID_FORMAT__ 1
#define __GXX_TYPEINFO_EQUALITY_INLINE 0
#define __DEC128_MIN__ 1E-6143DL
#define __REGISTER_PREFIX__
#define __UINT16_MAX__ 65535
#define __DBL_HAS_DENORM__ 1
#define __cdecl __attribute__((__cdecl__))
#define __UINT8_TYPE__ unsigned char
#define __NO_INLINE__ 1
#define __FLT_MANT_DIG__ 24
#define __VERSION__ "4.8.3"
#define __UINT64_C(c) c ## UL
#define __GCC_ATOMIC_INT_LOCK_FREE 2
#define __FLOAT_WORD_ORDER__ __ORDER_LITTLE_ENDIAN__
#define __INT32_C(c) c
#define __DEC64_EPSILON__ 1E-15DD
#define __ORDER_PDP_ENDIAN__ 3412
#define __DEC128_MIN_EXP__ (-6142)
#define __INT_FAST32_TYPE__ long int
#define __UINT_LEAST16_TYPE__ short unsigned int
#define unix 1
#define __INT16_MAX__ 32767
#define __SIZE_TYPE__ long unsigned int
#define __UINT64_MAX__ 18446744073709551615UL
#define __INT8_TYPE__ signed char
#define __FLT_RADIX__ 2
#define __INT_LEAST16_TYPE__ short int
#define __LDBL_EPSILON__ 1.08420217248550443401e-19L
#define __UINTMAX_C(c) c ## UL
#define __SSE_MATH__ 1
#define __k8 1
#define __SEH__ 1
#define __SIG_ATOMIC_MAX__ 2147483647
#define __GCC_ATOMIC_WCHAR_T_LOCK_FREE 2
#define __SIZEOF_PTRDIFF_T__ 8
#define __CYGWIN__ 1
#define __x86_64__ 1
#define __DEC32_SUBNORMAL_MIN__ 0.000001E-95DF
#define __INT_FAST16_MAX__ 9223372036854775807L
#define __UINT_FAST32_MAX__ 18446744073709551615UL
#define __UINT_LEAST64_TYPE__ long unsigned int
#define __FLT_HAS_QUIET_NAN__ 1
#define __FLT_MAX_10_EXP__ 38
#define __LONG_MAX__ 9223372036854775807L
#define __DEC128_SUBNORMAL_MIN__ 0.000000000000000000000000000000001E-6143DL
#define __FLT_HAS_INFINITY__ 1
#define __UINT_FAST16_TYPE__ long unsigned int
#define __DEC64_MAX__ 9.999999999999999E384DD
#define __CHAR16_TYPE__ short unsigned int
#define __PRAGMA_REDEFINE_EXTNAME 1
#define __INT_LEAST16_MAX__ 32767
#define __DEC64_MANT_DIG__ 16
#define __INT64_MAX__ 9223372036854775807L
#define __UINT_LEAST32_MAX__ 4294967295U
#define __GCC_ATOMIC_LONG_LOCK_FREE 2
#define __INT_LEAST64_TYPE__ long int
#define __INT16_TYPE__ short int
#define __INT_LEAST8_TYPE__ signed char
#define __DEC32_MAX_EXP__ 97
#define __INT_FAST8_MAX__ 127
#define __INTPTR_MAX__ 9223372036854775807L
#define __GXX_MERGED_TYPEINFO_NAMES 0
#define __stdcall __attribute__((__stdcall__))
#define __SSE2__ 1
#define __LDBL_MANT_DIG__ 64
#define __DBL_HAS_QUIET_NAN__ 1
#define __SIG_ATOMIC_MIN__ (-__SIG_ATOMIC_MAX__ - 1)
#define __k8__ 1
#define __INTPTR_TYPE__ long int
#define __UINT16_TYPE__ short unsigned int
#define __WCHAR_TYPE__ short unsigned int
#define __SIZEOF_FLOAT__ 4
#define __pic__ 1
#define __UINTPTR_MAX__ 18446744073709551615UL
#define __DEC64_MIN_EXP__ (-382)
#define __INT_FAST64_MAX__ 9223372036854775807L
#define __GCC_ATOMIC_TEST_AND_SET_TRUEVAL 1
#define __FLT_DIG__ 6
#define __UINT_FAST64_TYPE__ long unsigned int
#define __INT_MAX__ 2147483647
#define __amd64__ 1
#define __code_model_medium__ 1
#define __INT64_TYPE__ long int
#define __FLT_MAX_EXP__ 128
#define __ORDER_BIG_ENDIAN__ 4321
#define __DBL_MANT_DIG__ 53
#define __INT_LEAST64_MAX__ 9223372036854775807L
#define __GCC_ATOMIC_CHAR16_T_LOCK_FREE 2
#define __DEC64_MIN__ 1E-383DD
#define __WINT_TYPE__ unsigned int
#define __UINT_LEAST32_TYPE__ unsigned int
#define __SIZEOF_SHORT__ 2
#define __SSE__ 1
#define __LDBL_MIN_EXP__ (-16381)
#define __INT_LEAST8_MAX__ 127
#define __SIZEOF_INT128__ 16
#define __LDBL_MAX_10_EXP__ 4932
#define __ATOMIC_RELAXED 0
#define __DBL_EPSILON__ ((double)2.22044604925031308085e-16L)
#define __thiscall __attribute__((__thiscall__))
#define _LP64 1
#define __UINT8_C(c) c
#define __INT_LEAST32_TYPE__ int
#define __SIZEOF_WCHAR_T__ 2
#define __UINT64_TYPE__ long unsigned int
#define __INT_FAST8_TYPE__ signed char
#define __fastcall __attribute__((__fastcall__))
#define __DBL_DECIMAL_DIG__ 17
#define __FXSR__ 1
#define __DEC_EVAL_METHOD__ 2
#define __UINT32_C(c) c ## U
#define __INTMAX_MAX__ 9223372036854775807L
#define __BYTE_ORDER__ __ORDER_LITTLE_ENDIAN__
#define __FLT_DENORM_MIN__ 1.40129846432481707092e-45F
#define __INT8_MAX__ 127
#define __PIC__ 1
#define __UINT_FAST32_TYPE__ long unsigned int
#define __CHAR32_TYPE__ unsigned int
#define __FLT_MAX__ 3.40282346638528859812e+38F
#define __INT32_TYPE__ int
#define __SIZEOF_DOUBLE__ 8
#define __FLT_MIN_10_EXP__ (-37)
#define __INTMAX_TYPE__ long int
#define __DEC128_MAX_EXP__ 6145
#define __ATOMIC_CONSUME 1
#define __GNUC_MINOR__ 8
#define __UINTMAX_MAX__ 18446744073709551615UL
#define __DEC32_MANT_DIG__ 7
#define __DBL_MAX_10_EXP__ 308
#define __LDBL_DENORM_MIN__ 3.64519953188247460253e-4951L
#define __INT16_C(c) c
#define __STDC__ 1
#define __PTRDIFF_TYPE__ long int
#define __ATOMIC_SEQ_CST 5
#define __UINT32_TYPE__ unsigned int
#define __UINTPTR_TYPE__ long unsigned int
#define __DEC64_SUBNORMAL_MIN__ 0.000000000000001E-383DD
#define __DEC128_MANT_DIG__ 34
#define __LDBL_MIN_10_EXP__ (-4931)
#define __SIZEOF_LONG_LONG__ 8
#define __GCC_ATOMIC_LLONG_LOCK_FREE 2
#define __LDBL_DIG__ 18
#define __FLT_DECIMAL_DIG__ 9
#define __UINT_FAST16_MAX__ 18446744073709551615UL
#define __GNUC_GNU_INLINE__ 1
#define __GCC_ATOMIC_SHORT_LOCK_FREE 2
#define __UINT_FAST8_TYPE__ unsigned char
#define __ATOMIC_ACQ_REL 4
#define __ATOMIC_RELEASE 3
#define __declspec(x) __attribute__((x))
#define __WORDSIZE 64
"""
	default_include = [os.path.abspath(os.path.join(os.path.dirname(__file__), 'include')),
	                   os.path.abspath(os.path.join(os.path.dirname(__file__), 'include/posix'))]
	def __init__(me, encoding=sys.getdefaultencoding()
					, includes=[], ignore_warnings=[]
					, D=''):
		me.encoding = encoding
		me.compiler = ExecodeGeneratorLLP64()
		me.core = SyntaxCore(me.compiler)
		me.parser = Parser(me.core)
		me.preprocessor = Preprocessor(Tokenizer()
							, includes=me.default_include + includes + [r'/usr/include', ]
							, D=D + ' __extension__ __BEGIN_DECLS __END_DECLS __THROW'
							, predefined=me._defined_macro)
		me.ignore_warnings = ignore_warnings + [PreprocessWarning]
		
import os		
if os.name == 'posix':
	CCompiler = GCC
else:
	CCompiler = CompilerBase
	
if __name__ == '__main__':
	compiler = CCompiler()
	
	import inspect
	lno = inspect.currentframe().f_lineno+1
	src = r"""
	#include <stdio.h>
	#include <string.h>
	#include <stdlib.h>
	int G[3];
	char buffer[256];
	int test();
	int comp(){return 0;}
	//typedef int(*P)(void);
	//int qsort(P);
	//P x;
	int test(int n, char* p)
	{	
		static char c = 0;
		//qsort(comp);
		int size = sizeof(size);
		//const char* p = "";
		p += 1;
		p = &n;
		sprintf(buffer, "test%s\n", p);
		for(int i=0; i<n; ++i){
			printf("HelloWorld %d\n", i);
			fflush(stdout);
			//#@py: print(G)
		}
		G[0]++;
		return 0;
	}
	
	
	typedef struct{
		double x,y;
	}vector_t;
	
	int comp(const vector_t *l, const vector_t *r)
	{
		//@py: print(l[0].x, r[0].y)
		printf("x=%lf y=%lf ", l->x, l->y);
		printf("x=%lf y=%lf\n", r->x, r->y);
		if(l->x<r->x) return -1;
		if(l->x>r->x) return  1;
		if(l->y<r->y) return -1;
		if(l->y>r->y) return  1;
		return 0;
		
	}
	
	void test2(size_t size, vector_t a[])//, int(*Comp)(const void*, const void*))
	{
		for(int i=0; i<size; ++i){
			printf("%d x=%lf y=%lf\n", i, a[i].x, a[i].y);
		}
		printf("\n");
		qsort(a, size, sizeof(vector_t), comp);
		//qsort(a, size, sizeof(vector_t), Comp);
		//qsort(a, size, sizeof(vector_t), (int(*)(const void*, const void*))Comp);
		for(int i=0; i<size; ++i){
			printf("%d x=%lf y=%lf\n", i, a[i].x, a[i].y);
		}
	}
	
	
	int compi(const int *l, const int *r)
	{
		return *l - *r;
		
	}
	
	void test3(size_t size, int a[])//, int(*Comp)(const void*, const void*))
	{
		for(int i=0; i<size; ++i){
			printf("%d x=%d\n", i, a[i]);
		}
		printf("\n");
		qsort(a, size, sizeof(int), (int(*)(const void*, const void*))compi);
		for(int i=0; i<size; ++i){
			printf("%d x=%d\n", i, a[i]);
		}
	}
	
	"""
	#with warnings.catch_warnings(record=True):
	warnings.filterwarnings('error', category=NoueError)
	co = compiler.compile_source(src, __file__, lno)
	p = compiler.parse_source(src, __file__, lno, None)
	ast = compiler.compiler.dump(p)
	#for node in pyast.walk(ast[0]):
	#	if not hasattr(node, 'lineno'):
	#		print(node)
		#print(node)
	#ast = [ast[0].body[0]]
	#print()
	#print(ast[0].value.func.id)
	import recompiler
	re = recompiler.ReParser()
	for st in ast:
		re.toline(st, 0)
	#re.toline(ast[0], 0)
	#re.toline(ast[1], 0)
	#re.toline(ast[2], 0)
	
	print()
	for s in compiler.compiler.globalvarconverter.staticvarcreatecode:
		re.toline(s, 0)
	for s in compiler.compiler.globalvarconverter.staticvarinitcode:
		re.toline(s, 0)
	for s in compiler.compiler.conststring.statements:
		re.toline(s, 0)

	compiler.savecache(co, 'test.dat')
	
	from ctypes import*
	co.sprintf= cdll.msvcrt.sprintf
	co.printf = cdll.msvcrt.printf
	def printf(*args):
		#import pdb;pdb.set_trace()
		print(args)
	printf.__cfunc__ = CFUNCTYPE(c_int, *(c_voidp,)*64)(printf)
	#co.printf = printf
	co.printf = cdll.msvcrt.printf
	
	co.qsort = cdll.msvcrt.qsort
	#co.qsort = printf
	from random import random
	a = (c_int*8)()
	for i in range(8):
		a[i] = int(random()*1000)
	co.test3(c_size_t(8), a)

	
	a = (co.vector_t*8)()
	for i in range(8):
		a[i].x = random()*1000
		a[i].y = random()*1000
	co.test2(c_size_t(8), a)
	exit()
		
	co.fflush = cdll.msvcrt.fflush
	cdll.msvcrt.__iob_func.restype = c_voidp
	__iob = cdll.msvcrt.__iob_func()
	co.stdin  = c_voidp(__iob)
	co.stdout = c_voidp(__iob+48)
	#co.stdout = c_voidp(__iob+8)
	co.stderr = c_voidp(__iob+96)
	res = co.test(c_int(8), c_char_p(b''))
	print(res)
	res = co.test(c_int(8), c_char_p(b''))
	print(res)
	res = co.test(c_int(8), c_char_p(b''))
	print(res)

	compiler.loadcache('test.dat')