#coding: utf8

#日本語
try:
	from .error import *
	from .tokenizer import *
except SystemError:
	import imp
	noue = imp.load_source('noue', './__init__.py')
	from noue.error import *
	from noue.tokenizer import *

class _node:
	pass
	
import weakref
	
class _type_descriptor(_node):
	def __init__(me):
		pass

	@property
	def name(me):
		raise

	def __repr__(me):
		return '<%s>'%me.name
		
class td_error(_type_descriptor):
	def __init__(me):
		_type_descriptor.__init__(me)
		
	@property
	def name(me):
		return '<ErrorType>'
TD_ERROR = td_error()

class td_primitive(_type_descriptor):
	def __init__(me, name):
		_type_descriptor.__init__(me)
		me._name = name
		
	@property
	def name(me):
		return me._name
		
class td_dummy(_type_descriptor):
	def __init__(me):
		_type_descriptor.__init__(me)
		
	@property
	def name(me):
		return '<ErrorType>'
		
		
		
class td_integer(td_primitive):
	def __init__(me, name):
		td_primitive.__init__(me, name)
		
class td_unsigned(td_integer):
	pass
		
		
class td_real(td_primitive):   pass

class td_char(td_integer):
	pass


## standard integer type
TD_INT  = td_integer('int')
TD_LONG = td_integer('long')
TD_SHORT= td_integer('short')
TD_CHAR = td_char('char')

TD_UINT   = td_unsigned('unsigned int')
TD_ULONG  = td_unsigned('unsigned long')
TD_USHORT = td_unsigned('unsigned short')
TD_UCHAR  = td_unsigned('unsigned char')

TD_LONGLONG  = td_integer('long long')
TD_ULONGLONG = td_unsigned('unsigned long long')


## extended integer type
TD_SIZE_T = td_unsigned('size_t')
TD_WCHAR  = td_integer('wchar_t')

TD_FLOAT  = td_real('float')
TD_DOUBLE = td_real('double')



class td_void(_type_descriptor):
	def __init__(me):
		_type_descriptor.__init__(me)
		
	@property
	def name(me):
		return 'void'
TD_VOID = td_void()


class td_leftvalue(_type_descriptor):
	def __init__(me, typ):
		if isinstance(typ, td_leftvalue):
			raise FatalError()
		_type_descriptor.__init__(me)
		me._type = typ

	@property
	def name(me):
		if type(me._type) == tuple:
			import pdb;pdb.set_trace()
		return me._type.name+'&'

class td_const(_type_descriptor):
	def __init__(me, typ):
		if isinstance(typ, td_leftvalue):
			raise FatalError()
		if isinstance(typ, td_const):
			raise FatalError()
		_type_descriptor.__init__(me)
		me._type = typ

	@property
	def name(me):
		if is_pointer(me._type):
			return me._type.name + ' const'
		else:
			return 'const ' + me._type.name

class td_pointer(_type_descriptor):
	def __init__(me, typ):
		if isinstance(typ, td_leftvalue):
			raise FatalError()
		_type_descriptor.__init__(me)
		me._type = typ

	@property
	def name(me):
		return me._type.name + '*'
		



class td_array_base(_type_descriptor):
	pass
	
		
class td_unsized_array(td_array_base):
	def __init__(me, typ):
		if isinstance(typ, td_leftvalue):
			raise FatalError()
		td_array_base.__init__(me)
		me._type = typ
		
	@property
	def name(me):
		return me._type.name + '[]'
		
		
		
class td_sized_array(td_array_base):
	def __init__(me, typ, size):
		if isinstance(typ, td_leftvalue):
			raise FatalError()
		if not isinstance(size, int):
			raise FatalError()
			
		td_array_base.__init__(me)
		me._type = typ
		me._size = size
	
	@property
	def name(me):
		## 多次元配列の時に、字数が反対になることに注意
		return me._type.name + '[%d]'%me._size
		
		
def unsizedarray_type(typ):
	if is_lefttype(typ):
		typ = right_type(typ)
	if typ not in unsizedarray_type.memo:
		unsizedarray_type.memo[typ] = td_unsized_array(typ)
	return unsizedarray_type.memo[typ]
