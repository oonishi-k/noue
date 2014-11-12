#coding: utf8

try:
	from .error import *
	from .tokenizer import *
	from .syntaxtree import *
	from .syntaxtree import _scope, _expression, _expbinop, _function_stmt, _loopBlock, _execscope, _declareVarStmt, _externVarStmt
except SystemError:
	import imp
	noue = imp.load_source('noue', './__init__.py')
	from noue.error import *
	from noue.tokenizer import *
	from noue.syntaxtree import *
	from noue.syntaxtree import _scope, _expression, _expbinop, _function_stmt, _loopBlock, _execscope, _declareVarStmt, _externVarStmt

import weakref
#import syntaxtree
#for s in dir(syntaxtree):
#	obj = getattr(syntaxtree, s)
#	if isinstance(obj, syntaxtree._expression):
#		print(s)
#	elif isinstance(obj, type) and issubclass(obj, syntaxtree._expression):
#		print(s)
"""
TD_CHAR
TD_DOUBLE
TD_FLOAT
TD_INT
TD_LONG
TD_LONGLONG
TD_SHORT
TD_SIZE_T
TD_UCHAR
TD_UINT
TD_ULONG
TD_ULONGLONG
TD_USHORT
TD_VARARG_LIST
TD_VOID
TD_VOIDP
TD_WCHAR
_type_descriptor
td_array_base
td_const
td_dummy
td_enum
td_integer
td_leftvalue
td_pointer
td_primitive
td_real
td_sized_array
td_struct
td_union
td_unsigned
td_unsized_array
td_vararg_list_type
td_varsized_array
td_void		
"""

"""
ArgedAssign
Assign
BinCompare
ConstChar
ConstInteger
ConstReal
ConstString
ErrorExpression
NumBinOp
PtrAddSub
VarArg
VarGlobal
VarLocal
VarStaticGlobal
VarStaticLocal
Var_
_assign
_expbinop
_expression
"""

