#coding: utf8
import sys
from copy import deepcopy

try:
	from .preprocessor import *
	from .syntaxtree   import *
	from .parser       import *
	from .coresyntax   import *
	from .codegenerator import *
except SystemError:
	import imp
	noue = imp.load_source('noue', './__init__.py')
	from noue.preprocessor import *
	from noue.syntaxtree   import *
	from noue.parser       import *
	from noue.coresyntax   import *
	from noue.codegenerator import *

class CCompiler:
	def __init__(me, encoding=sys.getdefaultencoding()
					, includes=[], ignore_warnings=[]):
		me.encoding = encoding
		me.compiler = ExecodeGeneratorLLP64()
		me.core = SyntaxCore(me.compiler)
		me.parser = Parser(me.core)
		me.preprocessor = Preprocessor(Tokenizer(), includes=includes)
		me.ignore_warnings = ignore_warnings
		
	def compile(me, file, encoding=None, printerror=True):
		with warnings.catch_warnings(record=True) as r:
			for iw in me.ignore_warnings:
				warnings.filterwarnings('ignore', category=iw)

			with open(file, encoding=encoding or me.encoding) as f:
				src = f.read()
				res = me.compile_source(src, file, 1, encoding=encoding or me.encoding)

		if printerror:
			for w in r:
				print(w.message.message())
				print()
		else:
			for w in r:
				warnings.warn_explicit(w.message, w.category, w.filename, w.lineno)#, r.module, r.registry)
		return res
				
	def parse(me, file, encoding=None, printerror=True):
		with warnings.catch_warnings(record=True) as r:
			for iw in me.ignore_warnings:
				warnings.filterwarnings('ignore', category=iw)

			with open(file, encoding=encoding or me.encoding) as f:
				src = f.read()
				res =  me.parse_source(src, file, 1, encoding=encoding or me.encoding)
		
		if printerror:
			for w in r:
				print(w.message.message())
				print()
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
		p = parser.parse_global()
		
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
	
if __name__ == '__main__':
	compiler = CCompiler()
	
	import inspect
	lno = inspect.currentframe().f_lineno+1
	src = r"""
	#include <stdio.h>
	int G;
	int test(int n)
	{	
		for(int i=0; i<n+G; ++i){
			printf("HelloWorld %d\n", i);
			fflush(stdout);
			//#@py: print(G)
		}
		G++;
		return 0;
	}
	"""
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
	re.toline(ast[0], 0)
	
	print()
	for s in compiler.compiler.globalvarconverter.staticvarcreatecode:
		re.toline(s, 0)
	for s in compiler.compiler.globalvarconverter.staticvarinitcode:
		re.toline(s, 0)
	for s in compiler.compiler.conststring.statements:
		re.toline(s, 0)

	from ctypes import*
	co.printf = cdll.msvcrt.printf
	co.fflush = cdll.msvcrt.fflush
	cdll.msvcrt.__iob_func.restype = c_voidp
	__iob = cdll.msvcrt.__iob_func()
	co.stdin  = c_voidp(__iob)
	co.stdout = c_voidp(__iob+48)
	#co.stdout = c_voidp(__iob+8)
	co.stderr = c_voidp(__iob+96)
	res = co.test(c_int(8))
	print(res)
	res = co.test(c_int(8))
	print(res)
	res = co.test(c_int(8))
	print(res)
	