unsizedarray_type.memo = {}

	
def is_array(typ):
	typ = strip_options(typ)
	return isinstance(typ, td_array_base)
	
def is_unsizedarray(typ):
	typ = strip_options(typ)
	return isinstance(typ, td_unsized_array)
		
def sizedarray_type(typ, size):
	if is_lefttype(typ):
		typ = right_type(typ)
	if is_unsizedarray(typ):
		raise FatalError()
	
	if size <= 0:
		raise FatalError()
	
	if (typ,size) not in sizedarray_type.memo:
		sizedarray_type.memo[(typ,size)] = td_sized_array(typ, size)
	return sizedarray_type.memo[(typ,size)]
sizedarray_type.memo = {}


class td_varsized_array(td_array_base):
	def __init__(me, typ):
		if isinstance(typ, td_leftvalue):
			raise FatalError()
		td_array_base.__init__(me)
		me._type = typ

	@property
	def name(me):
		return me._type.name + '[*]'




class td_struct(_type_descriptor):
	def __init__(me, id, pos):
		_type_descriptor.__init__(me)
		me.id = id
		me.fields = None
		me.defined_at  = None
		me.declared_at = pos
	
	@property
	def name(me):
		return 'struct ' + me.id
		
	
class td_union(_type_descriptor):
	def __init__(me, id, pos):
		_type_descriptor.__init__(me)
		me.id = id
		me.fields = []
		me.defined_at  = None
		me.declared_at = pos
	
	@property
	def name(me):
		return 'union ' + me.id

def is_usertype(typ):
	typ = strip_options(typ)
	return isinstance(typ, td_struct) or isinstance(typ, td_union)

class td_enum(td_integer):
	def __init__(me, id, pos):
		td_integer.__init__(me, id)
		me.id = id
		me.values = []
		me.defined_at  = None
		me.declared_at = pos

	@property
	def name(me):
		return 'enum ' + me.id
		
class td_vararg_list_type(_type_descriptor):
	def __init__(me):
		_type_descriptor.__init__(me)

	@property
	def name(me):
		return '...'

		
		
TD_VARARG_LIST = td_vararg_list_type()


def is_type(typ):
	return isinstance(typ, _type_descriptor)

def is_lefttype(typ):
	return isinstance(typ, td_leftvalue)

def left_type(typ):
	if is_lefttype(typ):
		return typ
	
	if typ not in left_type._memo:
		left_type._memo[typ] = td_leftvalue(typ)
	return left_type._memo[typ]
left_type._memo = {}

def right_type(typ):
	if not is_lefttype(typ):
		return typ
	return typ._type
	

# 引数が左辺値なら返り値もconst左辺値になる
def const_type(typ):
	if is_lefttype(typ):
		is_left = True
		typ = right_type(typ)
	else:
		is_left = False
	
	if isinstance(typ, td_const):
		typ = typ._type
	
	if typ not in const_type._memo:
		const_type._memo[typ] = td_const(typ)
		
	typ = const_type._memo[typ]
	if is_left:
		typ = left_type(typ)
	return typ
const_type._memo = {}

def is_const(typ):
	typ = right_type(typ)
	return isinstance(typ, td_const)

# 引数が左辺値でも返り値は右辺値になる
def pointer_type(typ):
	if isinstance(strip_options(typ), td_error):
		return typ
	if is_lefttype(typ):
	#	is_left = True
		typ = right_type(typ)
	#else:
	#	is_left = False
	if typ not in pointer_type.memo:
		pointer_type.memo[typ] = td_pointer(typ)
	
	typ = pointer_type.memo[typ]
	return typ

TD_VOIDP  = td_pointer(TD_VOID)
TD_CVOIDP = td_pointer(const_type(TD_VOID))

pointer_type.memo = {TD_VOID:TD_VOIDP,const_type(TD_VOID):TD_CVOIDP}

def strip_options(typ):
	if not is_type(typ):
		print(typ)
		raise FatalError()
	typ = right_type(typ)
	if isinstance(typ, td_const):
		typ = typ._type
	return typ

	