class SyntaxCore:

	primitives = {'int':TD_INT, 'char':TD_CHAR, 'long':TD_LONG, 'long long':TD_LONGLONG, 
				 'short':TD_SHORT, 'void':TD_VOID, 'double': TD_DOUBLE, 'float':TD_FLOAT,
				 '__int64': TD_LONGLONG, 'long double':TD_DOUBLE, 'size_t':TD_SIZE_T,
				 'unsigned int':TD_UINT, 'unsigned char':TD_UCHAR, 'unsigned short':TD_SHORT,
				 'unsigned long':TD_ULONG, 'unsigned long long':TD_ULONGLONG,
				 'wchar_t': TD_WCHAR}
	
	TD_CHAR.__integer_rank        = 1.0
	TD_INT.__integer_rank         = 4.0
	TD_LONG.__integer_rank        = 4.5
	TD_LONGLONG.__integer_rank    = 8.0
	TD_SHORT.__integer_rank       = 2.0
	TD_SIZE_T.__integer_rank      = 8.2
	TD_UCHAR.__integer_rank       = 1.1
	TD_UINT.__integer_rank        = 4.2
	TD_ULONG.__integer_rank       = 4.6
	TD_ULONGLONG.__integer_rank   = 8.1
	TD_USHORT.__integer_rank      = 2.2
	TD_WCHAR .__integer_rank      = 2.1
	
	def __init__(me, size_caculator):
		me.size_caculator = size_caculator
	
	#def seterror(me, scope, err):
	#	scope.__adderror(err)
	#
	#def __adderror(scope, err):
	#	scope.haserror = True
	#	scope.parent.__adderror(err)
	#_scope.__adderror = __adderror
	#
	#def __adderror(scope, err):
	#	scope.haserror = True
	#	scope.errors += [err]
	#	scope.parent.__adderror(None)
	#DefineFunctionStmt.__adderror = __adderror
	#
	#def __adderror(scope, err):
	#	scope.haserror = True
	#	if err: scope.errors += [err]
	#ModuleFile.__adderror = __adderror
	
	def intrank(me, typ):
		return typ.__integer_rank
		
		
	def eval_constinteger(me, exp):
		return exp.__eval_constinteger(me)
	
	def __eval_constinteger(exp, me):
		import pdb;pdb.set_trace()
		raise NotConstInteger(exp)
	_expression.__eval_constinteger = __eval_constinteger
	
	def __eval_constinteger(exp, me):
		if exp.op == '+':
			return me.eval_constinteger(exp.left) + me.eval_constinteger(exp.right)
		if exp.op == '-':
			return me.eval_constinteger(exp.left) - me.eval_constinteger(exp.right)
		if exp.op == '*':
			return me.eval_constinteger(exp.left) * me.eval_constinteger(exp.right)
		if exp.op == '/':
			return me.eval_constinteger(exp.left) // me.eval_constinteger(exp.right)
		if exp.op == '%':
			return me.eval_constinteger(exp.left) % me.eval_constinteger(exp.right)
		if exp.op == '&':
			return me.eval_constinteger(exp.left) & me.eval_constinteger(exp.right)
		if exp.op == '|':
			return me.eval_constinteger(exp.left) | me.eval_constinteger(exp.right)
		if exp.op == '^':
			return me.eval_constinteger(exp.left) ^ me.eval_constinteger(exp.right)
		if exp.op == '<<':
			return me.eval_constinteger(exp.left) << me.eval_constinteger(exp.right)
		if exp.op == '>>':
			return me.eval_constinteger(exp.left) >> me.eval_constinteger(exp.right)
		if exp.op == '<':
			return int(me.eval_constinteger(exp.left) < me.eval_constinteger(exp.right))
		if exp.op == '>':
			return int(me.eval_constinteger(exp.left) > me.eval_constinteger(exp.right))
		if exp.op == '<=':
			return int(me.eval_constinteger(exp.left) <= me.eval_constinteger(exp.right))
		if exp.op == '>=':
			return int(me.eval_constinteger(exp.left) >= me.eval_constinteger(exp.right))
		if exp.op == '!=':
			return int(me.eval_constinteger(exp.left) != me.eval_constinteger(exp.right))
		if exp.op == '==':
			return int(me.eval_constinteger(exp.left) == me.eval_constinteger(exp.right))
		else:
			raise FatalError()
	_expbinop.__eval_constinteger = __eval_constinteger
	
	
	def __eval_constinteger(exp, me):
		return exp.value
	ConstInteger.__eval_constinteger = __eval_constinteger
	
	def __eval_constinteger(exp, me):
		if exp.op == '+':
			return me.eval_constinteger(exp.value)
		if exp.op == '-':
			return - me.eval_constinteger(exp.value)
		if exp.op == '!':
			return int(not me.eval_constinteger(exp.value))
		if exp.op == '~':
			return ~ me.eval_constinteger(exp.value)
		else:
			raise FatalError()
		
	UnaryOp.__eval_constinteger = __eval_constinteger
	
	
	def __eval_constinteger(exp, me):
		test = me.eval_constinteger(exp.test)
		if test:
			return me.eval_constinteger(exp.true)
		else:
			return me.eval_constinteger(exp.false)
		
	Three.__eval_constinteger = __eval_constinteger
	

		
	def exectype(me, typ):
		typ = strip_options(typ)
		if is_usertype(typ) and typ.fields is None:
			return type('', (ctypes.Structure,), {})
		return ctypes.c_voidp
		
	def sizeofexp(me, typ, token):
		if is_usertype(typ) and strip_options(typ).fields == []:
			warnings.warn(InvalidSizeof(token, typ))
			return me.errorexp(token)
		size = me.size_caculator.sizeof(typ)
		if size != 0:
			return ConstInteger(TD_SIZE_T, size, token)
		warnings.warn(InvalidSizeof(token, typ))
		return me.errorexp(token)

		
	def calc_restype_num(me, op, ltype, rtype):
		ltype = strip_options(ltype)
		rtype = strip_options(rtype)
		if not is_numeric(ltype) or  not is_numeric(rtype):
			raise FatalErro()
			
		if ltype == rtype:
			return ltype
		if ltype == TD_DOUBLE or rtype == TD_DOUBLE:
			return TD_DOUBLE
		if ltype == TD_FLOAT or rtype == TD_FLOAT:
			return TD_FLOAT
		if me.intrank(ltype) < me.intrank(TD_INT) and me.intrank(rtype) < me.intrank(TD_INT):
			return TD_INT
		if me.intrank(ltype) != me.intrank(rtype):
			return ltype if me.intrank(ltype) > me.intrank(rtype) else rtype
		if is_unsigned(ltype):
			return ltype
		if is_unsigned(rtype):
			return rtype
			
		raise FatalErro()
		
	def _addsub(me, op, left, right):
		ltype = left.restype
		rtype = right.restype
		if is_numeric(ltype) and is_numeric(rtype):
			restype = me.calc_restype_num(op, ltype, rtype)
			return BinOp(restype, op, left, right)
		if op in '+-' and is_pointer(ltype) and is_integer(rtype) and strip_options(ltype) != TD_VOIDP:
			restype = strip_options(ltype)
			return PtrAdd(op, left, right)
		if op == '-' and is_pointer(ltype) and is_pointer(rtype):
			if strip_options(ltype) != TD_VOIDP and strip_options(target_type(ltype)) == strip_options(target_type(rtype)):
				restype = strip_options(ltype)
				return PtrSub(TD_LONGLONG, left, right)
		warnings.warn(BinOpTypeError(op, left, right))
		return me.errorexp(left.first_token)
		
	def add(me, scope, left, right):
		if is_errorexp(left):  return left
		if is_errorexp(right): return right
		
		return me._addsub('+', left, right)
		
	def sub(me, scope, left, right):
		if is_errorexp(left):  return left
		if is_errorexp(right): return right
		
		return me._addsub('-', left, right)
		
		
	def _divmul(me, op, left, right):
		ltype = left.restype
		rtype = right.restype
		if is_numeric(ltype) and is_numeric(rtype):
			restype = me.calc_restype_num(op, ltype, rtype)
			return BinOp(restype, op, left, right)
		warnings.warn(BinOpTypeError(op, left, right))
		return me.errorexp()
		
		
	def div(me, scope, left, right):
		if is_errorexp(left):  return left
		if is_errorexp(right): return right
	
		return me._divmul('/', left, right)
		
	def mul(me, scope, left, right):
		if is_errorexp(left):  return left
		if is_errorexp(right): return right
		
		return me._divmul('*', left, right)
		
	def mod(me, scope, left, right):
		if is_errorexp(left):  return left
		if is_errorexp(right): return right
		
		return me._divmul('%', left, right)
			
	def _bit_binop(me, op, left, right):
		if is_integer(left.restype) and is_integer(right.restype):
			restype = strip_options(left.restype)
			return BinOp(restype, op, left, right)
		warnings.warn(BinOpTypeError(op, left, right))
		return me.errorexp()
		
	def bitand(me, scope, left, right):
		if is_errorexp(left):  return left
		if is_errorexp(right): return right
		
		return me._bit_binop('&', left, right)
		
	def bitor(me, scope, left, right):
		if is_errorexp(left):  return left
		if is_errorexp(right): return right
		
		return me._bit_binop('|', left, right)
		
	def lshift(me, scope, left, right):
		if is_errorexp(left):  return left
		if is_errorexp(right): return right
		
		return me._bit_binop('>>', left, right)
		
	def rshift(me, scope, left, right):
		if is_errorexp(left):  return left
		if is_errorexp(right): return right
		
		return me._bit_binop('<<', left, right)
		
	def bitxor(me, scope, left, right):
		if is_errorexp(left):  return left
		if is_errorexp(right): return right
		
		return me._bit_binop('^', left, right)
		
	def _compare(me, op, left, right):
		if is_numeric(left.restype) and is_numeric(right.restype):
			return BinCompare(op, left, right)
		if is_pointer(left.restype) and is_pointer(right.restype):
			return BinCompare(op, left, right)
		if is_pointer(left.restype) and isinstance(right, ConstInteger) and right.value == 0:
			return BinCompare(op, left, right)
		if isinstance(left, ConstInteger) and left.value == 0 and is_pointer(right.restype):
			return BinCompare(op, left, right)
		warnings.warn(BinOpTypeError(op, left, right))
		return me.errorexp(left.first_token)
		
	def equal(me, scope, left, right):
		if is_errorexp(left):  return left
		if is_errorexp(right): return right
		
		return me._compare('==', left, right)
		
	def notequal(me, scope, left, right):
		if is_errorexp(left):  return left
		if is_errorexp(right): return right
		
		return me._compare('!=', left, right)
		
	def lessthan(me, scope, left, right):
		if is_errorexp(left):  return left
		if is_errorexp(right): return right
		
		return me._compare('<', left, right)
		
	def lessequal(me, scope, left, right):
		if is_errorexp(left):  return left
		if is_errorexp(right): return right
		
		return me._compare('<=', left, right)
		
	def greaterthan(me, scope, left, right):
		if is_errorexp(left):  return left
		if is_errorexp(right): return right
		
		return me._compare('>', left, right)
		
	def greaterequal(me, scope, left, right):
		if is_errorexp(left):  return left
		if is_errorexp(right): return right
		
		return me._compare('>=', left, right)
		
		
	def _logical(me, op, left, right):
		if not is_bool(left.restype) or not is_bool(right.restype):
			warnings.warn(BinOpTypeError(op, left, right))
			return me.errorexp(left.first_token)
		return BinLogical(op, left, right)
		
	def logicalor(me, scope, left, right):
		if is_errorexp(left):  return left
		if is_errorexp(right): return right
		
		return me._logical('||', left, right)
		
	def logicaland(me, scope, left, right):
		if is_errorexp(left):  return left
		if is_errorexp(right): return right
		
		return me._logical('&&', left, right)
		
		
	def unaryplus(me, scope, token, value):
		if is_errorexp(value):  return value
		
		if not is_numeric(value.restype):
			msg = '+"%s"は不正です'%value.restype.name
			warnings.warn(TypeError(token, msg))
			return me.errorexp(token)
		
		if token.value != '+':
			raise FatalError()
			
		return UnaryOp(right_type(value.restype), token, value)
		
	def unaryminus(me, scope, token, value):
		if is_errorexp(value):  return value
		
		if not is_numeric(value.restype):
			msg = '-"%s"は不正です'%value.restype.name
			warnings.warn(TypeError(token, msg))
			return me.errorexp(token)
			
		if token.value != '-':
			raise FatalError()
		
		return UnaryOp(right_type(value.restype), token, value)
		
	def bitnot(me, scope, token, value):
		if is_errorexp(value):  return value
		
		if not is_integer(value.restype):
			msg = '~"%s"は不正です'%value.restype.name
			warnings.warn(TypeError(token, msg))
			return me.errorexp(token)
			
		if token.value != '-':
			raise FatalError()
		
		return UnaryOp(right_type(value.restype), token, value)
		
		
	def logicalnot(me, scope, token, value):
		if is_errorexp(value):  return value
		
		if not is_bool(value.restype):
			msg = '!"%s"は不正です'%value.restype.name
			warnings.warn(TypeError(token, msg))
			return me.errorexp(token)
			
		if token.value != '!':
			raise FatalError()
		
		return UnaryOp(TD_INT, token, value)
		
	def preincl(me, scope, token, value):
		if is_errorexp(value):  return value
		
		if not is_numeric(value.restype) and not is_pointer(value.restype):
			msg = '++"%s"は不正です'%value.restype.name
			warnings.warn(TypeError(token, msg))
			return me.errorexp(token)
			
		if not is_lefttype(value.restype):
			msg = '左辺値が必要です'
			warnings.warn(TypeError(token, msg))
			return me.errorexp(token)
			
		if token.value != '++':
			raise FatalError()
		
		return PreIncl(token, value)
		
	def predecl(me, scope, token, value):
		if is_errorexp(value):  return value
		
		if not is_numeric(value.restype) and not is_pointer(value.restype):
			msg = '--"%s"は不正です'%value.restype.name
			warnings.warn(TypeError(token, msg))
			return me.errorexp(token)
			
		if not is_lefttype(value.restype):
			msg = '左辺値が必要です'
			warnings.warn(TypeError(token, msg))
			return me.errorexp(token)
			
		if token.value != '--':
			raise FatalError()
		
		return PreIncl(token, value)
		
	def postincl(me, scope, value, token):
		if is_errorexp(value):  return value
		
		if not is_numeric(value.restype) and not is_pointer(value.restype):
			msg = '++"%s"は不正です'%value.restype.name
			warnings.warn(TypeError(token, msg))
			return me.errorexp(token)
			
		if not is_lefttype(value.restype):
			msg = '左辺値が必要です'
			warnings.warn(TypeError(token, msg))
			return me.errorexp(token)
			
		if token.value != '++':
			raise FatalError()
		
		return PostIncl(value, token)

		
	def postdecl(me, scope, value, token):
		if is_errorexp(value):  return value
		
		if not is_numeric(value.restype) and not is_pointer(value.restype):
			msg = '--"%s"は不正です'%value.restype.name
			warnings.warn(TypeError(token, msg))
			return me.errorexp(token)
			
		if not is_lefttype(value.restype):
			msg = '左辺値が必要です'
			warnings.warn(TypeError(token, msg))
			return me.errorexp(token)
			
		if token.value != '--':
			raise FatalError()
		
		return PostIncl(value, token)

		
		
	# 暗黙のcastが必要ならTrue
	def _assign_type_check(me, targettype, valueexp, first_token):
		ltype = strip_options(targettype)
		rtype = strip_options(valueexp.restype)

		if is_numeric(ltype) and is_numeric(rtype):
			wan = UnsafeImplicitConversion(first_token, ltype, rtype)
			if ltype == TD_DOUBLE:
				pass
			elif ltype == TD_FLOAT and rtype == TD_DOUBLE:
				if isinstance(valueexp, ConstInteger) and valueexp.value == 0:
					pass
				else:
					warnings.warn(wan)
				return True
			elif me.size_caculator.sizeof(ltype) < me.size_caculator.sizeof(rtype):
				if rtype != TD_INT:
					if isinstance(valueexp, ConstInteger) and valueexp.value == 0:
						pass
					else:
						warnings.warn(wan)
					return True
			elif is_unsigned(ltype) and not is_unsigned(rtype):
				if isinstance(valueexp, ConstInteger) and valueexp.value == 0:
					pass
				else:
					warnings.warn(wan)
				return True
			elif not is_unsigned(ltype) and is_unsigned(rtype) and me.size_caculator.sizeof(ltype) == me.size_caculator.sizeof(rtype):
				if isinstance(valueexp, ConstInteger) and valueexp.value == 0:
					pass
				else:
					warnings.warn(wan)
				return True
		elif is_pointer(ltype) and is_pointer(rtype):
			if ltype == TD_VOIDP or rtype == TD_VOIDP:
				pass
			elif ltype == TD_CVOIDP:
				pass
			elif target_type(ltype) == target_type(rtype):
				pass
			elif strip_options(target_type(ltype)) == target_type(rtype):
				pass
			else:
				err = CastError(first_token, ltype, rtype)
				raise err
		elif is_usertype(ltype) and is_usertype(rtype):
			if ltype != rtype:
				err = CastError(first_token, ltype, rtype)
				raise err
		elif is_funcptr(ltype) and is_funcptr(rtype):
			pass
		elif is_pointer(ltype) and isinstance(valueexp, ConstInteger) and valueexp.value == 0:
			pass
		else:
			err = CastError(first_token, ltype, rtype)
			raise err
		
		return False
		
	def assign(me, scope, left, right):
		if is_errorexp(left):  return left
		if is_errorexp(right): return right
		
		if not is_lefttype(left.restype):
			msg = '"="の左側が左辺値になっていません。'
			warnings.warn(TypeError(left.first_token, msg))
			return me.errorexp(left.first_token)
			
		if is_const(left.restype):
			msg = '"="の左側がconstです。'
			warnings.warn(TypeError(left.first_token, msg))
			return me.errorexp(left.first_token)
		try:
			require_cast = me._assign_type_check(left.restype, right, left.first_token)
			if require_cast:
				 right = me.implicit_cast(scope, left.restype, right)
		except NoueError as err:
			warnings.warn(err)
			return me.errorexp(left.first_token)
			
		return Assign(left, right)
		
	def comma(me, scope, vars):
		if not vars: raise FatalError()
		for v in vars:
			if is_errorexp(v):  return v
		
		return Comma(vars)
		
	def _arged_assign(me, op, left, right):
		if op in ('+=', '-='):
			# errorチェック
			res = me._addsub(op, left, right)
		elif op in ('*=', '/=', '%='):
			res = me._divmul(op, left, right)
		elif op in ('<<=', '>>=', '&=', '|=', '^='):
			res = me._bit_binop(op, left, right)
		else:
			raise FatalError()
		if not isinstance(res, ErrorExpression):
			return ArgedAssign(op, left, right)
		return res
		
	def assign_add(me, scope, left, right):
		if is_errorexp(left):  return left
		if is_errorexp(right): return right
		
		return me._arged_assign('+=', left, right)
	def assign_sub(me, scope, left, right):
		if is_errorexp(left):  return left
		if is_errorexp(right): return right
		
		return me._arged_assign('-=', left, right)
	def assign_mul(me, scope, left, right):
		if is_errorexp(left):  return left
		if is_errorexp(right): return right
		
		return me._arged_assign('*=', left, right)
	def assign_div(me, scope, left, right):
		if is_errorexp(left):  return left
		if is_errorexp(right): return right
		
		return me._arged_assign('/=', left, right)
	def assign_mod(me, scope, left, right):
		if is_errorexp(left):  return left
		if is_errorexp(right): return right
		
		return me._arged_assign('%=', left, right)
	def assign_bitand(me, scope, left, right):
		if is_errorexp(left):  return left
		if is_errorexp(right): return right
		
		return me._arged_assign('&=', left, right)
	def assign_bitor(me, scope, left, right):
		if is_errorexp(left):  return left
		if is_errorexp(right): return right
		
		return me._arged_assign('|=', left, right)
	def assign_bitxor(me, scope, left, right):
		if is_errorexp(left):  return left
		if is_errorexp(right): return right
		
		return me._arged_assign('^=', left, right)
	def assign_lshift(me, scope, left, right):
		if is_errorexp(left):  return left
		if is_errorexp(right): return right
		
		return me._arged_assign('<<=', left, right)
	def assign_rshift(me, scope, left, right):
		if is_errorexp(left):  return left
		if is_errorexp(right): return right
		
		return me._arged_assign('>>=', left, right)
		
	def dot(me, scope, owner, attr):
		if is_errorexp(owner):  return owner
		
		if not is_usertype(owner.restype):
			msg = '"."の左側が構造体または共用体ではありません。(%s)'%(owner.restype.name)
			warnings.warn(TypeError(owner.first_token, msg))
			return me.errorexp(owner.first_token)
			
		if strip_options(owner.restype).fields is None:
			msg = '構造体は未定義です。(%s)'%(owner.restype.name)
			warnings.warn(TypeError(owner.first_token, msg))
			return me.errorexp(owner.first_token)
			
		if not me.has_member(scope, owner.restype, attr.value):
			msg = '"%s"は%sのメンバーではありません。'%(attr.value, owner.restype.name)
			warnings.warn(TypeError(owner.first_token, msg))
			return me.errorexp(owner.first_token)
		
		restype = me.get_attrtype(scope, strip_options(owner.restype), attr.value)
		if is_const(owner.restype):
			restype = const_type
		return Dot(restype, owner, attr)
		
	def arrow(me, scope, owner, attr):
		if is_errorexp(owner):  return owner
		
		if not is_pointer(owner.restype):
			msg = '"->"の左側がポインタではありません。(%s)'%(owner.restype.name)
			warnings.warn(TypeError(owner.first_token, msg))
			return me.errorexp(owner.first_token)
		if not is_usertype(target_type(owner.restype)):
			msg = '"->"の左側が構造体または共用体ではありません。(%s)'%(target_type(owner.restype).name)
			warnings.warn(TypeError(owner.first_token, msg))
			return me.errorexp(owner.first_token)
		if not me.has_member(scope, target_type(owner.restype), attr.value):
			msg = '"%s"は%sのメンバーではありません。'%(attr.value, target_type(owner.restype).name)
			warnings.warn(TypeError(owner.first_token, msg))
			return me.errorexp(owner.first_token)
		
		restype = me.get_attrtype(scope, target_type(owner.restype), attr.value)
		if is_const(target_type(owner.restype)):
			restype = const_type
		return Arrow(restype, owner, attr)
		
	def _set_args(me, scope, sig, args, token):
		#print(sig.restype, sig.args, sig.has_vararg)
		callig_args = []
		if is_errorfunc(sig):
			return me.errorexp(token)
		if sig.args is not None:
			if len(sig.args) > len(args):
				msg = '"引数の個数が一致しません'
				#warnings.warn(TypeError(id, msg))
				#return me.errorexp(id)
				raise TypeError(token, msg)
			elif not sig.has_vararg and len(sig.args) != len(args):
				msg = '引数の個数が一致しません'
				raise TypeError(token, msg)
				
			args = iter(args)
			for argdef, argval in zip(sig.args, args):
				require_cast = me._assign_type_check(argdef.restype, argval, argval.first_token)
				if require_cast:
					argval = me.implicit_cast(scope, argdef.restype, argval)
				callig_args += [argval]
				
			for argval in args:
				callig_args += [argval]
		else:
			for argval in args:
				callig_args += [argval]
		return callig_args
			
	def call_id(me, scope, id, args, last_token):
		if id.type != 'ID':
			raise FatalError()

		func = me.getfunc(scope, id)
		
		#if is_func(func):
		if isinstance(func, ConstFunctionAddress):
			sig = func.restype.prototype
		else:
			return me.call_funcptr(scope, funcptr, argrs, last_token)
			
		try:
			callig_args = me._set_args(scope, sig, args, id)
		except NoueError as err:
			warnings.warn(err)
			return me.errorexp(id)
		
		return CallFunc(func, args, last_token)
	
	def call_funcptr(me, scope, funcptr, args, last_token):
		#if not is_funcptr(funcptr.restype):
		#	msg = '関数ポインタでない変数に対して関数呼び出しが行われました(%s)'%(id.value)
		#	warnings.warn(TypeError(id, msg))
		#	return me.errorexp(id)
		#sig = get_signature(funcptr)
		#sig = strip_options(funcptr.restype).prototype
		restype = strip_options(funcptr.restype)
		while is_pointer(restype):
			#restype = target_type(restype)
			funptr = ImplicitDerefFuncptr(funptr)
			restype = strip_options(funcptr.restype)
		if not is_funcptr(restype):
			msg = '関数ポインタでない変数に対して関数呼び出しが行われました(%s)'%(funcptr.restype.name)
			warnings.warn(TypeError(funcptr.first_token, msg))
			return me.errorexp(funcptr.first_token)
		sig = restype.prototype
		try:
			callig_args = me._set_args(scope, sig, args, funcptr.first_token)
		except NoueError as err:
			warnings.warn(err)
			return me.errorexp(id)

		return CallFuncptr(funcptr, args, last_token)
			
	def addressof(me, scope, op_token, value):
		if is_errorexp(value):  return value
		
		if not is_lefttype(value.restype):
			msg = '右辺値のアドレスは取得できません'
			warnings.warn(TypeError(op_token, msg))
			return me.errorexp(op_token)
			
		return Addressof(op_token, value)
		
	def dereference(me, scope, op_token, value):
		if is_errorexp(value):  return value
		
		if not is_pointer(value.restype) and not is_funcptr(value.restype):
			print(value, value.restype)
			msg = '*の右側にポインタが必要です'
			warnings.warn(TypeError(op_token, msg))
			return me.errorexp(op_token)
			
		return Dereference(op_token, value)

	def index(me, scope, owner, index, last_token):
		if is_errorexp(owner):  return owner
		if is_errorexp(index):  return index
		
		if not is_pointer(owner.restype):
			msg = '[]の左側にポインタが必要です'
			warnings.warn(TypeError(owner.first_token, msg))
			return me.errorexp(op_token)
			
		if not is_integer(index.restype):
			#import pdb;pdb.set_trace()
			msg = '[]の中に整数型が必要です'
			warnings.warn(TypeError(index.first_token, msg))
			return me.errorexp(owner.first_token)
			
		return Index(owner, index, last_token)
		
	def cast(me, scope, restype, value, first_token):
		if is_numeric(value.restype) and is_numeric(restype):
			return Cast(restype, value, first_token)
		if is_pointer(value.restype) and is_pointer(restype):
			return Cast(restype, value, first_token)
		if is_integer(value.restype) and is_pointer(restype):
			if me.size_caculator.sizeof(value.restype) != me.size_caculator.sizeof(restype):
				warnings.warn(Integer2PointerConversion(first_token, value.restype))
			return Cast(restype, value, first_token)
		if is_pointer(value.restype) and is_integer(restype):
			if me.size_caculator.sizeof(value.restype) != me.size_caculator.sizeof(restype):
				wan = UnsafeImplicitConversion(first_token, restype, value.restype)
				warnings.warn(wan)
			return Cast(restype, value, first_token)
		if is_funcptr(value.restype) and is_funcptr(restype):
			return Cast(restype, value, first_token)
		if is_integer(value.restype) and is_funcptr(restype):
			if me.size_caculator.sizeof(value.restype) != me.size_caculator.sizeof(restype):
				warnings.warn(Integer2PointerConversion(first_token, value.restype))
			return Cast(restype, value, first_token)
		if is_funcptr(value.restype) and is_integer(restype):
			if me.size_caculator.sizeof(value.restype) != me.size_caculator.sizeof(restype):
				wan = UnsafeImplicitConversion(first_token, restype, value.restype)
				warnings.warn(wan)
			return Cast(restype, value, first_token)
			
		warnings.warn(CastError(first_token, restype, value.restype))
		return me.errorexp(first_token)
		
	def implicit_cast(me, scope, restype, value):
		if is_numeric(value.restype) and is_numeric(restype):
			return ImplicitCast(restype, value)
		#if is_pointer(value.restype) and is_pointer(restype):
		#	return ImplicitCast(restype, value, first_token)
			
		warnings.warn(CastError(value.first_token, restype, value.restype))
		return me.errorexp(value.first_token)

	
	def three(me, scope, test, true, false):
		if is_errorexp(test):  return test
		if is_errorexp(true):  return true
		if is_errorexp(false):  return false
		
		if not is_bool(test.restype):
			warnings.warn(CastError(first_token, TD_BOOL, test.restype))
			return me.errexp(first_token)
		if is_numeric(true.restype) and is_numeric(false.restype):
			restype = me.calc_restype_num('?', true.restype, false.restype)
		elif is_pointer(true.restype) and is_pointer(false.restype):
			typ1 = target_type(true.restype)
			typ2 = target_type(false.restype)
			if strip_options(typ1) == strip_options(typ2):
				restype = pointer_type(const_type(typ1)) if is_const(typ1) or is_const(typ2) else pointer_type(typ1)
			else:
				restype = TD_CVOIDP if is_const(typ1) or is_const(typ2) else TD_VOIDP
		return Three(restype, test, true, false)
			
	def const_integer(me, scope, token):
		if token.type != 'CI':
			raise FatalError()
			
		if token.suffix == 'L':
			return ConstInteger(TD_LONG, token.value, token)
		elif token.suffix == 'LL':
			return ConstInteger(TD_LONGLONG, token.value, token)
		elif token.suffix == 'UL':
			return ConstInteger(TD_ULONG, token.value, token)
		elif token.suffix == 'ULL':
			return ConstInteger(TD_ULONGLONG, token.value, token)
		elif token.suffix == 'U':
			return ConstInteger(TD_UINT, token.value, token)
		elif token.suffix == '':
			return ConstInteger(TD_INT, token.value, token)
		else:
			msg = '整数値のサフィックス"%s"は不正です'%token.suffix
			warnings.warn(SyntaxError(token, msg))
			return me.errorexp(token)
			
	def const_real(me, scope, token):
		if token.type != 'CR':
			raise FatalError()
			
		if token.suffix in ('F', 'f'):
			return ConstReal(TD_FLOAT, token.value, token)
		elif token.suffix in ('D', 'd'):
			return ConstReal(TD_DOUBLE, token.value, token)
		elif token.suffix == '':
			return ConstReal(TD_DOUBLE, token.value, token)
		else:
			msg = '実数値のサフィックス"%s"は不正です'%token.suffix
			warnings.warn(SyntaxError(token, msg))
			return me.errorexp(token)
			
	def const_string(me, scope, token):
		if token.type != 'CS':
			raise FatalError()
		
		if token.prefix == 'L':
			return ConstString(sizedarray_type(TD_WCHAR, len(token.value)+1), token.value, token)
		elif token.prefix == '':
			s = token.value.encode() if not token.encoding else token.value.encode(token.encoding)
			return ConstString(sizedarray_type(TD_CHAR, len(s)+1), s, token)
		else:
			msg = '文字列のプレフィックス"%s"は不正です'%token.prefix
			warnings.warn(SyntaxError(token, msg))
			return me.errorexp(token)
		
	def const_char(me, scope, token):
		if token.type != 'CC':
			raise FatalError()
			
		if token.prefix == 'L':
			return ConstChar(TD_WCHAR, token.value, token)
		elif token.prefix == '':
			return ConstChar(TD_CHAR, token.value, token)
		else:
			msg = '文字列のプレフィックス"%s"は不正です'%token.prefix
			warnings.warn(SyntaxError(token, msg))
			return me.errorexp(token)

			
	def errorexp(me, token):
		return ErrorExpression(token)
		
		
	def errortype(me):
		return TD_ERROR
		
		
	def getfunc(me, scope, id):
		if id.value in me.primitives:
			raise NotFunction(id)
		res = scope.__getfunc(me, id)
		return res
	
	def __getfunc(scope, me, id):
		if id.value in scope.__ids:
			stmt = scope.__ids[id.value]
			if isinstance(stmt, _function_stmt):
				#return funcid(stmt.prototype, id)
				#return FunctionAddress(funcid(stmt.prototype, id), id)
				
				return ConstFunctionAddress(stmt.prototype, id)
			raise NotFunction(id)
		elif scope.parent is not None:
			return me.getfunc(scope.parent, id)
			
		warnings.warn(CallingUnknownFunction(id))
		
		proto = prototype(TD_INT)
		#return funcid(proto, id)
		#return FunctionAddress(funcid(stmt.prototype, id), id)
		return ConstFunctionAddress(proto, id)

	_scope.__getfunc = __getfunc
	
	def getid(me, scope, id):
		if id.value in me.primitives:
			return me.primitives[id.value]
		return scope.__getid(me, id)

		
	def __getid(scope, me, id):
		#if id.value == 'Py_ssize_t':
		#	import pdb;pdb.set_trace()
		if id.value in scope.__ids:
			stmt = scope.__ids[id.value]
			if isinstance(stmt, _declareVarStmt):
				if isinstance(stmt, LocalExtern):
					res = VarGlobal(stmt.restype, id)
				elif isinstance(stmt, LocalStaticStmt):
					res = VarStaticLocal(stmt.restype, id)
				elif isinstance(stmt, LocalVarStmt):
					res = VarLocal(stmt.restype, id)
				else:
					raise FatalError()
				res.declareat = weakref.proxy(stmt)
				return res
			elif isinstance(stmt, argdecl_descriptor):
				res = VarArg(stmt.restype, id)
				res.declareat = weakref.proxy(stmt)
				return res
			elif isinstance(stmt, _function_stmt):
				#return funcid(stmt.prototype, id)
				return FunctionAddress(stmt.prototype, id)
			elif isinstance(stmt, TypedefStmt):
				return stmt.restype
			else:
				raise
		return me.getid(scope.parent, id)
			
	_scope.__getid = __getid
	
	def __getid(scope, me, id):
		#if id.value == 'Py_ssize_t':
		#	import pdb;pdb.set_trace()
		if id.value in scope.__ids:
			stmt = scope.__ids[id.value]
			if isinstance(stmt, _declareVarStmt):
				if isinstance(stmt, GlobalExtern):
					res = VarGlobal(stmt.restype, id)
				elif isinstance(stmt, GlobalStaticStmt):
					res = VarStaticLocal(stmt.restype, id)
				elif isinstance(stmt, GlobalVarStmt):
					res = VarGlobal(stmt.restype, id)
				else:
					raise FatalError()
				res.declareat = weakref.proxy(stmt)
				return res
			elif isinstance(stmt, _function_stmt):
				#return funcid(stmt.prototype, id)
				return ConstFunctionAddress(stmt.prototype, id)
			elif isinstance(stmt, TypedefStmt):
				return stmt.restype
			else:
				raise
		return None
			
	ModuleFile.__getid = __getid
	
	
	def addstatement(me, scope, stmt):
		scope.statements += [stmt]
		stmt.parent = weakref.proxy(scope)
		scope.first_token = stmt.first_token
		scope.last_token  = stmt.last_token
	
	
	def typedef(me, scope, restype, name, first_token, last_token):
		#if name == 'Py_ssize_t':
		#	import pdb;pdb.set_trace()
		if restype == None:
			import pdb;pdb.set_trace()
		if is_lefttype(restype):
			raise FatalError()
		stmt = TypedefStmt(restype, name, first_token, last_token)
			
		if name in scope.__ids:
			warnings.warn(DefineDuplication(stmt, scope.__ids[name]))
			#scope.statements += [DummyStmt(first_token, last_token)]
			me.addstatement(scope, DummyStmt(first_token, last_token))
			return
		
		#stmt.parent = weakref.proxy(scope)
		#scope.statements += [stmt]
		
		me.addstatement(scope, stmt)
		scope.__ids[name] = stmt
		
		if is_usertype(restype) and strip_options(restype).id == '':
			strip_options(restype).id = 'typedefas(%s)'%name
		return stmt
		
	def definemember(me, scope, restype, name, bitsize, first_token, last_token):
		if not isinstance(scope, StructDefine) and not isinstance(scope, UnionDefine):
			raise FatalError()
		
		if name and name in scope.__members:
			warnings.warn(DefineDuplication(stmt, scope.__members[name]))
			return scope.__members[name]
			
		if scope.restype.fields is None:
			scope.restype.fields = []
		
		stmt = DefineMemberStmt(restype, name, bitsize, first_token, last_token)
		scope.restype.fields += [(name,restype)]
		
		#stmt.parent = weakref.proxy(scope)
		#scope.statements += [stmt]
		
		me.addstatement(scope, stmt)
		scope.__members[name] = stmt
		
		if is_usertype(restype) and strip_options(restype) == '':
			strip_options(restype).id = 'varas(%s)'%name
			
		return stmt
			
	def list_type_cherk(me, restype, values, token):
		if is_array(restype):
			typ = target_type(restype)
			for i,v in enumerate(values):
				if type(v) == list:
					typ,_ = me.list_type_cherk(typ, v, token)
				elif is_array(typ):
					size = strip_options(typ)._size
					newv = values[i:size+i]
					_,newv = me.list_type_cherk(typ, newv, token)
					values = values[:i] + [newv] + values[len(newv)+i:]
				else:
					require_cast = me._assign_type_check(typ, v, token)
					if require_cast:
						values[i] = me.implicit_cast(scope, typ, v)
			if is_unsizedarray(restype):
				restype = sizedarray_type(typ, i+1)
			else:
				if restype._size < i+1:
					msg = '初期化子の数が多すぎます'
					raise TypeError(values[restype._size].first_token, msg)
			return restype, values
		if is_usertype(restype) and isinstance(strip_options(restype), td_struct):
			struct = strip_options(restype)
			for i,(_,typ) in enumerate(struct.fields):
				if i >= len(values):
					break
				v = values[i]
				if type(v) == list:
					me.list_type_cherk(typ, v, token)
				elif is_usertype(typ):
					newv = values[i:len(strip_options(typ).fields)+i]
					_,newv = me.list_type_cherk(typ, newv, token)
					values = values[:i] + [newv] + values[len(strip_options(typ).fields)+i:]
				else:
					require_cast = me._assign_type_check(typ, v, token)
					if require_cast:
						print(require_cast, v.restype, typ)
						values[i] = me.implicit_cast(scope, typ, v)
						
			if len(struct.fields) < len(values):
				msg = '初期化子の数が多すぎます'
				raise TypeError(values[restype._size].first_token, msg)
			return restype, values
				
			
		elif is_usertype(restype) and isinstance(strip_options(restype), td_union):
			raise FatalError()
		else:
			msg = '初期化子が不正です'
			raise TypeError(values[0].first_token, msg)
				
		
	def declarevar(me, scope, restype, name, init, strage, options, first_token, last_token):
		if not isinstance(strage, str):
			raise FatalError()
		
		if isinstance(scope, _execscope):
			if strage == 'extern':
				stmt = LocalExtern(restype, name, first_token, last_token)
			elif strage == 'static':
				stmt = LocalStaticStmt(restype, name, first_token, last_token)
			elif strage == '':
				stmt = LocalVarStmt(restype, name, first_token, last_token)
			else:
				raise FatalError()
		elif isinstance(scope, ModuleFile):
			if strage == 'extern':
				stmt = GlobalExtern(restype, name, first_token, last_token)
			elif strage == 'static':
				stmt = GlobalStaticStmt(restype, name, first_token, last_token)
			elif strage == '':
				stmt = GlobalVarStmt(restype, name, first_token, last_token)
			else:
				raise FatalError()
		else:
			raise FatalError()
			
		stmt.options= options
		
		if strage == 'extern' and init is not None:
			raise FatalError()
			
		
		if init and type(init) != list and is_errorexp(init):
			init = None
		if name in scope.__ids:
			org = scope.__ids[name]
			if isinstance(org, _externVarStmt) and org.restype == restype:
				pass
			else:
				warnings.warn(DefineDuplication(stmt, scope.__ids[name]))
				#scope.statements += [DummyStmt(first_token, last_token)]
				me.addstatement(scope, DummyStmt(first_token, last_token))
				return
		if init is not None and type(init) == list:
			try:
				stmt.restype,init = me.list_type_cherk(stmt.restype, init, stmt.first_token)
			except NoueError as err:
				warnings.warn(err)
				#scope.statements += [DummyStmt(first_token, last_token)]
				me.addstatement(scope, DummyStmt(first_token, last_token))
				return scope.statements[-1]
		elif init is not None:
			#print(init, init.restype, init.first_token.line_string)
			try:
				require_cast = me._assign_type_check(stmt.restype, init, first_token)
				if require_cast:
					init = me.implicit_cast(scope, stmt.restype, init)
				if is_unsizedarray(stmt.restype) and is_sizedarray(init.restype):
					typ = target_type(stmt.restype)
					typ = sizedarray_type(typ, arraysize(init.restype))
					if is_const(stmt.restype):
						typ = const_type(typ)
					stmt.restype = typ
				elif is_sizedarray(stmt.restype) and is_sizedarray(init.restype):
					if arraysize(stmt.restype) < arraysize(init.restype):
						msg = '%sは%sで初期化できません'%(stmt.restype.name, init.restype.name)
						raise TypeError(stmt.first_token, msg)
			except NoueError as err:
				warnings.warn(err)
				#scope.statements += [DummyStmt(first_token, last_token)]
				me.addstatement(scope, DummyStmt(first_token, last_token))
				return scope.statements[-1]
			
		stmt.initexp= init
		#stmt.parent = weakref.proxy(scope)
		#scope.statements += [stmt]
		me.addstatement(scope, stmt)
		scope.__ids[name] = stmt
		
		return stmt
		
	def declfunc(me, scope, prototype, name, strage, options, first_token, last_token):
		if not isinstance(strage, str):
			raise FatalError()
		stmt = DeclareFunctionStmt(prototype, name, first_token, last_token)
		stmt.strage = strage
		stmt.options= options
		
		if name in scope.__ids:
			org = scope.__ids[name]
			err = True
			if isinstance(org, _function_stmt):
				if org.prototype.args is not None and len(org.prototype.args) == len(prototype.args):
					for a1,a2 in zip(org.prototype.args, prototype.args):
						if a1.restype != a2.restype:
							break
					else:
						if org.prototype.has_vararg == prototype.has_vararg:
							err = False
						
			if err:
				warnings.warn(DefineDuplication(stmt, scope.__ids[name]))
				#scope.statements += [DummyStmt(first_token, last_token)]
				me.addstatement(scope, DummyStmt(first_token, last_token))
				return stmt
			
		#stmt.parent = weakref.proxy(scope)
		#scope.statements += [stmt]
		me.addstatement(scope, stmt)
		scope.__ids[name] = stmt
		
		return stmt
		
		
	def definefunc(me, scope, prototype, name, strage, options, first_token):
		stmt = DefineFunctionStmt(prototype, name, first_token, first_token)
		stmt.strage  = strage
		stmt.options = options
		
		stmt.__ids = {}
		stmt.__structs = {}
		stmt.__unions = {}
		stmt.__enums   = {}
		
		stmt.__gotos  = {}
		stmt.__labels = {}
		
		if prototype.args is None:
			raise FatalError()
			
		for argdef in prototype.args:
			if argdef.id:
				stmt.__ids[argdef.id] = argdef
		
		if name in scope.__ids:
			org = scope.__ids[name]
			err = True
			if isinstance(org, _function_stmt):
				if org.prototype.args is not None and len(org.prototype.args) == len(prototype.args):
					for a1,a2 in zip(org.prototype.args, prototype.args):
						if a1.restype != a2.restype:
							break
					else:
						if org.prototype.has_vararg == prototype.has_vararg:
							err = False
						
			if err:
				warnings.warn(DefineDuplication(stmt, scope.__ids[name]))
				return stmt
				
		#stmt.parent = weakref.proxy(scope)
		#scope.statements += [stmt]
		me.addstatement(scope, stmt)
		scope.__ids[name] = stmt
		
		return stmt
		
	def exprstmt(me, scope, exp, last_token):
		stmt = ExprStmt(exp, exp.first_token, last_token)
		#scope.statements += [stmt]
		#stmt.parent = weakref.proxy(scope)
		me.addstatement(scope, stmt)
		return stmt
			
			
	def ifscope(me, scope, first_token, last_token):
		ifscope = If(first_token, last_token)
		#scope.statements += [ifscope]
		#
		#ifscope.parent = weakref.proxy(scope)
		me.addstatement(scope, ifscope)
		
		ifscope.__ids = {}
		ifscope.__structs = {}
		ifscope.__unions  = {}
		ifscope.__enums   = {}
		ifscope.body.__ids     = {}
		ifscope.body.__structs = {}
		ifscope.body.__unions  = {}
		ifscope.body.__enums   = {}
		ifscope.orelse.__ids     = {}
		ifscope.orelse.__structs = {}
		ifscope.orelse.__unions  = {}
		ifscope.orelse.__enums   = {}
		return ifscope
		
	def block(me, scope, first_token):
		newscope = ExecBlock(first_token, first_token)
		#scope.statements += [newscope]
		#newscope.parent = weakref.proxy(scope)
		me.addstatement(scope, newscope)
		
		newscope.__ids = {}
		newscope.__structs = {}
		newscope.__unions  = {}
		newscope.__enums   = {}
		return newscope
		
	def forscope(me, scope, first_token, last_token):
		newscope = For(first_token, last_token)
		#scope.statements += [newscope]
		#newscope.parent = weakref.proxy(scope)
		me.addstatement(scope, newscope)
		
		newscope.__ids = {}
		newscope.__structs = {}
		newscope.__unions  = {}
		newscope.__enums   = {}
		newscope.body.__ids = {}
		newscope.body.__structs = {}
		newscope.body.__unions  = {}
		newscope.body.__enums   = {}
		return newscope
		
	def whilescope(me, scope, first_token, last_token):
		newscope = While(first_token, last_token)
		#scope.statements += [newscope]
		#newscope.parent = weakref.proxy(scope)
		me.addstatement(scope, newscope)
		
		newscope.__ids = {}
		newscope.__structs = {}
		newscope.__unions  = {}
		newscope.__enums   = {}
		newscope.body.__ids = {}
		newscope.body.__structs = {}
		newscope.body.__unions  = {}
		newscope.body.__enums   = {}
		return newscope
		
	def dowhilescope(me, scope, first_token, last_token):
		newscope = DoWhile(first_token, last_token)
		#scope.statements += [newscope]
		#newscope.parent = weakref.proxy(scope)
		me.addstatement(scope, newscope)
		
		newscope.__ids = {}
		newscope.__structs = {}
		newscope.__unions  = {}
		newscope.__enums   = {}
		newscope.body.__ids = {}
		newscope.body.__structs = {}
		newscope.body.__unions  = {}
		newscope.body.__enums   = {}
		return newscope

	def switchscope(me, scope, first_token, last_token):
		newscope = Switch(first_token, last_token)
		#scope.statements += [newscope]
		#newscope.parent = weakref.proxy(scope)
		me.addstatement(scope, newscope)
		
		newscope.__ids = {}
		newscope.__structs = {}
		newscope.__unions  = {}
		newscope.__enums   = {}
		newscope.body.__ids = {}
		newscope.body.__structs = {}
		newscope.body.__unions  = {}
		newscope.body.__enums   = {}
		return newscope


		
	def returnstmt(me, scope, exp, first_token, last_token):
		sc = scope
		while not isinstance(sc, DefineFunctionStmt):
			if sc.parent is None:
				## ここにはこないはず
				raise FatalError()
				msg = '関数スコープの外にreturn文があります'
				warnings.warn(SyntaxError(first_token, msg))
				return None
			sc = sc.parent
		if exp is None:
			if strip_options(sc.prototype.restype) != TD_VOID:
				msg = '値が必要です'
				warnings.warn(SyntaxError(first_token, msg))
				#stmt = DummyStmt(first_token, last_token)
				#scope.statements += [stmt]
				me.addstatement(scope, DummyStmt(first_token, last_token))
				return stmt
				
		else:
			try:
				me._assign_type_check(sc.prototype.restype, exp, first_token)
			except NoueError as err:
				warnings.warn(err)
				return None

		stmt = ReturnStmt(exp, first_token, last_token)
		#stmt.parent = weakref.proxy(scope)
		#scope.statements += [stmt]
		
		me.addstatement(scope, stmt)
		return stmt
		
	def modulefile(me, name):
		mod = ModuleFile(name)
		mod.__ids = {}
		mod.__structs = {}
		mod.__unions  = {}
		mod.__enums   = {}
		return mod
		
	def structscope(me, scope, name, first_token, last_token):
		stmt = StructDefine(name, first_token, last_token)
		error = False
		if name in scope.__structs:
			td = scope.__structs[name]
			if td.fields is not None:
				warnings.warn(DefineDuplication(stmt, td.defined_at))
				td = td_struct(name, first_token)
				error = True
		else:
			td = td_struct(name, first_token)
			if name:
				scope.__structs[name] = td
		td.defined_at = weakref.proxy(stmt)
		stmt.restype = td
		
		stmt.__members = {}
		
		stmt.__ids     = scope.__ids
		stmt.__structs = scope.__structs
		stmt.__unions  = scope.__unions
		stmt.__enums   = scope.__enums
		#stmt.parent = weakref.proxy(scope)
		#
		#scope.statements += [stmt]
		me.addstatement(scope, stmt)
		return stmt
		
		
	def unionscope(me, scope, name, first_token, last_token):
		stmt = UnionDefine(name, first_token, last_token)
		error = False
		if name in scope.__unions:
			td = scope.__unions[name]
			if td.fields is not None:
				warnings.warn(DefineDuplication(stmt, td.defined_at))
				td = td_struct(name, first_token)
				error = True
		else:
			td = td_struct(name, first_token)
			if name:
				scope.__unions[name] = td
		td.defined_at = weakref.proxy(stmt)
		stmt.restype = td
		
		stmt.__members = {}
		
		stmt.__ids     = scope.__ids
		stmt.__structs = scope.__structs
		stmt.__enums   = scope.__enums
		stmt.__unions   = scope.__unions
		#stmt.parent = weakref.proxy(scope)
		#
		#scope.statements += [stmt]
		me.addstatement(scope, stmt)
		return stmt

	def setunionerror(me, union):
		union.restype.fields = []
		return union.restype
		
	def getstruct(me, scope, id):
		if id.value in me.primitives:
			warnings.warn(InvalidTydename(id))
			return td_struct('<error>', first_token)
		return scope.__getstruct(me, id)
	
	def __getstruct(scope, me, id):
		if id.value in scope.__structs:
			td = scope.__structs[id.value]
			return td
		elif scope.parent is not None:
			return me.getstruct(scope.parent, id)
		return None
	_scope.__getstruct = __getstruct
		
	def declstruct(me, scope, id):
		if id.value in scope.__structs:
			raise FatalError()
		td = td_struct(id.value, id)
		scope.__structs[id.value] = td
		return td
		
	def getunion(me, scope, id):
		if id.value in me.primitives:
			warnings.warn(InvalidTydename(id))
			return td_union('<error>', first_token)
		return scope.__getunion(me, id)
	
	def __getunion(scope, me, id):
		if id.value in scope.__unions:
			td = scope.__unions[id.value]
			return td
		elif scope.parent is not None:
			return me.getunion(scope.parent, id)
		return None
	_scope.__getunion = __getunion
		
	def declunion(me, scope, id):
		if id.value in scope.__unions:
			raise FatalError()
		td = td_union(id.value, id)
		scope.__unions[id.value] = td
		return td
		
	def has_member(me, scope, restype, attr):
		if not is_usertype(restype):
			raise FatalError()
		restype = strip_options(restype)
		if restype.fields is None:
			raise FatalError()
			
		return attr in [f[0] for f in restype.fields]
		
	def get_attrtype(me, scope, restype, attr):
		restype = strip_options(restype)
		return {f[0]:f[1] for f in restype.fields}[attr]
		
	class EnumValue:
		def __init__(me, restype, n):
			me.restype = restype
			me.n       = n
		
	def defineenum(me, scope, name, values, first_token, last_token):
		stmt = EnumDefine(name, values, first_token, last_token)
		
		if name in scope.__enums:
			if scope.__enums[name].values is not None:
				warnings.warn(DefineDuplication(stmt, scope.__enums[name]))
				#scope.statements += [DummyStmt(first_token, last_token)]
				me.addstatement(scope, DummyStmt(first_token, last_token))
				return scope.__enums[name].restype
			else:
				stmt.restype = scope.__enums[name].restype
			
		last = -1
		
		result = []
		for id, val in values:
			if val is not None:
				try:
					n = me.eval_constinteger(val)
				except NotConstInteger as err:
					warnings.warn(err)
			else:
				n = last+1
			
			last = n
			val = me.EnumValue(stmt.restype, n)
			result = [(id, val)]
			
		
			scope.__ids[id] = val
			
		stmt.restype.values = result
		stmt.defined_at = first_token
		if name:
			scope.__enums[name] = stmt
		#scope.statements += [stmt]
		
		me.addstatement(scope, stmt)
		return stmt.restype
		
	def getenum(me, scope, id):
		if id.value in me.primitives:
			warnings.warn(InvalidTydename(id))
			return td_enum('<error>', first_token)
		return scope.__getenum(me, id)
	
	def __getenum(scope, me, id):
		if id.value in scope.__enums:
			td = scope.__enums[id.value]
			return td
		elif scope.parent is not None:
			return me.getenum(scope.parent, id)
		return None
	_scope.__getenum = __getenum
	
	def declenum(me, scope, id):
		if id.value in scope.__enums:
			raise FatalError()
		td = td_enum(id.value, id)
		scope.__enums[id.value] = td
		return td

	def breakstmt(me, scope, break_token, semicolon_token):
		stmt = BreakStmt(break_token, semicolon_token)
		#stmt.parent = weakref.proxy(scope)
		me.addstatement(scope, stmt)
		stmt.escapescopes = []
		sc = scope
		stmt.escapescopes += [weakref.proxy(sc)]
		while not isinstance(sc, _loopBlock):
			if isinstance(sc, DefineFunctionStmt):
				msg = 'breakはループの中でなくてはなりません'
				warnings.warn(SyntaxError(first_token, msg))
				break
				
			if sc.parent is None:
				## ここにはこないはず
				raise FatalError()
			stmt.escapescopes += [sc.parent]
			sc = sc.parent
		
		#stmt.escapescopes += [weakref.proxy(sc)]
		#scope.statements += [stmt]
		return stmt
		
	def continuestmt(me, scope, break_token, semicolon_token):
		stmt = ContinueStmt(break_token, semicolon_token)
		#stmt.parent = weakref.proxy(scope)
		me.addstatement(scope, stmt)
		stmt.escapescopes = []
		sc = scope
		stmt.escapescopes += [weakref.proxy(sc)]
		while not isinstance(sc, _loopBlock):
			if isinstance(sc, DefineFunctionStmt):
				msg = 'breakはループの中でなくてはなりません'
				warnings.warn(SyntaxError(first_token, msg))
				break
				
			if sc.parent is None:
				## ここにはこないはず
				raise FatalError()
			stmt.escapescopes += [sc.parent]
			sc = sc.parent
			
		stmt.escapescopes.pop()
		#stmt.escapescopes += [weakref.proxy(sc)]
		#scope.statements += [stmt]
		return stmt
		
	def gotostmt(me, scope, label, goto_token, colon_token):
		sc = scope
		while isinstance(sc, _execscope):
			if isinstance(sc, DefineFunctionStmt):
				func = sc
				break
			sc = sc.parent
		else:
			msg = 'gotoは関数スコープの中でなくてはなりません。'
			warnings.warn(SyntaxError(first_token, msg))
			#scope.statements += [DummyStmt(first_token, last_token)]
			me.addstatement(scope, DummyStmt(first_token, last_token))
			return scope.statements[-1]
			
		
			
		stmt = GotoStmt(label, goto_token, colon_token)
		me.addstatement(scope, stmt)
		#stmt.parent = weakref.proxy(scope)
		#
		#scope.statements += [stmt]
		
		if stmt.label in func.__labels:
			stmt.labelstmt = weakref.proxy(func.__labels[stmt.label])
		else:
			stmt.labelstmt = None
			
		l = func.__gotos.setdefault(stmt.label, [])
		l += [stmt]
		
		return stmt

	def labelstmt(me, scope, label_token, colon_token):
		sc = scope
		while isinstance(sc, _execscope):
			if isinstance(sc, DefineFunctionStmt):
				func = sc
				break
			sc = sc.parent
		else:
			msg = 'ラベルは関数スコープの中でなくてはなりません。'
			warnings.warn(SyntaxError(first_token, msg))
			#scope.statements += [DummyStmt(first_token, last_token)]
			me.addstatement(scope, DummyStmt(first_token, last_token))
			return scope.statements[-1]
			
		if label_token.value in func.__labels:
			msg = 'ラベル%sが重複しています'%label_token.value
			warnings.warn(SyntaxError(first_token, msg))
			#scope.statements += [DummyStmt(first_token, last_token)]
			me.addstatement(scope, DummyStmt(first_token, last_token))
			return scope.statements[-1]
			
		stmt = LabelStmt(label_token, colon_token)
		#stmt.parent = weakref.proxy(scope)
		stmt.escapescopes = []
		
		#scope.statements += [stmt]
		me.addstatement(scope, stmt)
		
		func.__labels[stmt.label] = stmt
		for goto in func.__gotos.setdefault(stmt.label, []):
			goto.labelstmt = weakref.proxy(stmt)
			

		return stmt
		
	def defaultstmt(me, scope, break_token, colon_token):
		stmt = DefaultStmt(break_token, colon_token)
		#stmt.parent = weakref.proxy(scope)
		me.addstatement(scope, stmt)
		stmt.escapescopes = []
		sc = scope
		stmt.escapescopes += [weakref.proxy(sc)]
		while not isinstance(sc, Switch):
			if isinstance(sc, DefineFunctionStmt):
				msg = 'defaultはswitchスコープの中でなくてはなりません'
				warnings.warn(SyntaxError(first_token, msg))
				break
				
			if sc.parent is None:
				## ここにはこないはず
				raise FatalError()
			stmt.escapescopes += [sc.parent]
			sc = sc.parent
			
		#stmt.escapescopes += [weakref.proxy(sc)]
		#scope.statements += [stmt]
		return stmt

	def casestmt(me, scope, exp, break_token, colon_token):

		try:
			n = me.eval_constinteger(exp)
		except NotConstInteger as err:
			warnings.warn(err)	
			#scope.statements += [DummyStmt(first_token, last_token)]
			me.addstatement(scope, DummyStmt(first_token, last_token))
			return
			
		stmt = CaseStmt(n, break_token, colon_token)
		#stmt.parent = weakref.proxy(scope)
		me.addstatement(scope, stmt)
		stmt.escapescopes = []
		sc = scope
		stmt.escapescopes += [weakref.proxy(sc)]
		while not isinstance(sc, Switch):
			if isinstance(sc, DefineFunctionStmt):
				msg = 'defaultはswitchスコープの中でなくてはなりません'
				warnings.warn(SyntaxError(first_token, msg))
				break
				
			if sc.parent is None:
				## ここにはこないはず
				raise FatalError()
			stmt.escapescopes += [sc.parent]
			sc = sc.parent
			
		#stmt.escapescopes += [weakref.proxy(sc)]
		#scope.statements += [stmt]
		return stmt

	def comment(me, scope, token):
		s = token.value.lstrip()
		if s.startswith('@py:'):
			s = 'if 1:' + s[len('@py:'):]
			last = copy.deepcopy(token)
			last.line += len(token.value.splitlines())-1
		stmt = CommentStmt(token)
		#stmt.parent = weakref.proxy(scope)
		#scope.statements += [stmt]
		me.addstatement(scope, stmt)
			
		return stmt
		
		
		
if __name__ == '__main__':
	class dummysize:
		def sizeof(me, *args):
			return 1
	exp = SyntaxCore(dummysize())
	c = CodePositional('', 0, 0, '')
	l = _expression(TD_INT, c, c)
	r = _expression(TD_INT, c, c)
	exp.add(None, l,r)

