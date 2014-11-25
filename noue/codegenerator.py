#coding: utf8
try:
	from .preprocessor import *
	from .syntaxtree import *
	from .syntaxtree import _node, _statement, _scope, _expression, _expbinop, _function_stmt, _loopBlock, _type_descriptor, _execscope, _declareVarStmt
	
	from .goto import *
except SystemError:
	import imp
	noue = imp.load_source('noue', './__init__.py')
	from noue.preprocessor import *
	from noue.syntaxtree import *
	from noue.syntaxtree import _node, _statement, _scope, _expression, _expbinop, _function_stmt, _loopBlock, _type_descriptor, _execscope, _declareVarStmt
	from noue.goto import *


import ctypes as pyct
import ast    as pyast
import types

def genuniqueid(stnode):
	seed  = tuple(map(ord, stnode.first_token.file))
	seed += (stnode.first_token.line, stnode.first_token.col)
	seed += tuple(map(ord, stnode.last_token.file))
	seed += (stnode.last_token.line, stnode.last_token.col)
	return hex(hash(seed) % (1<<64))[2:].upper()
	
def classalias(name, mro, attrs):
	for a,v in attrs.items():
		if a.startswith('__'): continue
		setattr(mro[0], a, v)
	return mro[0]

class ConstStringSolution:
	def __init__(me, typeconverter):
		me._conststrings = []
		me.typeconverter = typeconverter

	@property
	def statements(me):
		num = len(me._conststrings)
		func = pyast.BinOp(
					left=pyast.Name(id='$T$c_char_p',ctx=pyast.Load()),
					op=pyast.Mult(),
					right=pyast.Num(n=num))
		value = pyast.Call(func=func,
							args=[],
							keywords=[],
							starargs=None,
							kwargs=None,)

		ast = pyast.Assign(
					targets=[pyast.Name(
								id='$CONSTSTRING',
								ctx=pyast.Store())
					],
					value=value)
		for n in pyast.walk(ast):
			n.lineno=0
			n.col_offset=0
		return [ast] + me._conststrings
		
	def conststring(me, exp):
		num = len(me._conststrings)
		
		## const文字列をデータ領域に登録する
		## $CONSTSTRING[num] = c_char_p(b"<文字列>")
		value = value=pyast.Call(
							func=pyast.Name(
								id='$T$c_char_p',ctx=pyast.Load(),
								lineno=exp.first_token.line, col_offset=exp.first_token.col),
							args=[pyast.Bytes(s=exp.value,
											lineno=exp.first_token.line,
											col_offset=exp.first_token.col)],
							keywords=[],
							starargs=None,
							kwargs=None,
							lineno=exp.first_token.line, col_offset=exp.first_token.col)
		ast = pyast.Assign(
					targets=[
						pyast.Subscript(
							value=pyast.Name(
								id='$CONSTSTRING',
								ctx=pyast.Load(),
								lineno=exp.first_token.line, col_offset=exp.first_token.col
							),
							slice=pyast.Index(
								value=pyast.Num(n=num,
								lineno=exp.first_token.line, col_offset=exp.first_token.col
								),
								lineno=exp.first_token.line, col_offset=exp.first_token.col
							),
							ctx=pyast.Store(),
							lineno=exp.first_token.line, col_offset=exp.first_token.col
						)
					],
					value=value,
					lineno=exp.first_token.line, col_offset=exp.first_token.col)
		
		me._conststrings += [ast]
		
		## const文字列を呼び出す
		res = pyast.Subscript(
							value=pyast.Name(
								id='$CONSTSTRING',
								ctx=pyast.Load(),
								lineno=exp.first_token.line, col_offset=exp.first_token.col
							),
							slice=pyast.Index(
								value=pyast.Num(n=num,
								lineno=exp.first_token.line, col_offset=exp.first_token.col
								),
								lineno=exp.first_token.line, col_offset=exp.first_token.col
							),
							ctx=pyast.Load(),
							lineno=exp.first_token.line, col_offset=exp.first_token.col
						)
		return res

class GlobalVarConverter:
	def __init__(me, typeconverter, exprconverter):
		me._conststrings = []
		me.typeconverter = typeconverter
		me.exprconverter  = exprconverter
		me.staticvarinitcode = []
		me.staticvarcreatecode = []
		
		
		
	#def conststring(me, cs):
	#	ctype = me.typeconverter.cnvtype(cs.restype)
	#	res = len(me._conststrings)
	#	me._conststrings += [ctype(*tuple(cs.value))]
	#	return '$CONSTSTR#%d'%res

		
	def globalinit(me, stmt, id):
		
		create = copy = pyast.Call(
						func=me.typeconverter.typecall(stmt.restype, stmt.first_token),
						args=[],
						keywords=[],
						starargs=None,
						kwargs=None,
						lineno = stmt.first_token.line,col_offset=stmt.first_token.col)
						
		ast = pyast.Assign(
					targets=[
						pyast.Name(
							id=id,ctx=pyast.Store(),
							lineno=stmt.first_token.line, col_offset=stmt.first_token.col),
					],
					value=create,
					lineno=stmt.first_token.line, col_offset=stmt.first_token.col
				)
				
		me.staticvarcreatecode += [ast]
		
		value = me.exprconverter.construct(stmt.restype, stmt.initexp, stmt.first_token)
		#if stmt.initexp:
		#	value = me.exprconverter.construct(stmt.restype, stmt.initexp, stmt.first_token)
		#else:
		#	value = copy = pyast.Call(
		#					func=me.typeconverter.typecall(stmt.restype, stmt.first_token),
		#					args=[],
		#					keywords=[],
		#					starargs=None,
		#					kwargs=None,
		#					lineno = stmt.first_token.line,col_offset=stmt.first_token.col)
							
		ptr = copy = pyast.Call(
						func=pyast.Name(
									id='$pointer',ctx=pyast.Load(),
									lineno=stmt.first_token.line, col_offset=stmt.first_token.col),
						args=[pyast.Name(
									id=id,ctx=pyast.Load(),
									lineno=stmt.first_token.line, col_offset=stmt.first_token.col)],
						keywords=[],
						starargs=None,
						kwargs=None,
						lineno = stmt.first_token.line,col_offset=stmt.first_token.col)

		ast = pyast.Assign(
					targets=[
						pyast.Subscript(
							value=ptr,
							slice=pyast.Index(
								value=pyast.Num(n=0,
									lineno=stmt.first_token.line, col_offset=stmt.first_token.col),
								lineno=stmt.first_token.line, col_offset=stmt.first_token.col
							),
							ctx=pyast.Store(),
							lineno=stmt.first_token.line, col_offset=stmt.first_token.col
						)
					],
					value=value,
					lineno=stmt.first_token.line, col_offset=stmt.first_token.col
				)
		ast.file = stmt.first_token.file
		me.staticvarinitcode += [ast]
		
		
	def getuniqueid(me, stmt):
		return stmt.__getuniqueid(me)
		
	def __getuniqueid(stmt, me):
		return '$S$%s$'%stmt.id + genuniqueid(stmt)
	LocalStaticStmt.__getuniqueid = __getuniqueid
	
	def __getuniqueid(stmt, me):
		return '$S$%s$'%stmt.id + genuniqueid(stmt)
	GlobalStaticStmt.__getuniqueid = __getuniqueid
	
	def __getuniqueid(stmt, me):
		return '$L$%s$'%stmt.id + genuniqueid(stmt)
	LocalVarStmt.__getuniqueid = __getuniqueid
	
	
	

	
	def compile(me, stmt):
		if stmt.haserror:
			return []
		return stmt.__compile(me)
		
	def __compile(stmt, me):
		id = stmt.id
		me.globalinit(stmt, id)
	
		return []
	GlobalVarStmt.__compile = __compile
	
	def __compile(stmt, me):
		return []
	GlobalExtern.__compile = __compile
	
	
	def __compile(stmt, me):
		#res = me.localvarbackup(stmt)
		
		value = me.exprconverter.construct(stmt.restype, stmt.initexp, stmt.first_token)
		ast = pyast.Assign(
					targets=[
						pyast.Name(
							id=stmt.id,ctx=pyast.Store(),
							lineno=stmt.first_token.line, col_offset=stmt.first_token.col),
						pyast.Name(
							id=me.getuniqueid(stmt),ctx=pyast.Store(),
							lineno=stmt.first_token.line, col_offset=stmt.first_token.col),
					],
					value=value,
					lineno=stmt.first_token.line, col_offset=stmt.first_token.col
				)
		return [ast]
	LocalVarStmt.__compile = __compile
	
	def __compile(stmt, me):
		id = me.getuniqueid(stmt)
		me.globalinit(stmt, id)
		#res = me.localvarbackup(stmt)
		value = pyast.Name(
					id=me.getuniqueid(stmt),ctx=pyast.Load(),
					lineno=stmt.first_token.line, col_offset=stmt.first_token.col)
		ast = pyast.Assign(
					targets=[
						pyast.Name(
							id=stmt.id,ctx=pyast.Store(),
							lineno=stmt.first_token.line, col_offset=stmt.first_token.col),
					],
					value=value,
					lineno=stmt.first_token.line, col_offset=stmt.first_token.col
				)
		return [ast]
	
	LocalStaticStmt.__compile = __compile	
	
	def __compile(stmt, me):
		return []
	LocalExtern.__compile = __compile	
	
	
	def __compile(stmt, me):
		id = stmt.id
		me.globalinit(stmt, id)

		return []
	GlobalStaticStmt.__compile = __compile
	
	def rollbackname(me, stmt, token):
		return stmt.__rollbackname(me, token)
		
	def __rollbackname(stmt, me, token):
		return pyast.Assign(
				targets=[
					pyast.Name(
						id=stmt.id,ctx=pyast.Store(),
						lineno=token.line, col_offset=token.col),
				],
				value=pyast.Name(
						id=me.getuniqueid(stmt),ctx=pyast.Load(),
						lineno=token.line, col_offset=token.col),
				lineno=token.line, col_offset=token.col
			)
	LocalVarStmt.__rollbackname = __rollbackname
	LocalStaticStmt.__rollbackname = __rollbackname

	
	def getfuncscope(me, stmt):
		p = stmt.parent
		while isinstance(p, _execscope):
			if isinstance(p, DefineFunctionStmt):
				return p
			p = p.parent
		else:
			raise FatalError()

	