def is_array(typ):
	typ = strip_options(typ)
	return isinstance(typ, td_array_base)
	
def is_sizedarray(typ):
	typ = strip_options(typ)
	return isinstance(typ, td_sized_array)
	
def is_unsizedarray(typ):
	typ = strip_options(typ)
	return isinstance(typ, td_unsized_array)
	
def arraysize(typ):
	if not is_sizedarray(typ):
		raise FatalError()
	return strip_options(typ)._size

def is_pointer(typ):
	typ = strip_options(typ)
	if isinstance(typ, td_pointer):
		return True
	return isinstance(typ, td_array_base)
	
def target_type(typ):
	if not is_pointer(typ):
		raise FatalError()
		
	return strip_options(typ)._type
	
	
def is_numeric(typ):
	typ = strip_options(typ)
	return isinstance(typ, td_primitive)
	
	
def is_integer(typ):
	typ = strip_options(typ)
	return isinstance(typ, td_integer)
	
def is_real(typ):
	return is_numeric(typ) and not is_integer(typ)
	
def is_unsigned(typ):
	typ = strip_options(typ)
	return isinstance(typ, td_unsigned)

	
def is_bool(typ):
	return is_numeric(typ) or is_pointer(typ) or is_funcptr(typ)
	

_signed_unsigned = {
	(TD_INT,     TD_UINT),
	(TD_LONG,    TD_ULONG),
	(TD_SHORT,   TD_USHORT),
	(TD_CHAR,    TD_UCHAR),
	(TD_LONGLONG,TD_ULONGLONG),
}
_s2u = {s:u for s,u in _signed_unsigned}
_u2s = {u:s for s,u in _signed_unsigned}
def to_unsigned(tid):
	if tid in _s2u:
		return _s2u[tid]
	raise


class argdecl_descriptor(_node):
	def __init__(me, restype, name):
		me.restype = restype
		me.id      = name

def argdecl(restype, name=''):
	return argdecl_descriptor(restype, name)
	
class func_prototype_descriptor(_node):
	def __init__(me, restype, args):
		me.restype = restype
		me.args    = args
		
class error_func(func_prototype_descriptor):
	def __init__(me):
		me.args = None
		me.restype = TD_ERROR
		me.has_vararg = False
		
def is_errorfunc(proto):
	if not isinstance(proto, func_prototype_descriptor):
		raise FatalError()
	return isinstance(proto, error_func)

def prototype(restype, args=None, has_vararg=False):
	if strip_options(restype) == TD_ERROR:
		return error_func()
	if args is not None:
		for a in args:
			if a.restype == TD_ERROR:
				return error_func()
	if args and len(args) == 1 and args[0].restype == TD_VOID:
		args = ()
	func = func_prototype_descriptor(restype, args)
	func.has_vararg = has_vararg
	return func
	
	
class td_funcptr(_type_descriptor):
	def __init__(me, prototype):
		me.prototype = prototype
		
	
	@property
	def name(me):
		s = me.prototype.restype.name
		s += '(*)'
		s += '(%s)'%','.join([a.restype.name for a in me.prototype.args])
		return s
		
def funcptr_type(restype, args, has_vararg=False):
	return td_funcptr(prototype(restype, args, has_vararg))
	
def is_funcptr(typ):
	typ = strip_options(typ) 
	return isinstance(typ, td_funcptr)
	
#class funcid_descriptor(_node):
#	def __init__(me, prototype, id):
#		me.prototype = prototype
#		me.id = id.value
#		me.first_token = id
#		me.last_token  = id
#		
#def funcid(proto, id):
#	return funcid_descriptor(proto, id)
	
	
#def is_func(func):
#	return isinstance(func, funcid_descriptor)

## 構文木中の式オブジェクト


class _expression(_node):
	def __init__(me, restype, first, last):
		if not isinstance(first, CodePositional):
			raise FatalError()
		if not isinstance(last, CodePositional):
			raise FatalError()
		#ASTNode.__init__(me, line, col)
		me.first_token = first
		me.last_token  = last
		
		me.restype = restype
		
def is_expression(exp):
	return isinstance(exp, _expression)

