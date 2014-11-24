# coding: utf8

## pythonバイトコードを書き換えて、gotoを実現する
## POP_BLOCKとかどうなるんだろうか

from struct import pack as tobin
import dis
import types
def set_goto(func):

	LOAD_GLOBAL = dis.opmap['LOAD_GLOBAL']
	POP_TOP   = dis.opmap['POP_TOP']
	LOAD_ATTR = dis.opmap['LOAD_ATTR']
	NOP       = dis.opmap['NOP']
	JUMP_ABSOLUTE = dis.opmap['JUMP_ABSOLUTE']
	SETUP_LOOP = dis.opmap['SETUP_LOOP']
	POP_BLOCK  = dis.opmap['POP_BLOCK']
	#print(tobin('b', POP_BLOCK), tobin('b', SETUP_LOOP))

	def search_points(co):
		i = 0
		
		source = {}
		target = {}
		push = []
		pop  = []
		
		while i < len(co.co_code):
			if co.co_code[i] == LOAD_GLOBAL:
				no = co.co_code[i+1] + (co.co_code[i+2]<<8)
				typ = co.co_names[no]
				if typ == set_goto.pushblock:
					push += [i]
					i += 3
					continue
				if typ == set_goto.popblock:
					pop += [i]
					i += 3
					continue
				if typ not in (set_goto.goto, set_goto.label):
					i += 3
					continue
				if co.co_code[i+3] != LOAD_ATTR:
					raise Exception()
				no = co.co_code[i+4] + (co.co_code[i+5]<<8)
				lab = co.co_names[no]
				if co.co_code[i+6] != POP_TOP:
					raise Exception()
					
				if typ == set_goto.goto:
					source[lab] = i
				elif typ == set_goto.label:
					target[lab] = i
					
				i += 7
			elif co.co_code[i] >=dis.HAVE_ARGUMENT:
				i += 3
			else:
				i += 1
		return source, target, push, pop
		
	source, target, push, pop = search_points(func.__code__)
	co_code = func.__code__.co_code
	
	for pos in push:
		co_code = co_code[:pos] + tobin('b', SETUP_LOOP) +b'\x06\x00'+ tobin('b', NOP)*3 + co_code[pos+6:]

	for pos in pop:
		co_code = co_code[:pos] + tobin('b', POP_BLOCK) + tobin('b', NOP)*3 + co_code[pos+4:]

	for lab, pos in source.items():
		co_code = co_code[:pos] + b'q' + tobin('h', target[lab]) + b'\x09'*4 + co_code[pos+7:]

	for lab, pos in target.items():
		co_code = co_code[:pos] + b'\x09'*7 + co_code[pos+7:]

	co = func.__code__
	code = types.CodeType(co.co_argcount, co.co_kwonlyargcount, co.co_nlocals, co.co_stacksize,
							  co.co_flags, co_code, co.co_consts, co.co_names, co.co_varnames,
							  co.co_filename, co.co_name, co.co_firstlineno, co.co_lnotab, 
							  co.co_freevars, co.co_cellvars)
	func = types.FunctionType(code, func.__globals__)
	return func
set_goto.goto='__goto'
set_goto.label='__label'
set_goto.popblock='__pop'
set_goto.pushblock='__push'

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
	print('test3')
	
	#@set_goto	
	def test(i):
		while 1:
			while 1:
				while 1:
					while 1:
												__push
												__goto.X
		#for i in range(3):
		if 0 and 1:
			while K:
				while K:
					while K:
						while i>0:
							while i>-3:
								__label.X
								print('coco')
								print(i)
								i -= 1
								if i == 1:
									print('coco2')
									break
				break
		else:
			print('else')
			#if i == 1:
			#	print('coco2')
			#	break
		print('test')
		print(i)
		return
	K = 0
	import dis
	dis.dis(test)
	test = set_goto(test)
	#exit()
	test(3)