class ExpressionConverter:
	def __init__(me, typeconverter, conststring):
		me.typeconverter = typeconverter
		me.conststring = conststring
		
	def compilelist(me, values):
		res = []
		for v in values:
			if type(v) == list:
				r = me.compilelist(v)
				r = pyast.Tuple(elts=r, ctx=pyast.Load(), lineno=v[0].first_token.line, col_offset=v[0].first_token.col)
			else:
				r = me.compile(me.toright(v))
			res += [r]
		return res

	def uninitiallized_varsizedarray(me, restype, token):
		typ  = me.typeconverter.typecall(strip_options(restype)._type, token)
		size = me.compile(me.toright(restype._size))
		call = pyast.BinOp(
			left=typ,
			op=pyast.Mult(),
			right=size,
			lineno=token.line,col_offset=token.col)
		return pyast.Call(
					func=call,
					args=[],
					keywords=[],
					starargs=None,
					kwargs=None,
					lineno=token.line,col_offset=token.col)

		
		
	def uninitiallized(me, restype, token):
			if is_varsizedarray(restype):
				return me.uninitiallized_varsizedarray(restype, token)
			size = me.typeconverter.sizeof(restype)
			value =pyast.Call(
								func=pyast.Name(
									id='$c_buffer',
									ctx=pyast.Load(),
									lineno=token.line,col_offset=token.col
								),
								args=[
									pyast.BinOp(
										left=pyast.Bytes(s=b'\xbc',
												lineno=token.line,col_offset=token.col),
										op=pyast.Mult(),
										right=pyast.Num(
											n=size,
											lineno=token.line,col_offset=token.col),
										lineno=token.line,col_offset=token.col
									),
									pyast.Num(
										n=size,
										lineno=token.line,col_offset=token.col),
								],
								keywords=[],
								starargs=None,
								kwargs=None,
								lineno=token.line,col_offset=token.col)
			typeast = me.typeconverter.typecall(restype, token)
			ast = pyast.Call(
					 func=pyast.Attribute(
						 value=typeast,
						 attr='from_buffer',
						 ctx=pyast.Load(),
						 lineno = token.line,col_offset=token.col),
					 args=[value],
					 keywords=[],starargs=None,kwargs=None,
					 lineno = token.line,col_offset=token.col)
			return ast
		
		
	def construct(me, restype, init, token):
		if type(init) == list:
			values = me.compilelist(init)
		elif is_expression(init):
			if isinstance(init, ConstString):
				if is_sizedarray(restype):
					val = me.conststring.conststring(init)
					copy = pyast.Call(
						func=me.typeconverter.typecall(init.restype, init.first_token),
						args=[],
						keywords=[],
						starargs=pyast.Call(
							func=pyast.Name(
								id='tuple',
								ctx=pyast.Load(),
								lineno = init.first_token.line,col_offset=init.first_token.col
							),
							args=[val],
							keywords=[],
							starargs=None,
							kwargs=None,
							lineno = init.first_token.line,col_offset=init.first_token.col
						),
						kwargs=None,
						lineno = init.first_token.line,col_offset=init.first_token.col
					)
					return copy
				else:
					values = [me.compile(me.toright(init))]
			else:
				#values = [me.compile(me.toright(init))]
				value = me.compile(me.toright(init))
				return me.typeconverter.fromright(init.restype, value, init.first_token)
		elif init is None:
			ast = me.uninitiallized(restype, token)
			#size = me.typeconverter.sizeof(restype)
			#value = value=pyast.Call(
			#					func=pyast.Name(
			#						id='c_buffer',
			#						ctx=pyast.Load(),
			#						lineno=token.line,col_offset=token.col
			#					),
			#					args=[
			#						pyast.BinOp(
			#							left=pyast.Bytes(s=b'\xbc',
			#									lineno=token.line,col_offset=token.col),
			#							op=pyast.Mult(),
			#							right=pyast.Num(
			#								n=size,
			#								lineno=token.line,col_offset=token.col),
			#							lineno=token.line,col_offset=token.col
			#						),
			#						pyast.Num(
			#							n=size,
			#							lineno=token.line,col_offset=token.col),
			#					],
			#					keywords=[],
			#					starargs=None,
			#					kwargs=None,
			#					lineno=token.line,col_offset=token.col)
			#typeast = me.typeconverter.typecall(restype, token)
			#ast = pyast.Call(
			#		 func=pyast.Attribute(
			#			 value=typeast,
			#			 attr='from_buffer',
			#			 ctx=pyast.Load(),
			#			 lineno = token.line,col_offset=token.col),
			#		 args=[value],
			#		 keywords=[],starargs=None,kwargs=None,
			#		 lineno = token.line,col_offset=token.col)
			return ast

		
		typeast = me.typeconverter.typecall(right_type(restype), token)
		ast = pyast.Call(func=typeast,
				args=values,keywords=[],
				starargs=None,
				kwargs=None,
				lineno=token.line, col_offset=token.col)
		return ast
		

	def compile(me, node):
		return node.__compile(me)
		
	def __compile(exp, me):
		print(exp, exp.first_token.file, exp.first_token)
		print(exp.first_token.line_string)
		import pdb;pdb.set_trace()
		raise FatalError()
	_expression.__compile = __compile
	
	def __compile(exp, me):
		ass = Assign(exp.left, BinOp(exp.left.restype, exp.op[:-1], exp.left, exp.right))
		return me.compile(ass)
	ArgedAssign.__compile = __compile
	
	def __compile(exp, me):
		value  = me.compile(me.toright(exp.value))
		target = me.compile(exp.value)
		if is_numeric(exp.value.restype):
			incl   = me.compile(BinOp(exp.value.restype, exp.op[:-1], exp.value, ConstInteger(TD_INT, 1, exp.value.first_token)))
		else:
			incl   = me.compile(PtrAdd(exp.op[:-1], exp.value, ConstInteger(TD_INT, 1, exp.value.first_token)))
		assign = me.typeconverter.assign(exp.value.restype, target, incl)
		ast = pyast.Subscript(
					value=pyast.Tuple(
						elts=[value, assign],
						ctx=pyast.Load(),
						lineno=exp.first_token.line, col_offset=exp.first_token.col),
					slice=pyast.Index(value=pyast.Num(n=0,lineno=exp.first_token.line, col_offset=exp.first_token.col)
								, lineno=exp.first_token.line, col_offset=exp.first_token.col),
					ctx=pyast.Load(),
					lineno=exp.first_token.line, col_offset=exp.first_token.col)
		return ast
	PostIncl.__compile = __compile
	
	def __compile(exp, me):
		if is_numeric(exp.value.restype):
			incl = BinOp(exp.value.restype, exp.op[:-1], exp.value, ConstInteger(TD_INT, 1, exp.value.first_token))
		else:
			incl = PtrAdd(exp.op[:1], exp.value, ConstInteger(TD_INT, 1, exp.value.first_token))

		ass = Assign(exp.value, incl)
		return me.compile(ass)
	PreIncl.__compile = __compile
	
	def __compile(exp, me):
		value=pyast.Attribute(
			 value=pyast.Name(id='$G',
					ctx=pyast.Load(),
					lineno=exp.first_token.line, col_offset=exp.first_token.col),
			 attr=exp.id,
			 ctx=pyast.Load(),
			 lineno=exp.first_token.line, col_offset=exp.first_token.col)
			 
		func = me.typeconverter.typecall(exp.restype, exp.first_token)
		
		return pyast.Call(
				func=func,
				args=[value],keywords=[],
				starargs=None,
				kwargs=None,
				lineno=exp.first_token.line, col_offset=exp.first_token.col
			)
		
		
	ConstFunctionAddress.__compile = __compile
	
	def __compile(exp, me):
		#if exp.func.id == 'find':
		#	print(exp.args)
		#	raise
		#print(exp.func, exp.func.id)
		func=pyast.Attribute(
			 value=pyast.Name(id='$G',
					ctx=pyast.Load(),
					lineno=exp.first_token.line, col_offset=exp.first_token.col),
			 attr=exp.func.id,
			 ctx=pyast.Load(),
			 lineno=exp.first_token.line, col_offset=exp.first_token.col)

		if not exp.args:
			return pyast.Call(
				func=func,
				args=[],keywords=[],
				starargs=None,
				kwargs=None,
				lineno=exp.first_token.line, col_offset=exp.first_token.col
			)
			
		prototype = exp.func.restype.prototype
		if len(exp.args) == 1:
			arg = exp.args[0]
			if prototype.args:
				argtyp = strip_options(prototype.args[0].restype)
				if strip_options(arg.restype) != argtyp:
					arg = ImplicitCast(argtyp, exp.args[0])
					
				
			arg = me.copyfromright(arg)
			return pyast.Call(
				func=func,
				args=[arg],keywords=[],
				starargs=None,
				kwargs=None,
				lineno=exp.first_token.line, col_offset=exp.first_token.col
			)
		
		args = []
		if prototype.args is None:
			for arg in exp.args[::-1]:
				args += [me.copyfromright(arg)]
		else:
			if prototype.has_vararg:
				for arg in exp.args[len(prototype.args):][::-1]:
					args += [me.copyfromright(arg)]
			for arg,argdef in reversed(list(zip(exp.args, prototype.args))):
				argtyp = strip_options(argdef.restype)
				if strip_options(arg.restype) != argtyp:
					arg = ImplicitCast(argtyp, arg)
				args += [me.copyfromright(arg)]
			
		return pyast.Call(
			func=func,
			args=[],keywords=[],
			starargs=pyast.Subscript(
				value=pyast.Tuple(
					elts=args,
					ctx=pyast.Load(),
					lineno=exp.first_token.line, col_offset=exp.first_token.col
				),
				slice=pyast.Slice(
					lower=None,
					upper=None,
					step=pyast.UnaryOp(
						op=pyast.USub(),
						operand=pyast.Num(n=1,
										lineno=exp.first_token.line, col_offset=exp.first_token.col),
						lineno=exp.first_token.line, col_offset=exp.first_token.col
					),
					lineno=exp.first_token.line, col_offset=exp.first_token.col
				),
				ctx=pyast.Load(),
				lineno=exp.first_token.line, col_offset=exp.first_token.col
			),
			kwargs=None,
			lineno=exp.first_token.line, col_offset=exp.first_token.col
		)
	CallFunc.__compile = __compile
	
	
	def __compile(exp, me):
		target = me.compile(exp.left)
		value  = me.compile(me.toright(exp.right))
		assign = me.typeconverter.assign(exp.restype, target, value)
		ast = pyast.Subscript(
					value=pyast.Tuple(
						elts=[assign, target],
						ctx=pyast.Load(),
						lineno=exp.first_token.line, col_offset=exp.first_token.col),
					slice=pyast.Index(value=pyast.Num(n=1,lineno=exp.first_token.line, col_offset=exp.first_token.col)
								, lineno=exp.first_token.line, col_offset=exp.first_token.col),
					ctx=pyast.Load(),
					lineno=exp.first_token.line, col_offset=exp.first_token.col)
		return ast
	Assign.__compile = __compile
		
	class _RightValueCast(_expression):
		def __init__(me, value):
			_expression.__init__(me, right_type(value.restype), value.first_token, value.last_token)
			me.value = value
	
	def __compile(exp, me):
		ast = me.compile(exp.value)
		return me.typeconverter.toright(exp.restype, ast)
	_RightValueCast.__compile = __compile
	
	
	def toright(me, exp):
		res = exp  if not is_lefttype(exp.restype)  else me._RightValueCast(exp)
		return res
		
	def copyfromright(me, exp):
		ast = me.compile(me.toright(exp))
		ast = me.typeconverter.fromright(strip_options(exp.restype), ast, exp.first_token)
		return ast
		
	
	def __compile(exp, me):
		owner = exp.owner
		if not is_lefttype(owner.restype):
			owner = me.copyfromright(owner)
			
		attr = ID(exp.attr, exp.first_token.file, exp.first_token.line, exp.first_token.col, exp.first_token.line_string)
		value = Arrow(exp.restype, Addressof(exp.first_token, owner), attr)
		ast = me.compile(value)
		#return exp.restype.__toright(ast)
		return ast
	Dot.__compile = __compile
	
	
	def __compile(exp, me):
		
		struct = right_type(target_type(exp.owner.restype))
		
		offset = me.typeconverter.offsetattr(struct, exp.attr)
		
		cast = ImplicitCast(TD_SIZE_T, exp.owner)
		addr = BinOp(TD_SIZE_T, '+', cast, ConstInteger(TD_SIZE_T, offset, exp.last_token))
		cast = ImplicitCast(pointer_type(exp.restype), addr)
		dref = Dereference(exp.first_token, cast)
		
		ast = me.compile(dref)
		return ast
		
	Arrow.__compile = __compile
	
	def __compile(exp, me):
		
		add = PtrAdd('+', exp.owner, exp.index)
		dref = Dereference(exp.first_token, add)
		
		ast = me.compile(dref)
		return ast
		
	Index.__compile = __compile
	
			
	def __compile(exp, me):
		ast = me.compile(me.toright(exp.value))
		if is_integer(exp.restype) and is_real(exp.value.restype):
			ast = pyast.Call(
					 func=pyast.Name(id='int',
										ctx=pyast.Load(),
										lineno = exp.first_token.line,col_offset=exp.first_token.col),
					 args=[ast],
					 keywords=[],starargs=None,kwargs=None,
					 lineno = exp.first_token.line,col_offset=exp.first_token.col)
		return ast
	Cast.__compile = __compile
	
	
	def __compile(exp, me):
		return pyast.Num(
					n = int(exp.value),
					lineno = exp.first_token.line,col_offset=exp.first_token.col)
					
	ConstInteger.__compile = __compile
	
	def __compile(exp, me):
		return pyast.Num(
					n = ord(exp.value),
					lineno = exp.first_token.line,col_offset=exp.first_token.col)
					
	ConstChar.__compile = __compile
	
	def __compile(exp, me):
		return pyast.Num(
					n = exp.value,
					lineno = exp.first_token.line,col_offset=exp.first_token.col)
					
	ConstReal.__compile = __compile
	
	
	def __compile(exp, me):
		## cast((c_char*SIZE)(*tuple($CONSTSTRING[index])), c_voidp).value or 0
		val = me.conststring.conststring(exp)
		
		copy = pyast.Call(
			func=me.typeconverter.typecall(exp.restype, exp.first_token),
			args=[],
			keywords=[],
			starargs=pyast.Call(
				func=pyast.Name(
					id='tuple',
					ctx=pyast.Load(),
					lineno = exp.first_token.line,col_offset=exp.first_token.col
				),
				args=[
					val
				],
				keywords=[],
				starargs=None,
				kwargs=None,
				lineno = exp.first_token.line,col_offset=exp.first_token.col
			),
			kwargs=None,
			lineno = exp.first_token.line,col_offset=exp.first_token.col
		)
		
		cast = pyast.Call(
				 func=pyast.Name(id='$cast',#me.pyfunc('addressof'),
									ctx=pyast.Load(),
									lineno = exp.first_token.line,col_offset=exp.first_token.col),
				 args=[copy, me.typeconverter.typecall(TD_VOIDP, exp.first_token)],
				 keywords=[],starargs=None,kwargs=None,
				 lineno = exp.first_token.line,col_offset=exp.first_token.col)
		value=pyast.BoolOp(
			op=pyast.Or(),
			values=[
				pyast.Attribute(
					value=cast,
					attr='value',
					ctx=pyast.Load(),
					lineno = exp.first_token.line,col_offset=exp.first_token.col
				),
				pyast.Num(n=0,
						lineno = exp.first_token.line,col_offset=exp.first_token.col),
			],
			lineno = exp.first_token.line,col_offset=exp.first_token.col
		)
		return value
	ConstString.__compile = __compile
	
	def __compile(exp, me):
		leftast  = me.compile(me.toright(exp.left))
		rightast = me.compile(me.toright(exp.right))
		
		op = {'==':pyast.Eq(), '!=':pyast.NotEq(), '<':pyast.Lt(), '>':pyast.Gt(),
			'>=':pyast.GtE(), '<=':pyast.LtE()}[exp.op]
		
		return pyast.Compare(
					left=leftast,
					ops=[op],
					comparators=[rightast],
					lineno = exp.first_token.line,col_offset=exp.first_token.col
				)
					
	BinCompare.__compile = __compile
	
	def __compile(exp, me):
		leftast  = me.compile(me.toright(exp.left))
		rightast = me.compile(me.toright(exp.right))
		
		op = {'&&':pyast.And(), '||':pyast.Or()}[exp.op]
		
		return pyast.BoolOp(
					op=op,
					values=[leftast,rightast],
					lineno = exp.first_token.line,col_offset=exp.first_token.col
				)
					
	BinLogical.__compile = __compile
	
	def __compile(exp, me):
		if exp.op == "+":
			return me.compile(me.toright(exp.value))
		elif exp.op == "-":
			return pyast.UnaryOp(op=pyast.USub(), operand=me.compile(me.toright(exp.value))
									, lineno=exp.value.first_token.line, col_offset=exp.value.first_token.col)
		elif exp.op == "!":
			value = pyast.UnaryOp(op=pyast.Not(), operand=me.compile(me.toright(exp.value))
									, lineno=exp.value.first_token.line, col_offset=exp.value.first_token.col)
			return pyast.Call(
				func=pyast.Name(
					id='int',
					ctx=pyast.Load(),
					lineno=exp.value.first_token.line, col_offset=exp.value.first_token.col
				),
				args=[value],
				keywords=[
				],
				starargs=None,kwargs=None,
				lineno=exp.value.first_token.line, col_offset=exp.value.first_token.col)
			
		print(exp.op)
		raise FatalError()
		return pyast.Num(
					n = int(exp.value),
					lineno = exp.first_token.line,col_offset=exp.first_token.col)
					
	UnaryOp.__compile = __compile
	
	
	
	def __compile(exp, me):
		value = me.compile(me.toright(exp.value))
		typeast = me.typeconverter.typecall(right_type(exp.restype), exp.first_token)
		ast = pyast.Call(
				 func=pyast.Attribute(
					 value=typeast,
					 attr='from_address',
					 ctx=pyast.Load(),
					 lineno = exp.first_token.line,col_offset=exp.first_token.col),
				 args=[value],
				 keywords=[],starargs=None,kwargs=None,
				 lineno = exp.first_token.line,col_offset=exp.first_token.col)

		return ast
		
	Dereference.__compile = __compile
	
	
	def __compile(exp, me):
		value  = me.compile(exp.value)
		ast = pyast.Call(
				 func=pyast.Name(id='$addressof',#me.pyfunc('addressof'),
									ctx=pyast.Load(),
									lineno = exp.first_token.line,col_offset=exp.first_token.col),
				 args=[value],
				 keywords=[],starargs=None,kwargs=None,
				 lineno = exp.first_token.line,col_offset=exp.first_token.col)
		return ast
	Addressof.__compile = __compile
	
	def __compile(exp, me):
		ast = pyast.Name(
					id=exp.id,
					ctx=pyast.Load(),
					lineno = exp.first_token.line,
					col_offset=exp.first_token.col,
				)
		return ast
	VarLocal.__compile = __compile
	VarArg.__compile   = __compile
	VarStaticLocal.__compile   = __compile
	
	def __compile(exp, me):
		value = pyast.Name(
					id='$G',
					ctx=pyast.Load(),
					lineno = exp.first_token.line,
					col_offset=exp.first_token.col,
				)
		ast=pyast.Attribute(
			value=value,
			attr=exp.id,
			ctx=pyast.Load(),
			lineno=exp.first_token.line,
			col_offset=exp.first_token.col)

		return ast
	VarGlobal.__compile = __compile
	VarStaticGlobal.__compile   = __compile
	
	def __compile(exp, me):
		vars = []
		for v in exp.vars:
			vars += [me.compile(v)]
		return pyast.Tuple(
					elts=vars,
					ctx=pyast.Load(),
					lineno = exp.first_token.line,
					col_offset=exp.first_token.col)
		
		if not is_integer(exp.restype) and exp.op == '/':
			 op = pyast.Div()
		else:
			op = {
				'+':  pyast.Add(), '-':  pyast.Sub(), '*': pyast.Mult(), '/': pyast.FloorDiv(), '%': pyast.Mod(),
				'<<': pyast.LShift(), '>>': pyast.RShift(), '&': pyast.BitAnd(), '|': pyast.BitOr(), '^': pyast.BitXor(),
			}[exp.op]
		
		ast = pyast.BinOp(
					left=leftast,
					op=op,
					right=rightast,
					lineno = exp.first_token.line,
					col_offset=exp.first_token.col
				)
		return ast
	Comma.__compile = __compile
	
	def __compile(exp, me):
		leftast  = me.compile(me.toright(exp.left))
		rightast = me.compile(me.toright(exp.right))
		
		if not is_integer(exp.restype) and exp.op == '/':
			 op = pyast.Div()
		else:
			op = {
				'+':  pyast.Add(), '-':  pyast.Sub(), '*': pyast.Mult(), '/': pyast.FloorDiv(), '%': pyast.Mod(),
				'<<': pyast.LShift(), '>>': pyast.RShift(), '&': pyast.BitAnd(), '|': pyast.BitOr(), '^': pyast.BitXor(),
			}[exp.op]
		
		ast = pyast.BinOp(
					left=leftast,
					op=op,
					right=rightast,
					lineno = exp.first_token.line,
					col_offset=exp.first_token.col
				)
		return ast
	BinOp.__compile = __compile
	
	
	def __compile(exp, me):
		leftast  = me.compile(me.toright(exp.left))
		rightast = me.compile(me.toright(exp.right))
		
		size = me.typeconverter.sizeof(target_type(exp.left.restype))
		rightast = pyast.BinOp(
					left=rightast,
					op=pyast.Mult(),
					right=pyast.Num(n=size, lineno = exp.first_token.line,col_offset=exp.first_token.col),
					lineno = exp.first_token.line,
					col_offset=exp.first_token.col
				)
		
		ast = pyast.BinOp(
					left=leftast,
					op=pyast.Add(),
					right=rightast,
					lineno = exp.first_token.line,
					col_offset=exp.first_token.col
				)
		return ast
	PtrAdd.__compile = __compile
	
	def __compile(exp, me):
		leftast  = me.compile(me.toright(exp.left))
		rightast = me.compile(me.toright(exp.right))
		
		leftast = pyast.BinOp(
					left=leftast,
					op=pyast.Sub(),
					right=rightast,
					lineno = exp.first_token.line,
					col_offset=exp.first_token.col
				)
		
		size = me.typeconverter.sizeof(target_type(exp.left.restype))
		ast = pyast.BinOp(
					left=leftast,
					op=pyast.FloorDiv(),
					right=pyast.Num(n=size, lineno = exp.first_token.line,col_offset=exp.first_token.col),
					lineno = exp.first_token.line,
					col_offset=exp.first_token.col
				)
		
		return ast
	PtrSub.__compile = __compile
	
	
	def __compile(exp, me):
		test = me.compile(me.toright(exp.test))
		true = me.compile(me.toright(exp.true))
		false= me.compile(me.toright(exp.false))
		return pyast.IfExp(
					test=test,
					body=true,
					orelse=false,
					lineno = exp.first_token.line,
					col_offset=exp.first_token.col)
	Three.__compile = __compile
	