class ErrorExpression(_expression):
	def __init__(me, tok):
		_expression.__init__(me, TD_ERROR, tok, tok)
		
def is_errorexp(exp):
	if not is_expression(exp):
		raise FatalError()
	#return isinstance(exp, ErrorExpression)
	return isinstance(strip_options(exp.restype), td_error)
	
def is_errortype(restype):
	if not is_type(restype):
		raise FatalError()
	#return isinstance(exp, ErrorExpression)
	return isinstance(strip_options(restype), td_error)


	
#class FunctionAddress(_expression):
#	def __init__(me, funcid, token):
#		restype = funcptr_type(funcid.prototype.restype, funcid.prototype.args or ())
#		_expression.__init__(me, restype, token, token)
#		
#		me.func = funcid
		
class ConstFunctionAddress(_expression):
	def __init__(me, prototype, id):
		#restype = funcptr_type(prototype.restype, prototype.args or ())
		restype = funcptr_type(prototype.restype, prototype.args, prototype.has_vararg)
		_expression.__init__(me, restype, id, id)
		me.id = id.value
		
class ConstInteger(_expression):
	def __init__(me, restype, value, token):
		if not is_integer(restype):
			raise FatalError()
		restype = const_type(right_type(restype))
		_expression.__init__(me, restype, token, token)
		
		me.value = value
		if type(me.value) != int:
			raise FatalError()

class ConstReal(_expression):
	def __init__(me, restype, value, token):
		if not is_numeric(restype) or is_integer(restype):
			raise FatalError()
		restype = const_type(right_type(restype))
		_expression.__init__(me, restype, token, token)
		
		me.value = value


class ConstString(_expression):
	def __init__(me, restype, value, token):
		_expression.__init__(me, restype, token, token)
		me.value = value

class ConstChar(_expression):
	def __init__(me, restype, value, token):
		restype = const_type(right_type(restype))
		_expression.__init__(me, restype, token, token)
		me.value = value

class Var_(_expression):
	def __init__(me, restype, id, const_init=None):
		_expression.__init__(me, left_type(restype), id, id)
		me.id     = id.value
		me.declareat = None
		
				
class VarGlobal(Var_):
	pass
	
class VarStaticGlobal(Var_):
	pass

class VarStaticLocal(Var_):
	pass

class VarLocal(Var_):
	pass
	
class VarArg(Var_):
	pass


class _expbinop(_expression):
	def __init__(me, restype, op, left, right):
		_expression.__init__(me, strip_options(restype), left.first_token, right.last_token)
		me.left = left
		me.right= right
		me.op = op

		
class BinOp(_expbinop):
	def __init__(me, restype, op, left, right):
		if is_numeric(left.restype) and is_numeric(right.restype):
			pass
		else:
			print(left.first_token.line_string)
			raise FatalError()
		_expbinop.__init__(me, restype, op, left, right)
		
		
class PtrAdd(_expbinop):
	def __init__(me, op, left, right):
		if is_pointer(left.restype) and is_integer(right.restype):
			pass
		else:
			raise FatalError()
		_expbinop.__init__(me, right_type(left.restype), op, left, right)
		
class PtrSub(_expbinop):
	## restypeはintかlonglong
	def __init__(me, restype, left, right):
		if is_pointer(left.restype) and is_pointer(right.restype):
			pass
		else:
			raise FatalError()
		_expbinop.__init__(me, restype, '-', left, right)

		

class BinCompare(_expbinop):
	def __init__(me, op, left, right):
		_expbinop.__init__(me, TD_INT, op, left, right)
		
		
class BinLogical(_expbinop):
	def __init__(me, op, left, right):
		_expbinop.__init__(me, TD_INT, op, left, right)

	
class _assign(_expression):
	## left.restypeはC++参照型でなくてはならない
	def __init__(me, left, right):
		_expression.__init__(me, left.restype, left.first_token, right.last_token)
		me.left = left
		me.right= right
		
		
		


class Assign(_assign):         pass


class ArgedAssign(_assign):
	## left.restypeはC++参照型でなくてはならない
	def __init__(me, op, left, right):
		_assign.__init__(me, left, right)
		me.op = op
			
