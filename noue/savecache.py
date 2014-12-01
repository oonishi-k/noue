#coding: utf8

import types
import copyreg
import ctypes  as pyct
import ast     as pyast
import pickle

try:
	from .codegenerator import *
except SystemError:
	import imp
	noue = imp.load_source('noue', './__init__.py')
	from noue.codegenerator import *


def build_code(code_fields):
	return types.CodeType(*code_fields)
	
def reduce_code(co):
	args = (co.co_argcount, co.co_kwonlyargcount, co.co_nlocals, co.co_stacksize,
		co.co_flags, co.co_code, co.co_consts, co.co_names, co.co_varnames,
		co.co_filename, co.co_name, co.co_firstlineno, co.co_lnotab, 
		co.co_freevars, co.co_cellvars)
	#for a in args:
	#	print(a)
	return (build_code, (args,))

copyreg.pickle(types.CodeType, reduce_code)


structs = {}
def define_struct(id, name, fileds):
	#debuglog('str', id, name)
	#print('define_struct', name, fileds)
	if id not in structs:
		structs[id] = type(name, (pyct.Structure,), {})
	structs[id]._fields_ = fileds
	return structs[id]

def define_ptr(id, name):
	#debuglog('ptr', id, name)
	if id not in structs:
		structs[id] = type(name, (pyct.Structure,), {})
	return pyct.POINTER(structs[id])

def reduce_struct(t):
	#print(t.__name__, t)
	if t == pyct.Structure:
		return 'pyct.Structure'
	if hasattr(t, '_fields_'):
		return (define_struct, (id(t), t.__name__, t._fields_))
	else:
		return (define_struct, (id(t), t.__name__, []))

copyreg.pickle(type(pyct.Structure), reduce_struct)

def reduce_ptr(t):
	#print(define_ptr, t._type_)
	if issubclass(t._type_, pyct.Structure):
		return (define_ptr, (id(t._type_), t._type_.__name__,))
	return (pyct.POINTER, (t._type_,))

copyreg.pickle(type(pyct.POINTER('')), reduce_ptr)

def reduce_array(t):
	return (pyct.ARRAY, (t._type_,t._length_))

copyreg.pickle(type(pyct.c_int*1), reduce_array)



#def reduce_cfunc(t):
#	print('yes2', t)
#	return (pyct.CFUNCTYPE(t.restype, *t.argtypes), ())
#import ctypes
#copyreg.pickle(pyct.CFUNCTYPE(ctypes.c_int).mro()[0], reduce_cfunc)
#
#
#def reduce_cfunc(t):
#	print('yes2', t)
#	if t == CNativeFuncPtr: return 'CNativeFuncPtr'
#	return (pyct.CFUNCTYPE, (t().restype,) + t().argtypes)
##	#return (print, (t().restype,) + t().argtypes)
##
#copyreg.pickle(type(pyct.CFUNCTYPE(None)), reduce_cfunc)

#def reduce_cfunc(t):
#	print('yes', t)
#	return 'CNativeFuncPtr'
#	#return (print, (t().restype,) + t().argtypes)
#
#copyreg.pickle(type(CNativeFuncPtr), reduce_cfunc)

def caches(mod):
	CData = pyct.c_int.mro()[2]
	
	d = {}
	for name,val in mod.__dict__.items():
		#if name != '__builtins__':print(name, val)
		if name == '__builtins__':
			pass
		elif isinstance(val, types.FunctionType) and val.__module__ == mod.__name__:
			#print(val, val.__module__, val.__name__)
			#if name in ('$CFUNCTYPE', '$CNativeFuncPtr'): continue
			#print(name, val.__code__)
			d[name] = (val.__code__, val.__cfunc__.restype, val.__cfunc__.argtypes)
			#d[name] = (val.__code__)
		elif name == '$$G':
			continue
		elif isinstance(val, CData):
			continue
		else:
			#if name in ('$CFUNCTYPE', '$CNativeFuncPtr'): continue
			#print(name, val)
			d[name] = val
			
	return pickle.dumps(d)


def loads(string):
	members = pickle.loads(string)
	pymod = types.ModuleType(members['__name__'])
	import builtins
	pymod.__dict__['__builtins__'] =builtins.__dict__.copy()
	
	for key,val in pyct.__dict__.items():
		if key[0] == '_': continue
		pymod.__dict__['__builtins__'][key] = val
			
	for attr,val in members.items():
		if type(val) == tuple and isinstance(val[0], types.CodeType):
			pymod.__dict__[attr] = types.FunctionType(val[0], pymod.__dict__)
			pymod.__dict__[attr].__cfunc__ = pyct.CFUNCTYPE(val[1], *val[2])(pymod.__dict__[attr])
		else:
			pymod.__dict__[attr] = val

	pymod.__dict__['$$G'] = pymod

	for s in pymod.__dict__['$$CREATECODES']:
		code = compile(pyast.Module(body=[s]), s.file, 'exec')
		exec(code, pymod.__dict__)

	for s in pymod.__dict__['$$INITCODES']:
		code = compile(pyast.Module(body=[s]), s.file, 'exec')
		exec(code, pymod.__dict__)

	return pymod

if __name__ == '__main__':
	if 1:
		import imp
		noue = imp.load_source('noue', '__init__.py')
		from noue.compiler import CCompiler
		com = CCompiler().compile('test3.c')
		print(com.__name__)
		print(com.__file__)
		s = caches(com)
		print(s)
		f = open('testdata.dat', 'wb')
		f.write(s)
		f.close()
		
		exit()
		
	else:
		import imp
		noue = imp.load_source('noue', '__init__.py')
		s = open('testdata.dat', 'rb').read()
		pymod = loads(s)
		print(pymod.vector_t())
		exit()