class TypeConverter:
	def __init__(me):
		me.usertypes = []
		me.primitives = [
			TD_INT,  TD_LONG,  TD_CHAR,  TD_SHORT,  TD_LONGLONG, 
			TD_UINT, TD_ULONG, TD_UCHAR, TD_USHORT, TD_ULONGLONG, 
			TD_SIZE_T, TD_WCHAR, TD_DOUBLE, TD_FLOAT,
			pointer_type(TD_CHAR), pointer_type(const_type(TD_CHAR)),
			TD_VOIDP, TD_CVOIDP
		]
		
	def setnames(me, dict):
		for p in me.primitives:
			if p == pointer_type(const_type(TD_VOID)):
				import pdb;pdb.set_trace()
			dict[p.__typename] = me.cnvtype(p)
			dict[p.__typename[2:]] = me.cnvtype(p)
		me.primitives = []
		for t in me.usertypes:
			dict[t.__typename] = me.cnvtype(t)
		me.usertypes = []
		
	def sizeof(me, restype):
		if is_errortype(restype): return 0
		return pyct.sizeof(me.cnvtype(restype))
		
	def fromright(me, restype, ast, token):
		return restype.__fromright(me, ast, token)
		
	def __fromright(td, me, value, token):
		ast = pyast.Call(
				 func=me.typecall(td, token),
				 args=[value],
				 keywords=[],starargs=None,kwargs=None,
				 lineno = token.line,col_offset=token.col)
		#return td._type.__toright(ast)
		return ast
	td_primitive.__fromright = __fromright
	
	def __fromright(td, me, value, token):
		return value
	td_struct.__fromright = __fromright

	
	def __fromright(td, me, value, token):
		return me.fromright(td._type, value, token)
	td_const.__fromright = __fromright
	
	def __fromright(td, me, value, token):
		return me.fromright(td._type, value, token)
	td_leftvalue.__fromright = __fromright
	
	def __fromright(td, me, value, token):
		ast = pyast.Call(
				func=pyast.Attribute(
					value=me.typecall(td, token),
					attr='from_address',
					ctx=pyast.Load(),
					lineno=token.line,
					col_offset=token.col),
				 args=[value],
				 keywords=[],starargs=None,kwargs=None,
				 lineno = token.line,col_offset=token.col)
		#return td._type.__toright(ast)
		return ast
	td_sized_array.__fromright = __fromright
	td_unsized_array.__fromright = __fromright
	td_varsized_array.__fromright = __fromright
	
	def __fromright(td, me, value, token):
		value = me.fromright(TD_SIZE_T, value, token)
		ast = pyast.Call(
				func=pyast.Attribute(
					value=me.typecall(td, token),
					attr='from_buffer',
					ctx=pyast.Load(),
					lineno=token.line,
					col_offset=token.col),
				 args=[value],
				 keywords=[],starargs=None,kwargs=None,
				 lineno = token.line,col_offset=token.col)
		#return td._type.__toright(ast)
		return ast
	td_pointer.__fromright = __fromright
	td_funcptr.__fromright = __fromright
		
	def typecall(me, restype, token):
		try:
			name = restype.__typename
			return pyast.Name(id=name,
							ctx=pyast.Load(),
							lineno = token.line,col_offset=token.col
				)
		except AttributeError:
			pass
		return restype.__typecall(me, token)
	pointer_type(TD_CHAR).__typename = '$T$c_char_p'
	pointer_type(const_type(TD_CHAR)).__typename = '$T$c_char_p'
	TD_VOIDP.__typename = '$T$c_voidp'
	TD_CVOIDP.__typename = '$T$c_voidp'
	
	def __typecall(restype, me, token):
		return me.typecall(restype._type, token)
	td_const.__typecall = __typecall
		
	def __typecall(restype, me, token):
		try:
			name = restype.__typename
		except AttributeError:
			#restype.__typename = genuniqueid(_statement(token, token))
			restype.__typename = '$T$%s$%s'%(restype.name, genuniqueid(_statement(token, token)))
			name = restype.__typename
			me.usertypes += [restype]
		return pyast.Name(id=name,
						ctx=pyast.Load(),
						lineno = token.line,col_offset=token.col
			)
	td_struct.__typecall = __typecall
	td_union.__typecall = __typecall
	
	def __typecall(restype, me, token):
			res  = me.typecall(restype.prototype.restype, token)
			args = [me.typecall(arg.restype, token) for arg in restype.prototype.args]
			return pyast.Call(
			func=pyast.Name(id='$CFUNCTYPE',
							ctx=pyast.Load(),
							lineno=token.line,
							col_offset=token.col),
			args=[res] + args,
			keywords=[],
			starargs=None,
			kwargs=None,
			lineno=token.line,
			col_offset=token.col)

		
	td_funcptr.__typecall = __typecall
	
			
	def __typecall(restype, me, token):
		nameast = me.typecall(restype._type, token)
		return pyast.Call(
				func=pyast.Name(
					 id='$POINTER',
					 ctx=pyast.Load(),
					lineno=token.line,col_offset=token.col),
				args=[
					nameast
				],
				keywords=[],
				starargs=None,
				kwargs=None,
				lineno=token.line,col_offset=token.col)

	td_pointer.__typecall = __typecall
	
	def __typecall(restype, me, token):
		return pyast.BinOp(
				left=me.typecall(restype._type, token),
				op = pyast.Mult(),
				right=pyast.Num(n=restype._size,lineno=token.line,col_offset=token.col),
				lineno=token.line,col_offset=token.col)

	td_sized_array.__typecall = __typecall
	
	def __typecall(restype, me, token):
		return pyast.BinOp(
				left=me.typecall(restype._type, token),
				op = pyast.Mult(),
				right=pyast.Num(n=1000,lineno=token.line,col_offset=token.col),
				lineno=token.line,col_offset=token.col)

	td_unsized_array.__typecall = __typecall
	td_varsized_array.__typecall = __typecall
		
	def cnvtype(me, typ):
		try:
			return typ.__ctype
		except AttributeError:
			pass
		return typ.__cnvtype(me)
		
	def __cnvtype(typ, me):
		print(typ)
		import pdb;pdb.set_trace()
		raise FatalError()
		
	_type_descriptor.__cnvtype = __cnvtype
		
	TD_WCHAR.__typename    = '$T$wchar_t'
	TD_CHAR.__typename     = '$T$char'
	TD_SHORT.__typename    = '$T$short'
	TD_INT.__typename      = '$T$int'
	TD_LONG.__typename     = '$T$long'
	TD_LONGLONG.__typename = '$T$longlong'
	
	TD_UCHAR.__typename     = '$T$uchar'
	TD_USHORT.__typename    = '$T$ushort'
	TD_UINT.__typename      = '$T$uint'
	TD_ULONG.__typename     = '$T$ulong'
	TD_ULONGLONG.__typename = '$T$ulonglong'
	TD_SIZE_T.__typename    = '$T$size_t'
	
	TD_FLOAT.__typename     = '$T$float'
	TD_DOUBLE.__typename    = '$T$double'
	TD_VOID.__typename      = '$T$void'
		

	TD_WCHAR.__ctype    = pyct.c_wchar
	TD_CHAR.__ctype     = pyct.c_char
	TD_SHORT.__ctype    = pyct.c_short
	TD_INT.__ctype      = pyct.c_int32
	TD_LONG.__ctype     = pyct.c_int64
	TD_LONGLONG.__ctype = pyct.c_int64
	
	TD_UCHAR.__ctype     = pyct.c_byte
	TD_USHORT.__ctype    = pyct.c_ushort
	TD_UINT.__ctype      = pyct.c_uint32
	TD_ULONG.__ctype     = pyct.c_uint64
	TD_ULONGLONG.__ctype = pyct.c_uint64
	TD_SIZE_T.__ctype    = pyct.c_uint64
	
	TD_FLOAT.__ctype     = pyct.c_float
	TD_DOUBLE.__ctype    = pyct.c_double
	TD_VOIDP.__ctype     = pyct.c_voidp
	TD_CVOIDP.__ctype    = pyct.c_voidp
	TD_VOID.__ctype      = None
	pointer_type(TD_CHAR).__ctype = pyct.c_char_p
	pointer_type(const_type(TD_CHAR)).__ctype = pyct.c_char_p
	
	def __cnvtype(td, me):
		return td._type.__cnvtype(me)
	td_const.__cnvtype = __cnvtype
	
	def __cnvtype(td, me):
		try:
			return td.__ctype
		except AttributeError:
			pass
		ctype = type(td.id, (pyct.Structure,), {'__slots__':[], '__module__':'test'})
		td.__ctype = ctype
		if td.fields:
			fields = []
			for f,t in td.fields:
				fields += [(f,me.cnvtype(t))]
			ctype._fields_ = fields
		return ctype
	td_struct.__cnvtype = __cnvtype
	td_union.__cnvtype = __cnvtype
	
	td_enum.__ctype    = TD_INT.__ctype
	td_enum.__typename = TD_INT.__typename
	
	def __cnvtype(td, me):
		try:
			return td.__ctype
		except AttributeError:
			pass
		ctype = me.cnvtype(td._type)
		ctype = ctype*td._size
		td.__ctype = ctype
		return ctype
	td_sized_array.__cnvtype = __cnvtype
	
	
	def __cnvtype(td, me):
		try:
			return td.__ctype
		except AttributeError:
			pass
		ctype = me.cnvtype(td._type)
		ctype = ctype*1000
		td.__ctype = ctype
		return ctype
	td_unsized_array.__cnvtype = __cnvtype

	
	def __cnvtype(td, me):
		try:
			return td.__ctype
		except AttributeError:
			pass
		ctype = me.cnvtype(td._type)
		ctype = pyct.POINTER(ctype)
		td.__ctype = ctype
		return ctype
	td_pointer.__cnvtype = __cnvtype
	
	def __cnvtype(td, me):
		try:
			return td.__ctype
		except AttributeError:
			pass
		restype = me.cnvtype(td.prototype.restype)
		argtypes = [me.cnvtype(arg.restype) for arg in td.prototype.args]
		ctype = pyct.CFUNCTYPE(restype, *argtypes)
		td.__ctype = ctype
		return ctype
	td_funcptr.__cnvtype = __cnvtype

	
	
	def __cnvtype(td, me):
		try:
			return td.__ctype
		except AttributeError:
			print(td)
			raise
	td_primitive.__cnvtype = __cnvtype
	
	def __cnvtype(td, me):
		return me.cnvtype(td._type)
	td_leftvalue.__cnvtype = __cnvtype
	
	def assign(me, restype, targetast, valueast):
		return restype._type.__assign(me, targetast, valueast)
		
	def __assign(restype, me, targetast, valueast):
		return pyast.Call(
			func=pyast.Name(id='setattr',
							ctx=pyast.Load(),
							lineno=targetast.lineno,
							col_offset=targetast.col_offset),
			args=[
				targetast,
				pyast.Str(s='value',
							lineno=targetast.lineno,
							col_offset=targetast.col_offset),
				valueast,
			],
			keywords=[],
			starargs=None,
			kwargs=None,
			lineno=targetast.lineno,
			col_offset=targetast.col_offset)
	td_primitive.__assign = __assign
	
	def __assign(td, me, targetast, valueast):
		# pointer(TARGET).__setitem__(0, VALUE)
		#token = CodePositional('', targetast.lineno, targetast.col_offset, '')
		ast = pyast.Call(
			func=pyast.Name(
				id='$pointer',
				ctx=pyast.Load(),
				lineno=targetast.lineno,col_offset=targetast.col_offset
			),
			args=[targetast],
			keywords=[],
			starargs=None,
			kwargs=None,
			lineno=targetast.lineno,col_offset=targetast.col_offset)

		ast = pyast.Attribute(
			value = ast,
			attr='__setitem__',
			ctx=pyast.Load(),
			lineno=targetast.lineno,col_offset=targetast.col_offset
		)

		ast = pyast.Call(
			func=ast,
			args=[
				pyast.Num(n=0,
						lineno=targetast.lineno,col_offset=targetast.col_offset),
				valueast
			],
			keywords=[],
			starargs=None,
			kwargs=None,
			lineno=targetast.lineno,col_offset=targetast.col_offset
		)

		#for n in pyast.walk(valueast):
		#	if not hasattr(n, 'lineno'):
		#		print(n)
		return ast
		
		#targetast= pyast.Call(
		#			func=pyast.Attribute(
		#				value=me.typecall(sizedarray_type(TD_CHAR, me.sizeof(td)), token),
		#				attr='from_buffer',
		#				ctx=pyast.Load(),
		#				lineno=targetast.lineno,
		#				col_offset=targetast.col_offset),
		#			args=[targetast],
		#			keywords=[],
		#			starargs=None,
		#			kwargs=None,
		#			lineno=targetast.lineno,
		#			col_offset=targetast.col_offset)
		#			
		#return pyast.Call(
		#	func=pyast.Name(id='setattr',
		#					ctx=pyast.Load(),
		#					lineno=targetast.lineno,
		#					col_offset=targetast.col_offset),
		#	args=[
		#		targetast,
		#		pyast.Str(s='value',
		#					lineno=targetast.lineno,
		#					col_offset=targetast.col_offset),
		#		valueast,
		#	],
		#	keywords=[],
		#	starargs=None,
		#	kwargs=None,
		#	lineno=targetast.lineno,
		#	col_offset=targetast.col_offset)
	td_struct.__assign = __assign
	
	def __assign(restype, me, targetast, valueast):
		token = CodePositional('', targetast.lineno, targetast.col_offset, '')
		targetast= pyast.Call(
					func=pyast.Attribute(
						value=me.typecall(TD_SIZE_T, token),
						attr='from_buffer',
						ctx=pyast.Load(),
						lineno=targetast.lineno,
						col_offset=targetast.col_offset),
					args=[targetast],
					keywords=[],
					starargs=None,
					kwargs=None,
					lineno=targetast.lineno,
					col_offset=targetast.col_offset)
					
		return pyast.Call(
			func=pyast.Name(id='setattr',
							ctx=pyast.Load(),
							lineno=targetast.lineno,
							col_offset=targetast.col_offset),
			args=[
				targetast,
				pyast.Str(s='value',
							lineno=targetast.lineno,
							col_offset=targetast.col_offset),
				valueast,
			],
			keywords=[],
			starargs=None,
			kwargs=None,
			lineno=targetast.lineno,
			col_offset=targetast.col_offset)
	td_pointer.__assign = __assign
	
	
	def toright(me, restype, ast):
		return restype.__toright(me, ast)
		
	
	def __toright(td, me, ast):
		return pyast.Attribute(
					value=ast,
					attr='value',
					ctx=pyast.Load(),
					lineno=ast.lineno,
					col_offset=ast.col_offset
				 )
	
	td_primitive.__toright = __toright
	
	def __toright(td, me, ast):
		val = pyast.Attribute(
					value=ast,
					attr='value',
					ctx=pyast.Load(),
					lineno=ast.lineno,
					col_offset=ast.col_offset
				 )
		ast= pyast.Call(
					func=pyast.Name(
						id='ord', ctx=pyast.Load(),
						lineno=ast.lineno,
						col_offset=ast.col_offset),
					args=[val],
					keywords=[],
					starargs=None,
					kwargs=None,
					lineno=ast.lineno,
					col_offset=ast.col_offset)
		return ast
	
	td_char.__toright = __toright

	
	
	def __toright(td, me, ast):
		return me.toright(td._type, ast)
	td_const.__toright = __toright
	
	
	
	def __toright(td, me, ast):
		token = CodePositional('', ast.lineno, ast.col_offset, '')
		ast= pyast.Call(
					func=pyast.Attribute(
						value=me.typecall(TD_SIZE_T, token),
						attr='from_buffer',
						ctx=pyast.Load(),
						lineno=ast.lineno,
						col_offset=ast.col_offset),
					args=[ast],
					keywords=[],
					starargs=None,
					kwargs=None,
					lineno=ast.lineno,
					col_offset=ast.col_offset)
		return td_primitive.__toright(TD_SIZE_T, me, ast)
	
	td_pointer.__toright = __toright
	
	def __toright(td, me, ast):
		ast= pyast.Call(
					func=pyast.Name(id='$addressof',
						ctx=pyast.Load(),
						lineno=ast.lineno,col_offset=ast.col_offset
					),
					args=[ast],
					keywords=[],
					starargs=None,
					kwargs=None,
					lineno=ast.lineno,
					col_offset=ast.col_offset)
		return ast
	
	td_array_base.__toright = __toright
	
	def __toright(td, me, ast):
		token = CodePositional('', ast.lineno, ast.col_offset, '')
		ast= pyast.Call(
					func=pyast.Attribute(
						value=me.typecall(sizedarray_type(TD_CHAR, me.sizeof(td)), token),
						attr='from_buffer',
						ctx=pyast.Load(),
						lineno=ast.lineno,
						col_offset=ast.col_offset),
					args=[ast],
					keywords=[],
					starargs=None,
					kwargs=None,
					lineno=ast.lineno,
					col_offset=ast.col_offset)
					
		ast=pyast.Attribute(
			value=ast,
			attr='raw',
			ctx=pyast.Load(),
			lineno=ast.lineno,
			col_offset=ast.col_offset)
		
		ast = value=pyast.Call(
							func=pyast.Name(
								id='$c_buffer',
								ctx=pyast.Load(),
								lineno=ast.lineno,col_offset=ast.col_offset),
							args=[
								ast, 
								pyast.Num(
									n=me.sizeof(td),
									lineno=ast.lineno,col_offset=ast.col_offset),
							],
							keywords=[],
							starargs=None,
							kwargs=None,
							lineno=ast.lineno,col_offset=ast.col_offset)
							
		token = CodePositional('', ast.lineno, ast.col_offset, '')
		typeast = me.typecall(td, token)
		
		ast = pyast.Call(
				 func=pyast.Attribute(
					 value=typeast,
					 attr='from_buffer',
					 ctx=pyast.Load(),
					 lineno=ast.lineno,col_offset=ast.col_offset),
				 args=[ast],
				 keywords=[],starargs=None,kwargs=None,
				 lineno=ast.lineno,col_offset=ast.col_offset)
		return ast

	
	td_struct.__toright = __toright
	
	
	def offsetattr(me, td, attr):
		cstruct = me.cnvtype(td)
		try:
			cfield  = getattr(cstruct, attr)
		except:
			print(cstruct, attr, td.fields)
			import pdb;pdb.set_trace()
			raise FatalError()
		return cfield.offset
		
	
	def sizeattr(me, td, attr):
		cstruct = me.cnvtype(td)
		cfield  = getattr(cstruct, attr)
		return cfield.size

	