class Dot(_expression):
	def __init__(me, restype, owner, attr):
		_expression.__init__(me, left_type(restype), owner.first_token, attr)
		me.owner = owner
		me.attr  = attr.value
		
class Index(_expression):
	def __init__(me, owner, index, last_token):
		restype = target_type(owner.restype)
		_expression.__init__(me, left_type(restype), owner.first_token, last_token)
		me.owner = owner
		me.index  = index

		
class Arrow(_expression):
	def __init__(me, restype, owner, attr):
		_expression.__init__(me, left_type(restype), owner.first_token, attr)
		me.owner = owner
		me.attr  = attr.value

class Cast(_expression):
	def __init__(me, restype, value, token):
		#if is_lefttype(restype):
		#	raise FatalError()
		_expression.__init__(me, right_type(restype), token, value.last_token)
		me.value = value
		
class ImplicitCast(Cast):
	def __init__(me, restype, value):
		Cast.__init__(me, restype, value, value.first_token)

class UnaryOp(_expression): # ! ~ + -
	def __init__(me, restype, op, value):
		_expression.__init__(me, restype, op, value.last_token)
		me.value = value
		me.op = op.value
		
class Addressof(_expression): # ! ~ + -
	def __init__(me, op, value):
		_expression.__init__(me, pointer_type(value.restype), op, value.last_token)
		me.value = value
		
class Dereference(_expression): # ! ~ + -
	def __init__(me, op, value):
		if is_pointer(value.restype):
			_expression.__init__(me, left_type(target_type(value.restype)), op, value.last_token)
		elif is_funcptr(value.restype):
			_expression.__init__(me, value.restype, op, value.last_token)
		me.value = value
		
		
class ImplicitDerefFuncptr(_expression): # ! ~ + -
	def __init__(me, funcptrptr):
		Dereference.__init__(funcptrptr.first_token, funcptrptr)

		
class PreIncl(_expression): # ++ or --
	def __init__(me, op, value):
		if not is_lefttype(value.restype):
			raise FatalError()
		_expression.__init__(me, value.restype, op, value.last_token)
		me.value = value
		me.op = op.value
		
class PostIncl(_expression): # ++ or --
	def __init__(me, value, op):
		if not is_lefttype(value.restype):
			raise FatalError()
		_expression.__init__(me, right_type(value.restype), value.first_token, op)
		me.value = value
		me.op = op.value
		

class Three(_expression):
	def __init__(me, restype, test, true, false):
		_expression.__init__(me, restype, test.first_token, false.last_token)
		me.test = test
		me.true = true
		me.false= false
		
class Comma(_expression):
	def __init__(me, vars):
		_expression.__init__(me, TD_VOID, vars[0].first_token, vars[-1].last_token)
		me.vars = vars
		
		
class _Call(_expression):
	pass
	
class CallFunc(_Call):
	def __init__(me, func, args, last_token):
		#if not is_func(func):
		#	raise FatalError()
		_expression.__init__(me, func.restype.prototype.restype, func.first_token, last_token)
		me.func = func
		me.args = args
		
class CallFuncptr(_Call):
	def __init__(me, funcptr, args, last_token):
		_expression.__init__(me, strip_options(funcptr.restype).prototype.restype, funcptr.first_token, last_token)
		me.func = funcptr
		me.args = args

		
class _statement(_node):
	@property
	def first_token(me):
		return me._first_token
		
	@first_token.setter
	def first_token(me, token):
		if me.first_token.file != token.file:
			return
		
		if me.first_token.line > token.line:
			me._first_token = token
			if me.parent:
				me.parent.first_token = token
				
	@property
	def last_token(me):
		return me._last_token
		
	@last_token.setter
	def last_token(me, token):
		if me.last_token.file != token.file:
			return
		
		if me.last_token.line < token.line:
			me._last_token = token
			if me.parent:
				me.parent.last_token = token
			
	
	def __init__(me, first_token, last_token=None):
		me.file = first_token.file
		
		#me.first_token = first_token
		#me.last_token  = last_token or first_token
		
		me._first_token = first_token
		me._last_token  = last_token or first_token
		me.parent = None
		me.haserror = False
		#if last_token: me.UpdateRange(last_token)

