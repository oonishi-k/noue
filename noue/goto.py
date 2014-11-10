# coding: cp932

## pythonバイトコードを書き換えて、gotoを実現する
## POP_BLOCKとかどうなるんだろうか

from struct import pack as tobin
import dis
import types
def set_goto(func, goto='__goto', label='__label'):

	LOAD_GLOBAL = dis.opmap['LOAD_GLOBAL']
	POP_TOP   = dis.opmap['POP_TOP']
	LOAD_ATTR = dis.opmap['LOAD_ATTR']
	NOP       = dis.opmap['NOP']
	JUMP_ABSOLUTE = dis.opmap['JUMP_ABSOLUTE']

	def search_points(co):
		i = 0
		
		source = {}
		target = {}
		
		while i < len(co.co_code):
			if co.co_code[i] == LOAD_GLOBAL:
				no = co.co_code[i+1] + (co.co_code[i+2]<<8)
				typ = co.co_names[no]
				if typ not in (goto, label):
					i += 3
					continue
				if co.co_code[i+3] != LOAD_ATTR:
					raise Exception()
				no = co.co_code[i+4] + (co.co_code[i+5]<<8)
				lab = co.co_names[no]
				if co.co_code[i+6] != POP_TOP:
					raise Exception()
					
				if typ == goto:
					source[lab] = i
				elif typ == label:
					target[lab] = i
					
				i += 7
			elif co.co_code[i] >=dis.HAVE_ARGUMENT:
				i += 3
			else:
				i += 1
		return source, target
	source, target = search_points(func.__code__)


	co_code = func.__code__.co_code
	for label, pos in source.items():
		co_code = co_code[:pos] + b'q' + tobin('h', target[label]) + b'\x09'*4 + co_code[pos+7:]

	for label, pos in target.items():
		co_code = co_code[:pos] + b'\x09'*7 + co_code[pos+7:]

	co = func.__code__
	code = types.CodeType(co.co_argcount, co.co_kwonlyargcount, co.co_nlocals, co.co_stacksize,
							  co.co_flags, co_code, co.co_consts, co.co_names, co.co_varnames,
							  co.co_filename, co.co_name, co.co_firstlineno, co.co_lnotab, 
							  co.co_freevars, co.co_cellvars)
	func = types.FunctionType(code, func.__globals__)
	return func


if __name__ == '__main__':
	@set_goto
	def test(n):
		m = 0
		__label.FIN
		for i in range(1):
			print('yes')
			for j in range(1):
				print('yes2')
				if m == 0: 
					m = 1
					__goto.FIN
					
				print('yes3')
			print('yes4')
			continue
		
	test(0)
	
	class Context:
		def __enter__(me, *args):
			print('enter', args)
		def __exit__(me, *args):
			print('exit', args)
	import inspect 
	
	@set_goto
	def test():
		try:
			try:
				with Context() as c:
					print('yes1')
					__goto.FIN
					print('yes2')
			finally:
				print('yes5')
		finally:
			print('yes4')
		__label.FIN
		print('yes3')
		return 0
		
	test()
	
	print()
	
	@set_goto	
	def test():
		__goto.X
		for i in range(3):
			__label.X
			print(i)
			if i == 1:
				break
		print('test')
		print(i)
		return
		
	test()