class ExecodeGeneratorLLP64:
	def __init__(me):
		me.typecnverter = TypeConverter()
		me.conststring   = ConstStringSolution(me.typecnverter)
		me.exprconverter = ExpressionConverter(me.typecnverter, me.conststring)
		me.globalvarconverter = GlobalVarConverter(me.typecnverter, me.exprconverter)
		
		me.import_vars = {}
		me.export_vars = {}
		me.import_funcs = {}
		me.export_funcs = {}
		
		
	def sizeof(me, restype):
		return me.typecnverter.sizeof(restype)
		
	
	
	
	def compile(me, node):
		return node.__compile(me)
		
	def __compile(node, me):
		print(node, node.first_token.file, node.first_token.line)
		raise FatalError()
	_node.__compile = __compile
	
	
	#def __compile(stmt, me):
	#	raise FatalError()
	#_statement.__compile = __compile
	
	def __compile(stmt, me):
		return []
	DummyStmt.__compile = __compile
	
	def __compile(module, me):
		#pymod = types.ModuleType(module.name)
		
		pymod = types.ModuleType(module.name)
		pymod.__dict__['__builtins__'] =__builtins__.copy()
		
		module.__current_vars  = {}
		module.__external_vars = {}
		
		import ctypes
		
		#print(me.typecnverter.usertypes)
		#me.typecnverter.setnames(pymod.__dict__)
		
		set_goto.goto  = '$GOTO'
		set_goto.label = '$LABEL'
		set_goto.pushblock = '$PUSH'
		set_goto.popblock  = '$POP'
		pymod.__dict__['$SETGOTO']   = set_goto
		pymod.__dict__['$POINTER']   = ctypes.POINTER
		pymod.__dict__['$CFUNCTYPE'] = ctypes.CFUNCTYPE
		pymod.__dict__['$pointer']   = ctypes.pointer
		pymod.__dict__['$c_buffer']  = ctypes.c_buffer
		pymod.__dict__['$cast']      = ctypes.cast
		pymod.__dict__['$addressof'] = ctypes.addressof
		pymod.__dict__['$classalias']= classalias
		
		for stmt in module.statements:
			codes = me.compile(stmt)
			me.typecnverter.setnames(pymod.__dict__)
			if codes:
				code = compile(pyast.Module(body=codes), stmt.first_token.file, 'exec')
				exec(code, pymod.__dict__)
				
		pymod.__dict__['$G'] = pymod
		
		#for ex,tp in me.export_vars.items():
		#	print(ex, tp)
		#for ex,tp in me.import_vars.items():
		#	print(ex, tp)
		#	
		#for ex,tp in me.export_funcs.items():
		#	print(ex, tp)
		#for ex,tp in me.import_funcs.items():
		#	print(ex, tp)
		
			
		#pymod.c_char_p = ctypes.c_char_p
		#pymod.cast     = ctypes.cast
		#pymod.c_voidp     = ctypes.c_voidp
		#pymod.c_buffer    = ctypes.c_buffer
		#pymod.pointer    = ctypes.pointer
		#pymod.addressof    = ctypes.addressof
		
		code = compile(pyast.Module(body=me.globalvarconverter.staticvarcreatecode), __file__, 'exec')
		exec(code, pymod.__dict__)
		#code = compile(pyast.Module(body=me.globalvarconverter.staticvarinitcode), __file__, 'exec')
		#exec(code, pymod.__dict__)
		code = compile(pyast.Module(body=me.conststring.statements), __file__, 'exec')
		exec(code, pymod.__dict__)
		for s in me.globalvarconverter.staticvarinitcode:
			code = compile(pyast.Module(body=[s]), s.file, 'exec')
			exec(code, pymod.__dict__)

		return pymod
	ModuleFile.__compile = __compile
	
	
	
	def dump(me, module):
		return module.__dump(me) + me.globalvarconverter.staticvarcreatecode + me.globalvarconverter.staticvarinitcode
		
	def __dump(module, me):
		module.__current_vars  = {}
		module.__external_vars = {}
		
		res = []
		for stmt in module.statements:
			res += me.compile(stmt)
		return res
	ModuleFile.__dump = __dump
	
	
	def __compile(stmt, me):
		ast = pyast.Assign(
			targets=[
				pyast.Name(
					id=stmt.id,ctx=pyast.Store(),
					lineno=stmt.first_token.line, col_offset=stmt.first_token.col),
			],
			value=me.typecnverter.typecall(stmt.restype, stmt.first_token),
			lineno=stmt.first_token.line, col_offset=stmt.first_token.col
		)
		return [ast]

	TypedefStmt.__compile = __compile
	
	def __compile(stmt, me):
		if stmt.id not in me.export_funcs:
			res  = me.typecnverter.cnvtype(stmt.prototype.restype)
			if stmt.prototype.args is not None:
				args = [me.typecnverter.cnvtype(arg.restype) for arg in stmt.prototype.args]
			else:
				args = None
			me.import_funcs[stmt.id] = (res, args)
		return []
	DeclareFunctionStmt.__compile = __compile
	
	def __compile(stmt, me):
		return []
	EnumDefine.__compile = __compile
	
	def __compile(stmt, me):
		return []
	DefineMemberStmt.__compile = __compile
	
	def __compile(stmt, me):
		ast = pyast.parse('class NAME(BASE, metaclass=classalias):pass').body[0]
		ast.name = stmt.id
		ast.bases = [me.typecnverter.typecall(stmt.restype, stmt.first_token)]
		ast.keywords[0].value.id = '$classalias'
		
		body = []
		for s in stmt.statements:
			body += me.compile(s)
		if body:
			ast.body = body
		
		return [ast]
	StructDefine.__compile = __compile
	
	def __compile(stmt, me):
		#for s in stmt.statements:
		#	me.compile(s)
		#fields = []
		#
		#ctype = me.typecnverter.cnvtype(stmt.restype)
		#if not hasattr(ctype, '_fields_'):
		#	for f,t in stmt.restype.fields:
		#		fields += [(f,me.typecnverter.cnvtype(t))]
        #
		#	ctype._fields_ = fields
		return []
	UnionDefine.__compile = __compile
	
	def __init(scope, me):
		scope.__current_vars  = {}
		scope.__external_vars = {}
		scope.__external_vars.update(scope.parent.__external_vars)
		scope.__external_vars.update(scope.parent.__current_vars)
	_scope.__init = __init
	
	def __escape(scope, me):
		body = []
		for id,stmt in scope.__current_vars.items():
			if id in scope.__external_vars:
				ast = me.globalvarconverter.rollbackname(scope.__external_vars[id], scope.last_token)
			else:
				ast = pyast.Delete(
					targets=[
						pyast.Name(
							id=id,
							ctx=pyast.Del(),
							lineno=scope.last_token.line, col_offset=scope.last_token.col
						),
					],
					lineno=scope.last_token.line, col_offset=scope.last_token.col
				)
			body += [ast]
		return body
	_scope.__escape = __escape
	
	def __compile(stmt, me):
		_scope.__init(stmt, me)
		body = []
		for s in stmt.statements:
			body += me.compile(s)
		
		return body + stmt.__escape(me)
	
	ExecBlock.__compile = __compile
	
	
	def __compile(func, me):
		if func.haserror:
			return []
			
		#import pdb;pdb.set_trace()
		
		res  = me.typecnverter.cnvtype(func.prototype.restype)
		args = [me.typecnverter.cnvtype(arg.restype) for arg in func.prototype.args]
		me.export_funcs[func.id] = (res, args)
		
		if func.id in me.import_funcs:	
			del me.import_funcs[func.id]
		
		_scope.__init(func, me)
		func.__stack_size = 0
			
		ast = pyast.parse(
			"""def NAME(arg):
				pass
			""").body[0]
			
		ast.decorator_list = [pyast.Name(
									id='$SETGOTO',ctx=pyast.Load(),
									lineno=func.first_token.line, col_offset=func.first_token.col)]
		
		ast.name = func.id
		ast.args.args = [pyast.arg(arg=arg.id, annotation=None) for arg in func.prototype.args]
		ast.body = []
		
		for n in pyast.walk(ast):
			n.lineno     = func.first_token.line
			n.col_offset = func.first_token.col
		
		
		code = []
		for stmt in func.statements:
			code += me.compile(stmt)
		
		ast.body = code
		return [ast]
	DefineFunctionStmt.__compile = __compile
	
	
		
	def __compile(stmt, me):
		if stmt.value is not None:
			ast = me.exprconverter.compile(stmt.value)
		else:
			ast = None
		ast = pyast.Expr(value=ast, lineno=stmt.first_token.line, col_offset=stmt.first_token.col)
		return [ast]
	ExprStmt.__compile = __compile
	
	def __compile(stmt, me):
		if stmt.value is not None:
			value = me.exprconverter.compile(me.exprconverter.toright(stmt.value))
		else:
			value = None
		return [pyast.Return(value=value, lineno=stmt.first_token.line, col_offset=stmt.first_token.col)]
	ReturnStmt.__compile = __compile
	
	def skipedvar(me, stmt):
			if isinstance(stmt, LocalVarStmt):
				value = me.exprconverter.uninitiallized(stmt.restype, stmt.first_token)
				ast = pyast.Assign(
					targets=[
						pyast.Name(
							id=stmt.id,ctx=pyast.Store(),
							lineno=stmt.first_token.line, col_offset=stmt.first_token.col),
						pyast.Name(
							id=me.globalvarconverter.getuniqueid(stmt),ctx=pyast.Store(),
							lineno=stmt.first_token.line, col_offset=stmt.first_token.col),
					],
					value=value,
					lineno=stmt.first_token.line, col_offset=stmt.first_token.col
				)
				return ast
			elif isinstance(stmt, LocalStaticStmt):
				ast = pyast.Assign(
					targets=[
						pyast.Name(
							id=stmt.id,ctx=pyast.Store(),
							lineno=stmt.first_token.line, col_offset=stmt.first_token.col),
					],
					value=pyast.Name(
							id=me.globalvarconverter.getuniqueid(stmt),ctx=pyast.Load(),
							lineno=stmt.first_token.line, col_offset=stmt.first_token.col),
					lineno=stmt.first_token.line, col_offset=stmt.first_token.col
				)
				return ast
			elif isinstance(stmt, LocalExtern):
				value = pyast.Name(
							id='$G',
							ctx=pyast.Load(),
							lineno = stmt.first_token.line,
							col_offset=stmt.first_token.col,
						)
				ast=pyast.Attribute(
					value=value,
					attr=stmt.id,
					ctx=pyast.Load(),
					lineno=stmt.first_token.line,
					col_offset=stmt.first_token.col)

				ast = pyast.Assign(
					targets=[
						pyast.Name(
							id=stmt.id,ctx=pyast.Store(),
							lineno=stmt.first_token.line, col_offset=stmt.first_token.col),
					],
					value=ast,
					lineno=stmt.first_token.line, col_offset=stmt.first_token.col
				)
				return ast
			else:
				raise FatalError()
		
	
	def __skipinto(scope, me, scopestack):
		if not scopestack or scope != scopestack[-1]:
			raise FatalError
			
		scopestack.pop()
		if not scopestack:
			raise FatalError
		
		res = []
		for s in scope.statements:
			if s == scopestack[-1]:
				return res + s.__skipinto(me, scopestack)
			if not isinstance(s, _declareVarStmt): continue
			
			res += [me.skipedvar(s)]
			#if isinstance(s, LocalVarStmt):
			#	value = me.exprconverter.uninitiallized(s.restype, s.first_token)
			#	ast = pyast.Assign(
			#		targets=[
			#			pyast.Name(
			#				id=s.id,ctx=pyast.Store(),
			#				lineno=s.first_token.line, col_offset=s.first_token.col),
			#			pyast.Name(
			#				id=me.globalvarconverter.getuniqueid(s),ctx=pyast.Store(),
			#				lineno=s.first_token.line, col_offset=s.first_token.col),
			#		],
			#		value=value,
			#		lineno=s.first_token.line, col_offset=s.first_token.col
			#	)
			#	res += [ast]
			#elif isinstance(s, LocalStaticStmt):
			#	ast = pyast.Assign(
			#		targets=[
			#			pyast.Name(
			#				id=s.id,ctx=pyast.Store(),
			#				lineno=s.first_token.line, col_offset=s.first_token.col),
			#		],
			#		value=pyast.Name(
			#				id=me.globalvarconverter.getuniqueid(s),ctx=pyast.Load(),
			#				lineno=s.first_token.line, col_offset=s.first_token.col),
			#		lineno=s.first_token.line, col_offset=s.first_token.col
			#	)
			#	res += [ast]
			#elif isinstance(s, LocalExtern):
			#	value = pyast.Name(
			#				id='$G',
			#				ctx=pyast.Load(),
			#				lineno = s.first_token.line,
			#				col_offset=s.first_token.col,
			#			)
			#	ast=pyast.Attribute(
			#		value=value,
			#		attr=s.id,
			#		ctx=pyast.Load(),
			#		lineno=s.first_token.line,
			#		col_offset=s.first_token.col)
            #
			#	ast = pyast.Assign(
			#		targets=[
			#			pyast.Name(
			#				id=s.id,ctx=pyast.Store(),
			#				lineno=s.first_token.line, col_offset=s.first_token.col),
			#		],
			#		value=ast,
			#		lineno=s.first_token.line, col_offset=s.first_token.col
			#	)
			#	res += [ast]
			#else:
			#	raise FatalError()

				
			#print(s, me.globalvarconverter.getuniqueid(s))
			
		#raise FatalError()
				
	_execscope.__skipinto = __skipinto
	def __skipinto(stmt, me, scopestack):
		return []
	LabelStmt.__skipinto = __skipinto
	
	def __compile(stmt, me):
		#print(stmt, stmt.label, stmt.labelstmt)
		if stmt.labelstmt is None:
			msg = 'gotoに対応するラベル"%s"がありません'%stmt.label
			raise SyntaxError(stmt.first_token, msg)
		
		labelparents = [stmt.labelstmt]
		p = stmt.labelstmt.parent
		while isinstance(p, _execscope):
			labelparents += [p]
			if isinstance(p, DefineFunctionStmt):
				break
			p = p.parent
		else:
			raise FatalError()
			
		body = []
		last = stmt
		p = stmt.parent
		escape_loop = 0
		while p not in labelparents:
			if isinstance(p, _loopBlock):
				escape_loop += 1
			if isinstance(p, DefineFunctionStmt):
				raise FatalError()
			body += p.__escape(me)
			last = p
			p = p.parent
			
		root = labelparents[labelparents.index(p)]
		labelparents = labelparents[:labelparents.index(p)]
		
		gotoindex  = root.statements.index(last)
		labelindex = root.statements.index(labelparents[-1])
		
		if gotoindex < labelindex:
			for s in root.statements[gotoindex:labelindex]:
				if not isinstance(s, _declareVarStmt): continue
				body += [me.skipedvar(s)]
		elif gotoindex > labelindex:
			for s in root.statements[labelindex:gotoindex]:
				if not isinstance(s, _declareVarStmt): continue
				ast = me.globalvarconverter.rollbackname(s, stmt.first_token)
				body += [ast]
		
		enter_loop = 0
		for sc in labelparents:
			if isinstance(sc, _loopBlock):
				enter_loop += 1
		
		body += labelparents[-1].__skipinto(me, labelparents)
		
		## gotoとラベルでループの深さが異なる場合は、pop_block、setup_loopを追加する
		if escape_loop < enter_loop:
			for _ in range(enter_loop-escape_loop):
				push = value=pyast.Name(
						id = '$PUSH', ctx=pyast.Load(),
						lineno = stmt.first_token.line,col_offset=stmt.first_token.col
					 )
				ast = pyast.Expr(value=push,lineno = stmt.first_token.line,col_offset=stmt.first_token.col)
				body += [ast]
		elif escape_loop > enter_loop:
			for _ in range(escape_loop-enter_loop):
				pop = value=pyast.Name(
						id = '$POP', ctx=pyast.Load(),
						lineno = stmt.first_token.line,col_offset=stmt.first_token.col
					 )
				ast = pyast.Expr(value=pop,lineno = stmt.first_token.line,col_offset=stmt.first_token.col)
				body += [ast]
		
		goto = pyast.Attribute(
			 value=pyast.Name(
				id = '$GOTO', ctx=pyast.Load(),
				lineno = stmt.first_token.line,col_offset=stmt.first_token.col
			 ),
			 attr=stmt.label,
			 ctx=pyast.Load(),
			 lineno = stmt.first_token.line,col_offset=stmt.first_token.col)
		ast = pyast.Expr(value=goto,lineno = stmt.first_token.line,col_offset=stmt.first_token.col)
		return body + [ast]
		
	GotoStmt.__compile = __compile
	
	def __compile(stmt, me):
		#print(stmt, stmt.label)
		label = pyast.Attribute(
			 value=pyast.Name(
				id = '$LABEL', ctx=pyast.Load(),
				lineno = stmt.first_token.line,col_offset=stmt.first_token.col
			 ),
			 attr=stmt.label,
			 ctx=pyast.Load(),
			 lineno = stmt.first_token.line,col_offset=stmt.first_token.col)
		ast = pyast.Expr(value=label,lineno = stmt.first_token.line,col_offset=stmt.first_token.col)
		return [ast]
	LabelStmt.__compile = __compile

	
	def __compile(stmt, me):
		s = stmt
		body = []
		while not isinstance(s.parent, _loopBlock):
			body += s.parent.__escape(me)
			s = s.parent
		body += s.parent.__escape(me)
		for s in body:
			for n in pyast.walk(s):
				n.lineno     = stmt.first_token.line
				n.col_offset = stmt.first_token.col
		ast = pyast.Break(lineno=stmt.first_token.line, col_offset=stmt.first_token.col)
		return body+[ast]
	BreakStmt.__compile = __compile
	
	
	def __compile(stmt, me):
		s = stmt
		body = []
		while not isinstance(s.parent, _loopBlock):
			body += s.parent.__escape(me)
			s = s.parent
		for s in body:
			for n in pyast.walk(s):
				n.lineno     = stmt.first_token.line
				n.col_offset = stmt.first_token.col
		ast = pyast.Continue(lineno=stmt.first_token.line, col_offset=stmt.first_token.col)
		return body+[ast]
	ContinueStmt.__compile = __compile
	
	def __compile(stmt, me):	
		_scope.__init(stmt, me)
		test = me.exprconverter.compile(me.exprconverter.toright(stmt.test))
		
		if type(test) == pyast.Num and test.n == 0:
			# if 0:はpythonが消してしまう。gotoとの兼ね合い上必要
			new = pyast.parse('0 and 1').body[0].value
			for n in pyast.walk(new):
				n.lineno     = test.lineno
				n.col_offset = test.col_offset
			test = new
			
		ast = pyast.parse(r"""
if 1:
	pass
else:
	pass
""").body[0]
		for n in pyast.walk(ast):
			n.lineno = stmt.first_token.line
			n.coloffset = stmt.first_token.col
		ast.test = test
		ast.body   = []
		ast.orelse = []
		
		#for s in stmt.body.statements:
		ast.body   = me.compile(stmt.body)
		ast.orelse = me.compile(stmt.orelse)
		
		
		if ast.body == []:
			ast.body = [pyast.Pass(lineno=stmt.last_token.line, col_offset=stmt.last_token.col)]
		return [ast]
	If.__compile = __compile
	
	
	def __compile(stmt, me):	
		_scope.__init(stmt, me)
		test = me.exprconverter.compile(me.exprconverter.toright(stmt.test))
		
		if type(test) == pyast.Num and test.n == 0:
			# while 0:はpythonが消してしまう。gotoとの兼ね合い上必要
			new = pyast.parse('0 and 1').body[0].value
			for n in pyast.walk(new):
				n.lineno     = test.lineno
				n.col_offset = test.col_offset
			test = new
			
		ast = pyast.parse(r"""
while 1:
	pass
""").body[0]
		for n in pyast.walk(ast):
			n.lineno = stmt.first_token.line
			n.coloffset = stmt.first_token.col
		ast.test = test
		ast.body   = []
		
		#for s in stmt.body.statements:
		ast.body   = me.compile(stmt.body)
		
		if ast.body == []:
			ast.body = [pyast.Pass(lineno=scope.last_token.line, col_offset=scope.last_token.col)]
		
		return [ast]
	While.__compile = __compile
	
	
	def __compile(stmt, me):
	
		switchid = genuniqueid(stmt)
		
		ast = pyast.parse(r"""for _ in [0]:pass""").body[0]
		
		
		test = me.exprconverter.compile(me.exprconverter.toright(stmt.test))

		cases = []
		for s in stmt.body.statements:
			if isinstance(s, CaseStmt):
				cases += [s.value]
				
		prev = goto = []
		for c in cases:
			gotocase = pyast.Attribute(
				value=pyast.Name(
						id = '$GOTO', ctx=pyast.Load()
					 ),
					 attr="$CASE$%s#%d"%(switchid, c),
					 ctx=pyast.Load())
			gotocase = pyast.Expr(value = gotocase)
			control = pyast.parse("""if VALUE==%d: pass"""%c).body[0]
			control.test.left = test
			
			control.body = [gotocase]
			prev += [control]
			prev = control.orelse
			
		gotocase = pyast.Attribute(
			value=pyast.Name(
					id = '$GOTO', ctx=pyast.Load()
				 ),
				 attr="$CASE$%s#DEFAULT"%switchid,
				 ctx=pyast.Load())
		gotocase = pyast.Expr(value = gotocase)
		prev += [gotocase]
		
		ast.body = goto
		for n in pyast.walk(ast):
			n.lineno = stmt.first_token.line
			n.col_offset = stmt.first_token.col
		
		_scope.__init(stmt, me)
		_scope.__init(stmt.body, me)
		for s in stmt.body.statements:
			if isinstance(s, CaseStmt):
				#if s.value == 99:
				#	import pdb;pdb.set_trace()
				caselabel = pyast.Attribute(
					value=pyast.Name(
							id = '$LABEL', ctx=pyast.Load()
						 ),
						 attr="$CASE$%s#%d"%(switchid, s.value),
						 ctx=pyast.Load())
				caselabel = pyast.Expr(value = caselabel)
				ast.body += [caselabel]
				for n in pyast.walk(caselabel):
					n.lineno = s.first_token.line
					n.col_offset = s.first_token.col
				
			elif isinstance(s, DefaultStmt):
				caselabel = pyast.Attribute(
					value=pyast.Name(
							id = '$LABEL', ctx=pyast.Load()
						 ),
						attr="$CASE$%s#DEFAULT"%switchid,ctx=pyast.Load())
				caselabel = pyast.Expr(value = caselabel)
				for n in pyast.walk(caselabel):
					n.lineno = s.first_token.line
					n.col_offset = s.first_token.col
				
				ast.body += [caselabel]
			else:
				ast.body += me.compile(s)
		ast.body += _scope.__escape(stmt.body, me)
		ast.body += _scope.__escape(stmt, me)
		
		return [ast]
	Switch.__compile = __compile
	
	def __compile(scope, me):	
		_scope.__init(scope, me)
		test = me.exprconverter.compile(me.exprconverter.toright(scope.test))
		
		if type(test) == pyast.Num and test.n == 0:
			# while 0:はpythonが消してしまう。gotoとの兼ね合い上必要
			new = pyast.parse('0 and 1').body[0].value
			for n in pyast.walk(new):
				n.lineno     = test.lineno
				n.col_offset = test.col_offset
			test = new
			

		
		dowhilebody = pyast.parse(
			"""
__COUNT__ = CINT()
while (__TEST__ if __COUNT__.value else (setattr(__COUNT__, 'value', 1),1)[1]):
		pass
del __COUNT__
"""					).body
		for n in pyast.walk(dowhilebody[0]):
			n.lineno     = scope.first_token.line
			n.col_offset = scope.first_token.col
		for n in pyast.walk(dowhilebody[1]):
			n.lineno     = scope.first_token.line
			n.col_offset = scope.first_token.col
		for n in pyast.walk(dowhilebody[2]):
			n.lineno     = scope.last_token.line
			n.col_offset = scope.last_token.col
		#system_count_var_id = '$FORCNT#%d'%scope.__pushstack()
		try:
			## gotoで設定された場合
			system_count_var_id = scope.__system_count_var_id
		except AttributeError:
			sc = scope
			while isinstance(sc, _execscope):
				if isinstance(sc, DefineFunctionStmt):
					break
				sc = sc.parent
			else:
				raise FatalError()
			func = sc
			try:
				forno = func.__forcnt
				func.__forcnt += 1
			except AttributeError:
				forno = 0
				func.__forcnt = 1
			system_count_var_id = scope.__system_count_var_id = '$DOWHILE#%d'%forno

		dowhilebody[0].targets[0].id = system_count_var_id
		dowhilebody[0].value.func = me.typecnverter.typecall(TD_INT, scope.first_token)
			
		
		dowhilebody[1].test.test.value.id = system_count_var_id
		dowhilebody[1].test.body          = test
		dowhilebody[1].test.orelse.value.elts[0].args[0].id = system_count_var_id
		
		dowhilebody[2].targets[0].id = system_count_var_id
		
		dowhilebody[1].body   = []
		dowhilebody[1].orelse = []
		
		#for s in stmt.body.statements:
		dowhilebody[1].body   = me.compile(scope.body)			
		
		if dowhilebody[1].body == []:
			dowhilebody[1].body = [pyast.Pass(lineno=scope.last_token.line, col_offset=scope.last_token.col)]

		
		return dowhilebody
	DoWhile.__compile = __compile
	
	def __compile(scope, me):	
		_scope.__init(scope, me)
		body = []
		for s in scope.statements:
			if s != scope.body:
				body += me.compile(s)
		
		
		forbody = pyast.parse(
			"""
__COUNT__ = CINT()
while (__INCL__ if __COUNT__.value else setattr(__COUNT__, 'value', 1), __TEST__)[1]:
		pass
del __COUNT__
"""					).body
		for n in pyast.walk(forbody[0]):
			n.lineno     = scope.first_token.line
			n.col_offset = scope.first_token.col
		for n in pyast.walk(forbody[1]):
			n.lineno     = scope.first_token.line
			n.col_offset = scope.first_token.col
		for n in pyast.walk(forbody[2]):
			n.lineno     = scope.last_token.line
			n.col_offset = scope.last_token.col
		#system_count_var_id = '$FORCNT#%d'%scope.__pushstack()
		try:
			## gotoで設定された場合
			system_count_var_id = scope.__system_count_var_id
		except AttributeError:
			sc = scope
			while isinstance(sc, _execscope):
				if isinstance(sc, DefineFunctionStmt):
					break
				sc = sc.parent
			else:
				raise FatalError()
			func = sc
			try:
				forno = func.__forcnt
				func.__forcnt += 1
			except AttributeError:
				forno = 0
				func.__forcnt = 1
			system_count_var_id = scope.__system_count_var_id = '$FORCNT#%d'%forno

		forbody[0].targets[0].id = system_count_var_id
		forbody[0].value.func = me.typecnverter.typecall(TD_INT, scope.first_token)
			
		test = me.exprconverter.compile(me.exprconverter.toright(scope.test))
		
		forbody[1].test.value.elts[0].test.value.id = system_count_var_id
		forbody[1].test.value.elts[0].body   = me.exprconverter.compile(scope.incl)
		forbody[1].test.value.elts[0].orelse.args[0].id = system_count_var_id
		forbody[1].test.value.elts[1] = test
		
		forbody[2].targets[0].id = system_count_var_id
		
		forbody[1].body   = []
		forbody[1].orelse = []
		
		#for s in stmt.body.statements:
		forbody[1].body   = me.compile(scope.body)
		
		if forbody[1].body == []:
			forbody[1].body = [pyast.Pass(lineno=scope.last_token.line, col_offset=scope.last_token.col)]
		
		body += forbody
		body += scope.__escape(me)
		return body
	For.__compile = __compile
	
	
	def __compile(stmt, me):
		if not isinstance(stmt.parent, _execscope):
			return []
	
		s = stmt.first_token.value.lstrip()
		if s.startswith('@py:'):
			s = 'class _____:' + s[len('@py:'):]
			lineno = stmt.value.count('\n', 0, stmt.value.find('@py:')) + stmt.first_token.line - 1
			
			
			try:
				ast = pyast.parse(s)
				ast.name = '$INSERT_COMMENT'
			except:
				warnings.warn(InsertPySourceError(stmt.first_token))
				return []
			
			return pyast.increment_lineno(ast, lineno).body
		else:
			return []
		
	CommentStmt.__compile = __compile
	
	
	def __compile(stmt, me):
		me.export_vars[stmt.id] = me.typecnverter.cnvtype(stmt.restype)
		if stmt.id in me.import_vars:
			del me.import_vars[stmt.id]
		return me.globalvarconverter.compile(stmt)
	GlobalVarStmt.__compile = __compile
		
	def __compile(stmt, me):
		if stmt.id not in me.export_vars:
			me.import_vars[stmt.id] = me.typecnverter.cnvtype(stmt.restype)
		return me.globalvarconverter.compile(stmt)
	GlobalExtern.__compile = __compile
	
	def __compile(stmt, me):
		me.export_vars[stmt.id] = me.typecnverter.cnvtype(stmt.restype)
		if stmt.id in me.import_vars:
			del me.import_vars[stmt.id]
		return me.globalvarconverter.compile(stmt)
	GlobalStaticStmt.__compile = __compile
	
	def __compile(stmt, me):
		if stmt.id in stmt.parent.__current_vars:
			raise FatalError()
		stmt.parent.__current_vars[stmt.id] = weakref.proxy(stmt)
		return  me.globalvarconverter.compile(stmt)
	LocalVarStmt.__compile = __compile
	LocalStaticStmt.__compile = __compile
	LocalExtern.__compile = __compile


	#def __compile(stmt, me):
	#	return me.globalvarconverter.compile(stmt)
	#GlobalVarStmt.__compile = __compile
	#GlobalExtern.__compile = __compile
	#GlobalStaticStmt.__compile = __compile
	
	
			
	#def __pushstack(stmt):
	#	return stmt.parent.__pushstack()
	#_scope.__pushstack = __pushstack
	#
	#def __popstack(stmt):
	#	return stmt.parent.__popstack()
	#_scope.__popstack = __popstack
	#
	#
	#def __pushstack(stmt):
	#	ret = stmt.__stack_size
	#	stmt.__stack_size += 1
	#	return ret
	#DefineFunctionStmt.__pushstack = __pushstack
	#
	#def __popstack(stmt):
	#	stmt.__stack_size -= 1
	#DefineFunctionStmt.__popstack = __popstack
	


	#def localvarbackup(me, stmt):
	#	stmt.__stackno = stmt.parent.__pushstack()
	#	#stmt.__uniquename = '$LOCAL$%d'%stmt.__stackno + '$' + stmt.id
	#	if stmt.id in stmt.parent.__current_vars:
	#		raise FatalError()
	#	
	#	#stmt.parent.__current[stmt.id] = stmt.__uniquename
	#	
	#	res = []
	#	if stmt.id in stmt.parent.__external_vars:
	#		stmt.parent.__current_vars[stmt.id] = '$ORVERLOADED#%d'%stmt.__stackno + '$' + stmt.id
	#		back = pyast.Assign(
	#					targets=[
	#						pyast.Name(
	#							id=stmt.parent.__current_vars[stmt.id],ctx=pyast.Store(),
	#							lineno=stmt.first_token.line, col_offset=stmt.first_token.col),
	#					],
	#					value=pyast.Name(
	#							id=stmt.id,ctx=pyast.Load(),
	#							lineno=stmt.first_token.line, col_offset=stmt.first_token.col),
	#					lineno=stmt.first_token.line, col_offset=stmt.first_token.col
	#				)
	#		res += [back]
	#	else:
	#		stmt.parent.__current_vars[stmt.id] = ''
	#	return res

	