class _simple_stmt(_statement):
	pass
		
class CommentStmt(_simple_stmt):
	def __init__(me, token):
		_simple_stmt.__init__(me, token, token)
		me.value = token.value

class DummyStmt(_simple_stmt):
	pass
	
	

class _declareVarStmt(_simple_stmt):
	## id: 文字列
	## first_token: 型宣言の最初のトークン、または,の次のトークン
	## last_token: ';'または','
	def __init__(me, restype, id, first_token, last_token):
		_simple_stmt.__init__(me, first_token, last_token)
		
		me.restype = restype
		me.id      = id

class _externVarStmt(_declareVarStmt):		
	def __init__(me, restype, id, first_token, last_token):
		_declareVarStmt.__init__(me, restype, id, first_token, last_token)
		me.strage  = 'extern'
		
class LocalExtern(_externVarStmt):
	pass
		
class GlobalExtern(_externVarStmt):
	pass
		
class LocalVarStmt(_declareVarStmt):
	def __init__(me, restype, id, first_token, last_token):
		_declareVarStmt.__init__(me, restype, id, first_token, last_token)
		me.strage  = ''
		me.initexp = None
		
class GlobalVarStmt(_declareVarStmt):
	def __init__(me, restype, id, first_token, last_token):
		_declareVarStmt.__init__(me, restype, id, first_token, last_token)
		me.strage  = ''
		me.initexp = None
		
class LocalStaticStmt(_declareVarStmt):
	def __init__(me, restype, id, first_token, last_token):
		_declareVarStmt.__init__(me, restype, id, first_token, last_token)
		me.strage  = 'static'
		me.initexp = None
		
class GlobalStaticStmt(_declareVarStmt):
	def __init__(me, restype, id, first_token, last_token):
		_declareVarStmt.__init__(me, restype, id, first_token, last_token)
		me.strage  = 'static'
		me.initexp = None
		
class DefineMemberStmt(_declareVarStmt):
	def __init__(me, restype, id, bitsize, first_token, last_token):
		_declareVarStmt.__init__(me, restype, id, first_token, last_token)
		me.bitsize = bitsize
		
		
class ExprStmt(_simple_stmt):
	## id: 文字列
	## first_token: 型宣言の最初のトークン、または,の次のトークン
	## last_token: ';'または','
	def __init__(me, exp, first_token, last_token):
		_simple_stmt.__init__(me, first_token, last_token)
		
		me.value = exp
		

class TypedefStmt(_simple_stmt):
	## id: 文字列
	## first_token: 型宣言の最初のトークン、または,の次のトークン
	## last_token: ';'または','
	def __init__(me, restype, id, first_token, last_token):
		_simple_stmt.__init__(me, first_token, last_token)
		me.restype = restype
		me.id      = id


			
		
		

		
		
class _scope(_statement):
	def __init__(me, first_token, last_token):
		_statement.__init__(me, first_token, last_token)
		me.statements    = []


class _execscope(_scope):
	pass


class _function_stmt(_statement):
	def __init__(me, prototype, id, first_token, last_token):
		me.prototype = prototype
		me.id      = id
		
		me.strage  = None
		me.options = None
		
		_statement.__init__(me, first_token, last_token)
	

class DefineFunctionStmt(_execscope, _function_stmt):
	## id: 文字列
	## first_token: 型宣言の最初のトークン、または,の次のトークン
	## last_token: ';'または','
	def __init__(me, prototype, id, first_token, last_token):
		_function_stmt.__init__(me, prototype, id, first_token, last_token)		
		_execscope.__init__(me, first_token, last_token)
		me.errors = []
		
class DeclareFunctionStmt(_simple_stmt, _function_stmt):
	## id: 文字列
	## first_token: 型宣言の最初のトークン、または,の次のトークン
	## last_token: ';'または','
	def __init__(me, prototype, id, first_token, last_token):
		_function_stmt.__init__(me, prototype, id, first_token, last_token)		
		_simple_stmt.__init__(me, first_token, last_token)
		

					
			