if __name__ == '__main__':
	try:
		from .parser import *
	except SystemError:
		from noue.parser import *

	import inspect
	lno = inspect.currentframe().f_lineno+1
	src = r"""
		typedef struct test_t{
			int n;
			struct {
				int x;
			}x;
		}N;
		int test(int f){
		
			prints("%d\n", f);
			
			f = f = 0;
			
			
			N x;
			x.n = 0;
			x.n ^= 0xF;
			x.n++;
			--x.n;
			int *p;
			p = &x.n;
			*p += -1;
			x.n = *p;
			printf(++x.n, ++x.n, __LINE__);
			x.n != 1;
			int i;
			i = 0;
			printf(i, __LINE__);
			if(i == 0){
				int i;
				i = 2;
				int j;
				printf(i, __LINE__);
				for(int j=0;j<8;++j){
					printf(j);
					int i;
					i = 3;
					printf(i, __LINE__);
					while(j==0){
						int i;
						i = 4;
						printf(i, __LINE__);
						j += 1;
					}
					printf(i, __LINE__);
				}
				printf(i, __LINE__);
			}
			printf(i, __LINE__);
			x.x.x += 1, p=(void*)0;
			N x2;
			x2 = x;
			return x.n+8;
		}
		int func2()
		{
			const char s[] = "test";
			return 0;
		}
	"""
	lno = inspect.currentframe().f_lineno+1
	src = r"""
	int test(int n)
	{	
		int S2 = 99;
		int k;
		if(1){
			static int S2 = 3;
			int k;
			char s[] = "日本語";
			k = n+S2++;
			printf("test");
			printf(s);
			return k;
		}
		
		return 0;
	}
	
	"""
	
	lno = inspect.currentframe().f_lineno+1
	src = r"""
	#include <stdio.h>
	int test(int n)
	{	int i;
		if(n == 0){
			int i;
			int j;
			//@py: print('yes', j)
			goto FIN;
		}
		printf("HelloWorld%d\n", n);
		
		if(n != 0){
			int ss;
			if(n!= 0){
				int s;
				static int ss = 0;
				int n = 0;
	FIN:
				printf("Test%d\n", n);
			}
		}
		return 0;
	}
	"""
	
	lno = inspect.currentframe().f_lineno+1
	src = r"""
	#include <stdio.h>
int find(int A[5], int a, int size)
{
	for(int i=0; i<size; i++){
		if(A[i] == a){
			return i;
		}
		if(A[i] == -1)
			goto FIN;
	}
FIN:
	// @py: raise Exception()
	return size;
}

int test(int n)
{
	int A[] = {0,1,-1,3,4};
	int ret = find(A, n, 5);
	return ret;
}

	"""
	lno = inspect.currentframe().f_lineno+1
	src = r"""
	#include <stdio.h>
int test(int n){
	do{
		n--;
	}while(n>0);
	return n;
}"""

	# 日本語
	tok = Tokenizer()
	tok = Preprocessor(tok).proccess(src, __file__, lno)
	compiler = ExecodeGeneratorLLP64()
	core = SyntaxCore(compiler)
	parser = Parser(core)
	p = parser.parse_global()
	next(p)
	with warnings.catch_warnings(record = True) as rec:
	#with warnings.catch_warnings():
		warnings.filterwarnings('always')
		try:
			#warnings.filterwarnings('ignore', category=NoaffectStatement)
			for t in tok:
				if t and t[0].type == 'MC':
					#print(t)
					continue
				p.send(t)
			p.send([END(__file__)])
		except StopIteration as stop:
			module = stop.args[0]
	for w in rec:
		print(w.message.message())
		
	module = parser.module
	
	compiler = ExecodeGeneratorLLP64()
	
	ast = compiler.dump(module)
	print(ast)
	#for node in pyast.walk(ast[0]):
	#	if not hasattr(node, 'lineno'):
	#		print(node)
		#print(node)
	#ast = [ast[0].body[0]]
	#print()
	#print(ast[0].value.func.id)
	import recompiler
	p = recompiler.ReParser()
	p.toline(ast[0], 0)
	p.toline(ast[1], 0)
	
	print()
	for s in compiler.globalvarconverter.staticvarcreatecode:
		p.toline(s, 0)
	for s in compiler.globalvarconverter.staticvarinitcode:
		p.toline(s, 0)
	for s in compiler.conststring.statements:
		p.toline(s, 0)
	print()
	
	import goto
	goto.set_goto.goto  = '$GOTO'
	goto.set_goto.label = '$LABEL'
	goto.set_goto.pushblock = '$PUSH'
	goto.set_goto.popblock  = '$POP'
	globals()['$SETGOTO'] = goto.set_goto
	
	code = compile(pyast.Module(body=ast), __file__, 'exec')
	exec(code)
	print(find)
	
	from ctypes import*
	for key in compiler.typecnverter._uniquename:
		print(key, compiler.typecnverter._uniquename[key])
		name = compiler.typecnverter._uniquename[key]
		globals()[name] = key
		
		
	code = compile(pyast.Module(body=compiler.globalvarconverter.staticvarcreatecode), __file__, 'exec')
	exec(code)
	code = compile(pyast.Module(body=compiler.globalvarconverter.staticvarinitcode), __file__, 'exec')
	exec(code)
	code = compile(pyast.Module(body=compiler.conststring.statements), __file__, 'exec')
	exec(code)
	
	
	def printf(*args):
		#print(args)
		print(args[0].value.decode())
	
	def prints(s, n):
		print(s[:].decode()%n.value)
	printf = cdll.msvcrt.printf
	import sys
	globals()['$G'] = sys.modules[__name__]
	import copy
	#globals()['$CONSTSTR#0'] = compiler.globalvarconverter._conststrings[0]
	#import pdb;pdb.set_trace()
	#test = goto.set_goto(test)
	ret = test(c_int(1))
	print(ret)
	ret = test(c_int(2))
	print(ret)
	ret = test(c_int(3))
	print(ret)
	ret = test(c_int(4))
	print(ret)