class ExecBlock(_execscope):
	pass
	
class _controlBlock(ExecBlock):
	## id: 文字列
	## first_token: 型宣言の最初のトークン、または,の次のトークン
	## last_token: ';'または','
	def __init__(me, first_token, last_token):
		ExecBlock.__init__(me, first_token, last_token)
		me.body = ExecBlock(first_token, last_token)
		me.body.parent = weakref.proxy(me)
		me.statements += [me.body]
		
class _loopBlock(_controlBlock):
	pass

class For(_loopBlock):
	def __init__(me, first_token, last_token):
		_controlBlock.__init__(me, first_token, last_token)
		me.test     = None
		me.incl     = None

class If(_controlBlock):
	def __init__(me, first_token, last_token):
		_controlBlock.__init__(me, first_token, last_token)
		me.test = None
		
		me.orelse = ExecBlock(first_token, last_token)
		me.orelse.parent = weakref.proxy(me)
		me.statements += [me.orelse]
		
class While(_loopBlock):
	def __init__(me, first_token, last_token):
		_controlBlock.__init__(me, first_token, last_token)
		me.test     = None

class DoWhile(_loopBlock):
	def __init__(me, first_token, last_token):
		_controlBlock.__init__(me, first_token, last_token)
		me.test = None
		

class Switch(_loopBlock):
	def __init__(me, first_token, last_token):
		_controlBlock.__init__(me, first_token, last_token)
		me.test = None
		
class ReturnStmt(_simple_stmt):
	def __init__(me, exp, first_token, last_token):
		_simple_stmt.__init__(me, first_token, last_token)
		
		me.value = exp
		
		
class CaseStmt(_simple_stmt):
	def __init__(me, n, first_token, last_token):
		if type(n) != int:
			raise FatalError()
		_simple_stmt.__init__(me, first_token, last_token)
		
		me.value = n
		
		
class DefaultStmt(_simple_stmt):
	def __init__(me, first_token, last_token):
		_simple_stmt.__init__(me, first_token, last_token)
		
		


class GotoStmt(_simple_stmt):
	def __init__(me, label, first_token, last_token):
		_simple_stmt.__init__(me, first_token, last_token)
		
		me.label = label
		
		
class LabelStmt(_simple_stmt):
	def __init__(me, label_token, colon_token):
		_simple_stmt.__init__(me, label_token, colon_token)
		
		me.label = label_token.value
		

class BreakStmt(_simple_stmt):
	def __init__(me, break_token, semicolon_token):
		_simple_stmt.__init__(me, break_token, semicolon_token)
		
		

class ContinueStmt(_simple_stmt):
	def __init__(me, continue_token, semicolon_token):
		_simple_stmt.__init__(me, continue_token, semicolon_token)
		
		
class EnumDefine(_simple_stmt):
	def __init__(me, name, values, first_token, last_token):
		_simple_stmt.__init__(me, first_token, last_token)
		
		me.restype = td_enum(name, first_token)
		me.values = values
		me.id = name
		
		
		
			

class StructDefine(_scope):
	def __init__(me, id, first_token, last_token):
		_scope.__init__(me, first_token, last_token)
		me.id = id
		
		
class UnionDefine(_scope):
	def __init__(me, id, first_token, last_token):
		_scope.__init__(me, first_token, last_token)
		me.id  = id


class ModuleFile(_scope):
	@property
	def first_token(me):
		me._first_token
		
	@first_token.setter
	def first_token(me, token):
		if me.first_token is None:
			me._first_token = token
			return
		
		if me.first_token.file != token.file:
			return
			
		if me.first_token.line > token.line:
			me._first_token = token
			
	@property
	def last_token(me):
		me._last_token
		
	@last_token.setter
	def last_token(me, token):
		if me.last_token is None:
			me._last_token = token
			return
		
		if me.last_token.file != token.file:
			return
			
		if me.last_token.line < token.line:
			me._last_token = token
		
	
	def __init__(me, name=''):
		me._first_token = None
		me._last_token  = None

		me.name = name
		me.parent = None
		me.statements = []
	
