# coding: utf8
#from cxstmt import *
#from cxtokenizer import *
try:
	from .coresyntax import *
except SystemError:
	import imp
	noue = imp.load_source('noue', './__init__.py')
	from noue.coresyntax import *
#from cxerror import *
import warnings

from os.path import split as path_split, splitext


#class ConstInteger:
#	def __init__(me, tok):
#		me.value = tok.value
#		me.file  = tok.file
#		me.line  = tok.line
#		me.col   = tok.col
#		me.restype = TID_INT
#
#	def ConstEval(me):
#		return me
#


#class SyntaxKeyword:
#	def __init__(me, name):
#		me.name = name
#		
#	def __eq__(me, right):
#		return me.__req__(right)
#		
#	def __req__(me, left):
#		return left.type == 'ID' and left.value == me.name
#		
#FOR      = SyntaxKeyword('for')
#IF       = SyntaxKeyword('if')
#WHILE    = SyntaxKeyword('while')
#SWITCH   = SyntaxKeyword('switch')
#ELSE     = SyntaxKeyword('else')
#STRUCT   = SyntaxKeyword('struct')
#DO       = SyntaxKeyword('do')
#RETURN   = SyntaxKeyword('return')
#BREAK    = SyntaxKeyword('break')
#CONTINUE = SyntaxKeyword('continue')


class Parser:
	def __init__(me, compilercore):
		me.tokens = []
		me._index  = 0
		me.errors = []
		me.compiler = compilercore
		
	
	class InsertComment(NoueException):
		def __init__(me, token):
			NoueException.__init__(me, token, '')
			me.token = token

	def seek(me, offset=1):
		me._index += offset
		yield from me.load(0)

	def load(me, size=1):
		while me._index+size >= len(me.tokens):
			try:
				toks = (yield)
				#if toks is None:
				#	break
				me.tokens += toks
			except NoueException as ins:
				warnings.warn(ins)
				pass
				
				
		return

	@property
	def cur(me):
		return me.tokens[me._index]
		
	def next(me, index):
		#while me._index+index >= len(me.tokens):
		#	me.tokens += (yield)
		yield from me.load(index)
		return me.tokens[me._index + index]
		
	def prev(me, index):
		return me.tokens[me._index - index]
	
			
	
	def parse_args(me, scope):
		if me.cur.type != '(':
			raise FatalError()
		
		yield from me.seek()
		if me.cur.type == ')':
			#yield from me.seek()
			return []
		
		args = []
		while 1:
			arg = yield from me.parse_expression(scope)
			args += [arg]
			if me.cur.type == ')':
				#yield from me.seek()
				break
			if me.cur.type != ',':
				## ")"の書き忘れと判断して継続する
				warnings.warn(MissingToken(me.cur, ')'))
				me._index -= 1
				break
				
			yield from me.seek()
				
		
		return args
			
		
		
	def parse_term(me, scope):
		if me.cur.type == 'CI':
			res = me.compiler.const_integer(scope, me.cur)
		elif me.cur.type == 'CR':
			res = me.compiler.const_real(scope, me.cur)
		elif me.cur.type == 'CS':
			prefix = me.cur.prefix
			s = me.cur.value
			first = me.cur
			tok = yield from me.next(1)
			while tok.type == 'CS' and tok.prefix == prefix:
				s += tok.value
				yield from me.seek()
				tok = yield from me.next(1)
			tok = TokenDoubleQuote(repr(s), prefix, first.file, first.line, first.col, first.line_string, first.encoding)
			res = me.compiler.const_string(scope, tok)
		elif me.cur.type == 'CC':
			res = me.compiler.const_char(scope, me.cur)
		elif me.cur.type == 'ID':
			id = me.cur
			#yield from me.load()
			nxt = yield from me.next(1)
			if nxt.type == '(':
				yield from me.seek()
				#func = scope.GetFunction(id)
				args = yield from me.parse_args(scope)
				yield from me.seek()
				return me.compiler.call_id(scope, id, args, me.cur)
			else:
				term = me.compiler.getid(scope, id)
				#term = scope.GetId(id)
				if term is None:
					warnings.warn(NotDefined(id))
					term = me.compiler.errorexp(id)
				elif not is_expression(term):
					warnings.warn(ParseUnexpectedToken(id))
					## エラー用のダミーExpresisonを返して継続
					term = me.compiler.errorexp(id)
				
				yield from me.seek()
				return term
			
		elif me.cur.type == '(':
			yield from me.seek()
			res = yield from me.parse_comma(scope)
			if me.cur.type != ')':
				warnings.warn(MissingToken(me.cur, ")"))
				## ")"の書き忘れとして継続
				
		else:
			#import pdb;pdb.set_trace()
			warnings.warn(ParseUnexpectedToken(me.cur))
			res = me.compiler.errorexp(me.cur)
			## 想定外のトークン 無視して継続する
			
		yield from me.seek()
		return res
		
	def parse_sufop(me, scope):
		res = yield from me.parse_term(scope)
		ops = {'++', '--', '.', '->', '[', '('}
		while me.cur.type in ops:
			if me.cur.type == '++':
				res = me.compiler.postincl(scope, res, me.cur)
			elif me.cur.type == '--':
				res = me.compiler.postdecl(scope, res, me.cur)
			elif me.cur.type == '.':
				yield from me.seek()
				if me.cur.type != 'ID':
					## .の後がメンバ名でない場合、.のみ読み飛ばして継続
					warnings.warn(ParseUnexpectedToken(me.cur))
					me._index -= 1
					
				else:
					res = me.compiler.dot(scope, res, me.cur)
			elif me.cur.type == '->':
				yield from me.seek()
				if me.cur.type != 'ID':
					## ->の後がメンバ名でない場合、->のみ読み飛ばして継続
					warnings.warn(ParseUnexpectedToken(me.cur))
					me._index -= 1
					
				res = me.compiler.arrow(scope, res, me.cur)
			elif me.cur.type == '[':
				yield from me.seek()
				index = yield from me.parse_expression(scope)
				if me.cur.type != ']':
					## "]"の書き忘れとして継続
					warnings.warn(MissingToken(me.cur, "]"))
					me._index -= 1
					
				res = me.compiler.index(scope, res, index, me.cur)
			elif me.cur.type == '(':
				## 関数ポインタの関数呼び出し
				## 関数そのものの関数呼び出しはtermで処理するので注意
				args = yield from me.parse_args(scope)
				res = me.compiler.call_funcptr(scope, res, args, me.cur)
				#print(me.cur)
				#raise
			yield from me.seek()
		return res
		
	def parse_cast(me, scope):
		first_token = me.cur
		tid, _ = yield from me.parse_typespec(scope, False)
			
		restype = tid
		while me.cur.type == '*':
			restype = pointer_type(restype)
			yield from me.seek()
			if me.cur.value == 'const':
				restype = const_type(restype)
				yield from me.seek()
		if me.cur.type == '(':
			restype, _ = yield from me.parse_funcptrtype(scope, restype)

		return restype
		
		
	def parse_preop(me, scope):
		op_token = me.cur
		if me.cur.type == '+':
			yield from me.seek()
			res = yield from me.parse_preop(scope)
			return me.compiler.unaryplus(scope, op_token, res)
		elif me.cur.type == '++':
			yield from me.seek()
			res = yield from me.parse_preop(scope)
			return me.compiler.preincl(scope, op_token, res)
		elif me.cur.type == '-':
			yield from me.seek()
			res = yield from me.parse_preop(scope)
			return me.compiler.unaryminus(scope, op_token, res)
		elif me.cur.type == '--':
			yield from me.seek()
			res = yield from me.parse_preop(scope)
			return me.compiler.predecl(scope, op_token, res)
		elif me.cur.type == '*':
			yield from me.seek()
			res = yield from me.parse_preop(scope)
			return me.compiler.dereference(scope, op_token, res)
		elif me.cur.type == '&':
			yield from me.seek()
			res = yield from me.parse_preop(scope)
			return me.compiler.addressof(scope, op_token, res)
		elif me.cur.type == '!':
			yield from me.seek()
			res = yield from me.parse_preop(scope)
			return me.compiler.logicalnot(scope, op_token, res)
		elif me.cur.type == '~':
			yield from me.seek()
			res = yield from me.parse_preop(scope)
			return me.compiler.bitnot(scope, op_token, res)
		elif me.cur.type == '(':
			back = me._index
			yield from me.seek()
			
			try:
				tid = yield from me.parse_cast(scope)
				if me.cur.type != ')':
					## ")"の書き忘れとして継続
					warnings.warn(ParseUnexpectedToken(me.cur))
					me._index -= 1
				yield from me.seek()
				res = yield from me.parse_preop(scope)
				return me.compiler.cast(scope, tid, res, op_token)
			except NotTypeDescriptor as err:
				pass
			me._index = back
			return (yield from me.parse_sufop(scope))
				


		elif me.cur.value == 'sizeof':
			sizeofid = me.cur
			yield from me.seek()
			if me.cur.type == '(':
				back = me._index
				try:
					yield from me.seek()
					tid = yield from me.parse_cast(scope)
					if me.cur.type != ')':
						## ':'の書き忘れとして継続
						warnings.warn(MissingToken(me.cur, ":"))
						me._index -= 1
					yield from me.seek()
					return  me.compiler.sizeofexp(tid, sizeofid)
				except NotTypeDescriptor:
					me._index = back
					
			res = yield from me.parse_preop(scope)
			return  me.compiler.sizeofexp(res.restype, sizeofid)
			
		else:
			return (yield from me.parse_sufop(scope))
			
	def parse_mul(me, scope):
		#left = yield from me.parse_preop(scope)
		left = yield from me.parse_preop(scope)
		while me.cur.type in {'*', '/', '%'}:
			op = me.cur.type

			yield from me.seek()
			#right = yield from parse_preop(scope)
			right = yield from me.parse_preop(scope)

			if op == '*':
				left = me.compiler.mul(scope, left, right)
			elif op == '/':
				left = me.compiler.div(scope, left, right)
			elif op == '%':
				left = me.compiler.mod(scope, left, right)
		return left
		
	def parse_add(me, scope):
		left = yield from me.parse_mul(scope)
		while me.cur.type in {'+', '-'}:
			op = me.cur.type
			yield from me.seek()
			right = yield from me.parse_mul(scope)
			if op == '+':
				left = me.compiler.add(scope, left, right)
			elif op == '-':
				left = me.compiler.sub(scope, left, right)
		return left
		
	def parse_shift(me, scope):
		left = yield from me.parse_add(scope)
		while me.cur.type in {'<<', '>>'}:
			op = me.cur.type
			yield from me.seek()
			right = yield from me.parse_add(scope)
			if op == '<<':
				left = me.compiler.lshift(scope, left, right)
			elif op == '>>':
				left = me.compiler.rshift(scope, left, right)
		return left
		
		
	def parse_compare(me, scope):
		left = yield from me.parse_shift(scope)
		while me.cur.type in {'<', '>', '<=', '>='}:
			op = me.cur.type
			yield from me.seek()
			right = yield from me.parse_shift(scope)
			if op == '<':
				left = me.compiler.lessthan(scope, left, right)
			elif op == '<=':
				left = me.compiler.lessequal(scope, left, right)
			elif op == '>':
				left = me.compiler.greaterthan(scope, left, right)
			elif op == '>=':
				left = me.compiler.greaterequal(scope, left, right)
		return left
				
		
		
	def parse_eq(me, scope):
		left = yield from me.parse_compare(scope)
		
		while me.cur.type in {'==', '!='}:
			op = me.cur.type
			yield from me.seek()

			right = yield from me.parse_compare(scope)

			if op == '==':
				left = me.compiler.equal(scope, left, right)
			elif op == '!=':
				left = me.compiler.notequal(scope, left, right)
				
		return left
		
	def parse_bitand(me, scope):
		left = yield from me.parse_eq(scope)
		if me.cur.type == '&':
			yield from me.seek()
			right = yield from me.parse_eq(scope)
			left = me.compiler.bitand(scope, left, right)
				
		return left
		
	def parse_bitxor(me, scope):
		left = yield from me.parse_bitand(scope)
		while me.cur.type == '^':
			yield from me.seek()
			right = yield from me.parse_bitand(scope)
			left = me.compiler.bitxor(scope, left, right)
				
		return left
		
	def parse_bitor(me, scope):
		left = yield from me.parse_bitxor(scope)
		while me.cur.type == '|':
			yield from me.seek()
			right = yield from me.parse_bitxor(scope)
			left = me.compiler.bitor(scope, left, right)
				
		return left
		
	def parse_logicaland(me, scope):
		left = yield from me.parse_bitor(scope)
		while me.cur.type == '&&':
			yield from me.seek()
			right = yield from me.parse_bitor(scope)
			left = me.compiler.logicaland(scope, left, right)
				
		return left

	def parse_logicalor(me, scope):
		left = yield from me.parse_logicaland(scope)
		while me.cur.type == '||':
			yield from me.seek()
			right = yield from me.parse_logicaland(scope)
			left = me.compiler.logicalor(scope, left, right)
				
		return left

	def parse_three(me, scope):
		res = yield from me.parse_logicalor(scope)
		if me.cur.type == '?':
			yield from me.seek()
			true = yield from me.parse_three(scope)
			if me.cur.type != ':':
				## ':'の書き忘れとして継続
				warnings.warn(MissingToken(me.cur, ":"))
				me._index -= 1
			yield from me.seek()
			false = yield from me.parse_three(scope)
			res = me.compiler.three(scope, res, true, false)
		return res

	def parse_assign(me, scope):
		res = yield from me.parse_three(scope)
		ops = []
		vs  = []
		while me.cur.type in {'=', '+=', '-=', '*=', '/=', '%='
								, '>>=', '<<=', '|=', '&=', '^=', }:
			vs += [res]
			ops += [me.cur.type]
			yield from me.seek()
			res = yield from me.parse_three(scope)

		while ops:
			op  = ops.pop()
			trg = vs.pop()
			if op == '=':
				res = me.compiler.assign(scope, trg, res)
			elif op == '+=':
				res = me.compiler.assign_add(scope, trg, res)
			elif op == '-=':
				res = me.compiler.assign_sub(scope, trg, res)
			elif op == '*=':
				res = me.compiler.assign_mul(scope, trg, res)
			elif op == '/=':
				res = me.compiler.assign_div(scope, trg, res)
			elif op == '%=':
				res = me.compiler.assign_mod(scope, trg, res)
			elif op == '<<=':
				res = me.compiler.assign_lshift(scope, trg, res)
			elif op == '>>=':
				res = me.compiler.assign_rshift(scope, trg, res)
			elif op == '|=':
				res = me.compiler.assign_bitor(scope, trg, res)
			elif op == '&=':
				res = me.compiler.assign_bitand(scope, trg, res)
			elif op == '^=':
				res = me.compiler.assign_bitxor(scope, trg, res)

		return res
		
	def parse_comma(me, scope):
		top = yield from me.parse_expression(scope)
		
		vars = [top]
		while me.cur.type == ',':
			yield from me.seek()
			nxt = yield from me.parse_expression(scope)
			vars += [nxt]
		if len(vars) == 1:
			return top
		else:
			return me.compiler.comma(scope, vars)
		
	def is_exptoken(me, tok):
		if tok.type in {'ID', '+', '-', '++', '--', '*', '!', '(', '&', '~', '^'}:
			return True
		if tok.type[0] == 'C':
			return True
		return False
		
	def parse_expression(me, scope):
		if not me.is_exptoken(me.cur):
			#import pdb;pdb.set_trace()
			warnings.warn(ParseUnexpectedToken(me.cur))
			yield from me.seek()
			return me.compiler.errorexp(me.prev(1))
		#if me.cur.type == 'CI':
		#	res = yield from me.parse_term(scope)
		#	return res
		#import pdb;pdb.set_trace()
		res = yield from me.parse_assign(scope)
		return res

	def parse_enum(me, scope):
		if me.cur.value != 'enum':
			raise FatalError()
		first_token = me.cur

		yield from me.seek()

		nxt = yield from me.next(1)

		if me.cur.type == 'ID' and nxt.type == '{':
			name = me.cur.value
			#struct_scope = scope.CreateEnumStmt(me.cur.value, first_token)
			yield from me.seek(2)
			values = []
			last_value = -1
			while me.cur.type != '}':
				if me.cur.type != 'ID':
					warnings.warn(ParseUnexpectedToken(me.cur))
					yield from me.seek()
					continue
					
				id = me.cur.value
				yield from me.seek()
				if me.cur.type == '=':
					yield from me.seek()
					exp = yield from me.parse_expression(scope)
				else:
					exp = None
				values += [(id, exp)]
				if me.cur.type == '}':
					#yield from me.seek()
					break
					
				if me.cur.type != ',':
					## ","の書き忘れとして継続
					warnings.warn(MissingToken(me.cur, ":"))
					me._index -= 1
				yield from me.seek()
			restype = me.compiler.defineenum(scope, name, values, first_token, me.cur)
			#scope.DefineEnum(name, values, first_token, me.cur)
		elif me.cur.type == '{':
			#name = '%s(%d,%d)'%(splitext(path_split(first_token.file)[1])[0]
			#					, first_token.line, first_token.col)
			#struct_scope = scope.CreateStructScope(name, first_token)					
			name = ''
			yield from me.seek()
			values = []
			last_value = -1
			while me.cur.type != '}':
				if me.cur.type != 'ID':
					warnings.warn(ParseUnexpectedToken(me.cur))
					yield from me.seek()
					continue
				id = me.cur.value
				yield from me.seek()
				if me.cur.type == '=':
					yield from me.seek()
					exp = yield from me.parse_expression(scope)
				else:
					exp = None
				values += [(id, exp)]
				if me.cur.type == '}':
					#yield from me.seek()
					break
					
				if me.cur.type != ',':
					## ","の書き忘れとして継続
					warnings.warn(MissingToken(me.cur, ":"))
					me._index -= 1
				yield from me.seek()
			#print(values)
			#raise
			#scope.DefineEnum(name, values, first_token, me.cur)
			restype = me.compiler.defineenum(scope, name, values, first_token, me.cur)
		elif me.cur.type == 'ID':
			#name = me.cur.value
			restype = me.compiler.getenum(scope, me.cur)
			if restype is None:
				restype = me.compiler.declenum(scope, me.cur)
			
			
			
		yield from me.seek(1)
		#return scope.GetEnumTid(name)
		return restype


	def parse_struct(me, scope):		
		if me.cur.value != 'struct':
			raise FatalError()
			
		first_token = me.cur
		
		yield from me.seek()
		
		nxt = yield from me.next(1)
		
		if me.cur.type == 'ID' and nxt.type == '{':
			with warnings.catch_warnings(record=True) as rec:
				warnings.filterwarnings('always')
				struct_scope = me.compiler.structscope(scope, me.cur.value, first_token, me.cur)
				
				yield from me.seek(2)
				while me.cur.type != '}':
					yield from me.parse_struct_body(struct_scope)

			for w in rec:
				if isinstance(w.message, NoueError):
					struct_scope.restype.fields = []
					struct_scope.haserror = True
				#print('from struct', w)
				warnings.warn_explicit(w.message, w.category, w.filename, w.lineno)#, r.module, r.registry)
				
			res = struct_scope.restype
		elif me.cur.type == '{':
			with warnings.catch_warnings(record=True) as rec:
				warnings.filterwarnings('always')
				struct_scope = me.compiler.structscope(scope, '', first_token, me.cur)
				
				yield from me.seek()
				while me.cur.type != '}':
					yield from me.parse_struct_body(struct_scope)
			for w in rec:
				if isinstance(w.message, NoueError):
					struct_scope.restype.fields = []
					struct_scope.haserror = True
				#print('from struct', w)
				warnings.warn_explicit(w.message, w.category, w.filename, w.lineno)#, r.module, r.registry)
	
			res = struct_scope.restype
		elif me.cur.type == 'ID':
			## sturuct type_t *var; みたいなパターン
			
			name = me.cur.value
			res = me.compiler.getstruct(scope, me.cur)
			if res is None:
				res = me.compiler.declstruct(scope, me.cur)
		else:
			raise
		yield from me.seek(1)
		return res

	def parse_union(me, scope):		
		if me.cur.value != 'union':
			raise FatalError()
			
		first_token = me.cur
		
		yield from me.seek()
		
		nxt = yield from me.next(1)
		
		if me.cur.type == 'ID' and nxt.type == '{':
			with warnings.catch_warnings(record=True) as rec:
				warnings.filterwarnings('always')
				union_scope = me.compiler.unionscope(scope, me.cur.value, first_token, me.cur)
				
				yield from me.seek(2)
				while me.cur.type != '}':
					yield from me.parse_struct_body(union_scope)

			for w in rec:
				if isinstance(w.message, NoueError):
					union_scope.restype.fields = []
					union_scope.haserror = True
				#print('from union', w)
				warnings.warn_explicit(w.message, w.category, w.filename, w.lineno)#, r.module, r.registry)
				
			res = union_scope.restype
		elif me.cur.type == '{':
			with warnings.catch_warnings(record=True) as rec:
				warnings.filterwarnings('always')
				union_scope = me.compiler.unionscope(scope, '', first_token, me.cur)
				
				yield from me.seek()
				while me.cur.type != '}':
					yield from me.parse_struct_body(union_scope)
					
			for w in rec:
				if isinstance(w.message, NoueError):
					union_scope.restype.fields = []
					union_scope.haserror = True
				#print('from union', w)
				warnings.warn_explicit(w.message, w.category, w.filename, w.lineno)#, r.module, r.registry)
				
			res = union_scope.restype
		elif me.cur.type == 'ID':
			## sturuct type_t *var; みたいなパターン
			
			name = me.cur.value
			res = me.compiler.getunion(scope, me.cur)
			if res is None:
				res = me.compiler.declunion(scope, me.cur)
		else:
			raise
		yield from me.seek(1)
		return res
		

	def parse_tid_id(me, scope):
		id = me.cur
		yield from me.seek()
		
		#nxt = yield from me.next(1)
		if id.value == 'long' and me.cur.value in ('long', 'double'):
			id = copy_tokens([id], id)[0]
			id.value = 'long ' + me.cur.value
			yield from me.seek()
			

		td = me.compiler.getid(scope, id)
		
		if not is_type(td):
			raise NotTypeDescriptor(id)

		return td 
			
	## @return: tid, strage
	##          strage:       ストレージを示すTokenオブジェクト
	def parse_typespec(me, scope, has_strage=True):
		#affected = False
		options = set()
		_strage = {'static', 'register', 'auto', 'typedef', 'extern', 'inline'}
		Options = {'const', 'unsigned', 'signed', 'volatile'}.union(_strage)
		
		strage = ''
			
		while me.cur.value in Options:
			if me.cur.value in _strage:
				if not has_strage:
					warnings.warn(SemanticError(me.cur, 'この位置の%s指定は不正です。'%me.cur.value))
				strage = me.cur.value
			else:
				options.add(me.cur.value)
			yield from me.seek()
		
		if me.cur.value == 'struct':
			tid = yield from me.parse_struct(scope)
			#affected = True
		elif me.cur.value == 'enum':
			tid = yield from me.parse_enum(scope)
			#affected = True
		elif me.cur.value == 'union':
			tid = yield from me.parse_union(scope)
			#affected = True
		elif me.cur.type == 'ID':
			try:
				tid = yield from me.parse_tid_id(scope)
			except NotTypeDescriptor as ntd:
				if 'unsigned' in options or 'signed' in options:
					tid = TD_INT
				else:
					raise
		else:		
			if options.intersection({'signed', 'unsigned'}):
				## unsigned intのintは省略可能
				if me.cur.type == 'ID' and \
						me.cur.value in me.primitive and \
						is_integer(me.primitive[me.cur.value]):
					
					tid = me.primitive[me.cur.value]
					yield from me.seek()
				else:
					tid = TD_INT
			else:
				#import pdb;pdb.set_trace()
				## 不正なトークン。読み飛ばして継続
				#import pdb;pdb.set_trace()
				#warnings.warn(ParseUnexpectedToken(me.cur))
				#yield from me.seek()
				#tid = me.compiler.errortype()
				raise NotTypeDescriptor(me.cur)

		while me.cur.type in Options:
			if me.cur.type in _strage:
				if not has_strage:
					warnings.warn(SemanticError(me.cur, 'この位置の%s指定は不正です。'%me.cur.value))
				strage = me.cur.value
			else:
				options.add(me.cur.value)
			yield from me.seek()
		
		if 'unsigned' in options:
			tid = to_unsigned(tid)
			
		if 'const' in options:
			tid = const_type(tid)
			
		return tid, strage#, affected
	
	
		
	def parse_funcptrtype(me, scope, restype):
		##以下のように、関数定義中の引数とし関数ポインタが宣言された場合
		##void sumefunc(int (*argfunc)(int,int,int));
		nxt1 = yield from me.next(1)

		if me.cur.type != '(':	
			raise FatalError()
			
		if nxt1.type != '*':
			raise NotTypeDescriptor(nxt1)
			
		yield from me.seek(1)
		
		stars = []
		while me.cur.type == '*':
			yield from me.seek()
			if me.cur.value == 'const':
				yield from me.seek()
				stars += ['const*']
			else:
				stars += ['*']

		if me.cur.type == 'ID':
			id = me.cur
			yield from me.seek()
		else:
			id = None
			
		if me.cur.type == '[':
			size_and_tokens = yield from me.parse_arraysizes(scope)
		else:
			size_and_tokens = []
			
		if me.cur.type != ')':
			raise NotTypeDescriptor(me.cur)
		
		yield from me.seek()
		if me.cur.type != '(':
			raise NotTypeDescriptor()
			
		yield from me.seek()
		if me.cur.type == ')':
			restype = funcptr_type(restype, ())
			yield from me.seek()
		else:
			has_vararg = False
			args = []
			while 1:
				if me.cur.type == '...':
					has_vararg = True
					if args == []:
						#msg = '...の前に可変長でない引数が必要です'
						#warnings.warn(SyntaxError(me.cur, msg))
						#args += [argdecl(TD_ERROR, '')]
						raise SyntaxError(me.cur, msg)
					
					yield from me.seek()
					if me.cur.type != ')':
						#warnings.warn(MissingToken(me.cur, ")"))
						#args += [argdecl(TD_ERROR, '')]
						raise MissingToken(me.cur, ")")
					else:
						has_vararg = True
						yield from me.seek()
						break
				
				typ, arg_id = yield from me.parse_argdef(scope)
				if arg_id is not None and arg_id.type != 'ID':
					raise FatalError()
				args += [argdecl(typ, arg_id or '')]
				
				
				if me.cur.type == ')':
					yield from me.seek()
					break
				if me.cur.type != ',':
					### ","の書き忘れとして継続
					### ここまで来たら継続しないほうがいいか? 動かしてから考える
					#warnings.warn(MissingToken(me.cur, ","))
					#args += [argdecl(TD_ERROR, '')]
					#me._index -= 1
					raise MissingToken(me.cur, ",")
				yield from me.seek()
			#restype = tid_funcptr(function_prototype(restype, args))
			restype = funcptr_type(restype, args, has_vararg)
			
		
		if stars[0] == 'const*':
			restype = const_type(restype)

		for p in stars[1:]:
			restype = pointer_type(restype)
			if p == 'const*':
				restype = const_type(restype)
			elif p != '*':
				raise FatalError()

		while size_and_tokens:
			size,tok = size_and_tokens.pop()
			if size is None:
				if size_and_tokens:
					#warnings.warn(SemanticError(tok, '配列型引数が不正です。'))
					#restype = sized_array_type(restype, 1)
					#continue
					raise SemanticError(tok, '配列型引数が不正です。')
					
				restype = unsizedarray_type(restype)
				break
			try:
				#size = size.ConstEvalInteger()
				if is_errorexp(size):
					return td_error(), None
				size = me.compiler.eval_constinteger(size)
				restype = sizedarray_type(restype, size)
			except NotConstInteger as err:
				## 関数引数定義での可変長配列変数の宣言
				## これはどうなるんだろう　あとで確認
				raise FatalError() from err

		return restype, id 


	def parse_arraysizes(me, scope):
		if me.cur.type != '[':
			raise FatalError()
			
		#sizes = []
		#tokens= []
		size_and_tokens = []
		while me.cur.type == '[':
			yield from me.seek()
			#tokens += [me.cur]
			tok = me.cur
			if me.cur.type == ']':
				#sizes += [None]
				size_and_tokens += [(None,tok)]
			else:
				sizeexp = yield from me.parse_expression(scope)
				#sizes += [sizeexp]
				size_and_tokens += [(sizeexp,tok)]
				if me.cur.type != ']':
					## ]の書き忘れとして継続
					warnings.warn(MissingToken(me.cur, "]"))
					me._index -= 1
			yield from me.seek()
		return size_and_tokens
	
	
	def parse_arrayarg(me, scope, restype, first_token):
		if me.cur.type != '[':
			raise FatalError()
		
		size_and_tokens = yield from me.parse_arraysizes(scope)
		#sizes = []
		#tokens= []
		#while me.cur.type == '[':
		#	yield from me.seek()
		#	tokens += [me.cur]
		#	if me.cur.type == ']':
		#		sizes += [None]
		#	else:
		#		sizeexp = yield from me.parse_expression(scope)
		#		sizes += [sizeexp]
		#		if me.cur.type != ']':
		#			## ]の書き忘れとして継続
		#			warnings.warn(MissingToken(me.cur, "]"))
		#			me._index -= 1
		#	yield from me.seek()
			
		while size_and_tokens:
			#size = sizes.pop()
			#tok = tokens.pop()
			size,tok = size_and_tokens.pop()
			if size is None:
				if size_and_tokens:
					## void func(int a[][]);とか void func(int a[a][]);
					## (void func(int a[][a]);は文法上許される)
					## size = 1と過程して継続
					warnings.warn(SemanticError(tok, '配列型引数が不正です。'))
					restype = sized_array_type(restype, 1)
					continue
					
				#restype = unsized_array_type(restype)
				restype = unsizedarray_type(restype)
				break
			try:
				#const = size.ConstEval()
				#if not isinstance(const, ConstInteger):
				#	raise
				#restype = sized_array_type(restype, const.value)
				#size = size.ConstEvalInteger()
				#restype = sizedarray_type(restype, size)

				size = me.compiler.eval_constinteger(size)
				restype = sizedarray_type(restype, size)
			except NotConstInteger as nci:
				## 関数引数定義での可変長配列変数の宣言
				## これはどうなるんだろう　あとで確認
				raise
				#restype = varsized_array_type(restype, size)
		return restype
		
	
	## situation: 'global' or 'function' or 'arg' or 'struct'
	def parse_argdef(me, scope):
		first_token = me.cur
		
		if me.cur.type == '...':
			raise FatalError()
			#yield from me.seek()
			#return me.cur, None
		
		tok = me.cur
		restype, options = yield from me.parse_typespec(scope, False)
		
		if options:
			## 引数定義にstaticとかのストレージ指定子がついてる。無視して継続
			#warnings.warn(SemanticError(tok, '引数定義に対する%s指定は不正です。'%list(options)[0]))
			raise SemanticError(tok, '引数定義に対する%s指定は不正です。'%list(options)[0])

		while me.cur.type == '*':
			restype = pointer_type(restype)
			yield from me.seek()
			if me.cur.value == 'const':
				restype = const_type(restype)
				yield from me.seek()
			
		nxt = yield from me.next(1)
		
		if me.cur.type == '(':
			#return (yield from me.parse_funcptrarg(scope, restype, first_token))
			return (yield from me.parse_funcptrtype(scope, restype))
		elif me.cur.type == 'ID' and nxt.type == '[':
			id = me.cur
			yield from me.seek()
			return (yield from me.parse_arrayarg(scope, restype, first_token)), id
		elif me.cur.type == 'ID':
			id = me.cur
			yield from me.seek()
			return restype, id
		elif me.cur.type == '[':
			id = None
			return (yield from me.parse_arrayarg(scope, restype, first_token)), id
		else:
			return restype, None
			
	def parse_prototype(me, scope, restype, first_token):
		options = {}
		
		if me.cur.type != 'ID':
			raise FatalError()
			
		funcname = me.cur
		yield from me.seek()
		
		if me.cur.type != '(':
			raise FatalError()
			
		yield from me.seek()
		
		if me.cur.type == ')':
			yield from me.seek()
			proto = prototype(restype)
			
		else:
			try:
				has_vararg = False
				## 関数プロトタイプ
				args = []
				while 1:
					if me.cur.type == '...':
						if args == []:
							msg = '...の前に可変長でない引数が必要です'
							#warnings.warn(SyntaxError(me.cur, msg))
							#args += [argdecl(TD_ERROR, '')]
							raise SyntaxError(me.cur, msg)
						
						yield from me.seek()
						if me.cur.type != ')':
							#warnings.warn(MissingToken(me.cur, ")"))
							#args += [argdecl(TD_ERROR, '')]
							raise MissingToken(me.cur, ")")
						else:
							has_vararg = True
							yield from me.seek()
							break
							
					typ, arg_id = yield from me.parse_argdef(scope)
					if arg_id is not None and arg_id.type != 'ID':
						raise FatalError()
					args += [argdecl(typ, arg_id.value if arg_id else '')]
					
					if me.cur.type == ')':
						yield from me.seek()
						break
						
					if me.cur.type == ';{}':
						raise ParseUnexpectedToken(me.cur)
						
						
					if me.cur.type != ',':
						## )の書き忘れとして継続
						#warnings.warn(MissingToken(me.cur, ")"))
						#break
						raise MissingToken(me.cur, ")")
						#me._index -= 1
					yield from me.seek()
				#print('funcdef', funcname)
				
			except OldStyleFunction:
				## 旧スタイルの関数定義 int foo(a,b) int a,int b;
				raise
			proto = prototype(restype, args, has_vararg)
		return proto
		
	def parse_funcdef(me, scope, proto, id, first_token, strage, options):
		if me.cur.type != '{':
			raise FatalError()
		
		if proto.args is None:
			proto.args = []
		## 関数定義
		funcscope = me.compiler.definefunc(scope, proto, id.value, strage, options, first_token)
		
		with warnings.catch_warnings(record=True) as rec:
		#	warnings.filterwarnings('always', category=Warning)
		#if 1:
			#warnings.filterwarnings('error')
			warnings.filterwarnings('always')
			#warnings.filterwarnings('error', category=NoueError)
			yield from me.parse_funcbody(funcscope)
			
		for w in rec:
			if isinstance(w.message, NoueError):
				funcscope.haserror = True
				funcscope.errors += [w]
			elif isinstance(w.message, NoueWarning):
				funcscope.errors += [w]
			#print('from funcdef', w)
			warnings.warn_explicit(w.message, w.category, w.filename, w.lineno)#, r.module, r.registry)
		
		return funcscope
		

		
				
				
	def parse_funcbody(me, scope):
		if me.cur.type != '{': raise FatalError()
		with warnings.catch_warnings(record=True) as rec:
			warnings.filterwarnings('always')
			yield from me.seek()
			while me.cur.type != '}':
				yield from me.parse_funcstmt(scope)
			yield from me.seek()
		for w in rec:
			#print('yes')
			#import pdb;pdb.set_trace()
			#print(w.message.message())
			#print('from funcbody', w)
			#import pdb;pdb.set_trace()
			warnings.warn_explicit(w.message, w.category, w.filename, w.lineno)#, r.module, r.registry)
			
	def parse_initlist(me, scope):
		
		if me.cur.type != '{': raise FatalError()
		
		yield from me.seek()
		res = []
		while 1:
			if me.cur.type == '{':
				initlist = yield from me.parse_initlist(scope)
				res += [initlist]
			else:
				init = yield from me.parse_expression(scope)
				res += [init]
			if me.cur.type == '}':
				yield from me.seek()
				return res
			if me.cur.type == ',':
				yield from me.seek()
			else:				
				## ,の書き忘れとして継続
				warnings.warn(MissingToken(me.cur, ","))
		return res
	
	def parse_arraydimension(me, scope, restype):
		nxt = yield from me.next(1)
		if me.cur.type != 'ID' or nxt.type != '[':
			raise FatalError()
		id = me.cur
		yield from me.seek()
		
		size_and_tokens = yield from me.parse_arraysizes(scope)
		#sizes = []
		#parents = []
		#while me.cur.type == '[':
		#	parents += [me.cur]
		#	yield from me.seek()
		#	if me.cur.type == ']':
		#		sizes += [None]
		#	else:
		#		sizeexp = yield from me.parse_expression(scope)
		#		sizes += [sizeexp]
		#		if me.cur.type != ']':
		#			## ]の書き忘れとして継続
		#			warnings.warn(MissingToken(me.cur, ","))
		#			me._index -= 1
		#	yield from me.seek()
		
		while size_and_tokens:
			size,_ = size_and_tokens.pop()
			if size is None:
				restype = unsizedarray_type(restype)
				continue
			try:
				
				if is_unsizedarray(restype):
					restype = me.error_type()
					warnings.warn(InvalidArrayType(id, restype))
					break
				if is_errorexp(size):
					return td_error(), None
				size = me.compiler.eval_constinteger(size)
				restype = sizedarray_type(restype, size)
			except NotConstInteger as nci:
				raise ## 未対応。可変長配列
		return restype
		
	
		

			
			
	

	
	## situation: 'global' or 'function' or 'arg' or 'struct'
	def parse_vardecl(me, scope):
		first_token = me.cur
		
		last_stmt_cnt = len(scope.statements)
		
		tid, strage = yield from me.parse_typespec(scope)
		yield from me.parse_vardecl_body(scope, tid, strage, set(), first_token)
		
		if last_stmt_cnt == len(scope.statements):
			warnings.warn(NoaffectStatement(me.cur))
						
		
	def parse_vardecl_body(me, scope, restype_root, strage, options, first_token, type=''):
		if not isinstance(strage, str):
			raise FatalError()
		while 1:
			restype = restype_root
			while me.cur.type == '*':
				restype = pointer_type(restype)
				yield from me.seek()
				if me.cur.value == 'const':
					restype = const_type(restype)
					yield from me.seek()
			
			#if me.cur.value == 'c':
			#	import pdb;pdb.set_trace()
			nxt = yield from me.next(1)
			if me.cur.type == 'ID' and nxt.type == '(':
				id = me.cur
				try:
					proto = (yield from me.parse_prototype(scope, restype, first_token))
				except NoueError as err:
					warnings.warn(err)
					proto = error_func()
					
					## error復帰処理
					while me.cur.type not in ';{':
						yield from me.seek()
				
				options = set()
				
				
				if me.cur.type == '{':
					funcscope = yield from me.parse_funcdef(scope, proto, id, first_token, strage, options)
					if is_errorfunc(proto):
						funcscope.haserror = True
					return
				else:
					stmt = me.compiler.declfunc(scope, proto, id.value, strage, options, first_token, me.cur)
					stmt.strage  = strage
					stmt.options = options
			else:
				if me.cur.type == '(':
					try:
						restype, id = yield from me.parse_funcptrtype(scope, restype)
					except NoueError as err:
						warnings.warn(err)
						## error復帰処理
						while me.cur.type not in ';':
							yield from me.seek()
						return
					#restype, id = yield from me.parse_funcptrtype(scope, restype)
				elif me.cur.type == 'ID' and nxt.type == '[':
					id = me.cur
					restype = yield from me.parse_arraydimension(scope, restype)
				elif me.cur.type == 'ID':
					id = me.cur
					yield from me.seek()
				elif me.cur.type == ';':
					yield from me.seek()
					return
				else:
					warnings.warn(ParseUnexpectedToken(me.prev(1)))
					id = me.cur
				
				if me.cur.type == '=':
					if strage in ('extern', 'typedef'):
						## extern,typedefに対して初期化値が定義されている。継続
						warnings.warn(SemanticError(me.cur, '%sに対する初期化は不正です。'%strage))
					yield from me.seek()
					if me.cur.type == '{':
						init = yield from me.parse_initlist(scope)
					else:
						init = yield from me.parse_expression(scope)
				else:
					init = None
				
				if strage == 'typedef':
					stmt = me.compiler.typedef(scope, restype, id.value, first_token, me.cur)
				else:
					stmt = me.compiler.declarevar(scope, restype, id.value, init, strage, options, first_token, me.cur)



			if me.cur.type == ';':
				yield from me.seek()
				return
			elif me.cur.type == ',':
				yield from me.seek()
				continue
			else:
				#print(me.cur)
				#raise
				## ";"の書き忘れとして、変数定義を終了する
				warnings.warn(MissingToken(me.prev(1), ";"))
				return
				
			
	
				
	def parse_struct_body(me, scope):
		first_token = me.cur
		
		last_stmt_cnt = len(scope.statements)
		last = (me.cur)
		tid, strage = yield from me.parse_typespec(scope, False)

		if strage:
			warnings.warn(SemanticError(me.cur, '構造体メンバに対する"%s"は不正です。'%' '.join(strage)))
			strage = None
			
		while 1:
			restype = tid
			while me.cur.type == '*':
				restype = pointer_type(restype)
				yield from me.seek()
				if me.cur.value == 'const':
					restype = const_type(restype)
					yield from me.seek()
			
			nxt = yield from me.next(1)
			if me.cur.type == 'ID' and nxt.type == '(':
				## メンバ関数定義
				warnings.warn(ParseUnexpectedToken(nxt))
				yield from me.seek()
				yield from me.seek()
				return
				
				
			bitsize = 0
			
			if me.cur.type == '(':
				restype, id = yield from me.parse_funcptrtype(scope, restype)
			elif me.cur.type == 'ID' and nxt.type == '[':
				id = me.cur
				restype = yield from me.parse_arraydimension(scope, restype)
			elif me.cur.type == 'ID':
				id = me.cur
				yield from me.seek()
				if me.cur.type == ':':
					yield from me.seek()
					bitsizeexp = yield from me.parse_expression(scope)
					try:
						bitsize = me.compiler.eval_constinteger(bitsizeexp)
						if bitsize == 0:
							msg = '構造体ビットフィールドサイズ0は不正です'
							warnings.warn(SyntaxError(me.cur, msg))
					except NotConstInteger as nci:
						warnings.warn(nci)
						bitsize = 0
			elif me.cur.type == ':':
				id = ID('', me.cur.file, me.cur.line, me.cur.col, me.cur.line_string)
				yield from me.seek()
				bitsizeexp = yield from me.parse_expression(scope)
				try:
					bitsize = me.compiler.eval_constinteger(bitsizeexp)
					if bitsize == 0:
						msg = '構造体ビットフィールドサイズ0は不正です'
						warnings.warn(SyntaxError(me.cur, msg))
				except NotConstInteger as nci:
					warnings.warn(nci)
					bitsize = 0
			elif me.cur.type == ';':
				if last_stmt_cnt == len(scope.statements):
					warnings.warn(NoaffectStatement(me.cur))
				yield from me.seek()
				return
			else:
				warnings.warn(ParseUnexpectedToken(me.cur))
				id = me.cur
				if me.cur.type not in (';', ','):
					yield from me.seek()
					
			me.compiler.definemember(scope, restype, id.value, bitsize, first_token, me.cur)
			if me.cur.type == ';':
				yield from me.seek()
				return
			elif me.cur.type == ',':
				yield from me.seek()
				continue
			else:
				warnings.warn(MissingToken(me.prev(1), ";"))
				return
				
	def parse_func_simplestmt(me, scope):
		first_token = me.cur
		if me.cur.type == ';':
			yield from me.seek()
		elif me.cur.value == 'return':
			yield from me.seek()
			#if me.cur.type != ';':
			if me.cur.type != ';':
				res = yield from me.parse_expression(scope)
			else:
				res = None
			if me.cur.type != ';':
				warnings.warn(MissingToken(me.prev(1), ";"))
				me._index -= 1
			stmt = me.compiler.returnstmt(scope, res, first_token, me.cur)
			#stmt = ReturnStmt(res, first_token, me.cur)
			#scope.AddStmt(stmt)
			yield from me.seek()
			
		elif me.cur.value == 'goto':
			yield from me.seek()
			if me.cur.type != 'ID':
				warnings.warn(ParseError(msg))
				me._index -= 1
				label = ''
			label = me.cur.value
			yield from me.seek()
			if me.cur.type != ';':
				warnings.warn(MissingToken(me.cur, ";"))
				me._index -= 1
			
			#stmt = GotoStmt(label, first_token, me.cur)
			#scope.AddStmt(stmt)
			stmt = me.compiler.gotostmt(scope, label, first_token, me.cur)
			yield from me.seek()
			
		elif me.cur.value == 'break':
			yield from me.seek()
			if me.cur.type != ';':
				warnings.warn(MissingToken(me.cur, ";"))
				me._index -= 1
			
			stmt = me.compiler.breakstmt(scope, first_token, me.cur)
			#stmt = BreakStmt(first_token, me.cur)
			#scope.AddStmt(stmt)
			yield from me.seek()
			
		elif me.cur.value == 'continue':
			yield from me.seek()
			if me.cur.type != ';':
				warnings.warn(MissingToken(me.cur, ";"))
				me._index -= 1
				
			stmt = me.compiler.continuestmt(scope, first_token, me.cur)
			#stmt = BreakStmt(first_token, me.cur)
			#scope.AddStmt(stmt)
			yield from me.seek()
			
		elif me.cur.value == 'case':
			yield from me.seek()
			res = yield from me.parse_expression(scope)
			if me.cur.type != ':':
				warnings.warn(MissingToken(me.cur, ":"))
				me._index -= 1
				
			#stmt = CaseStmt(res, first_token, me.cur)
			#scope.AddStmt(stmt)
			stmt = me.compiler.casestmt(scope, res, first_token, me.cur)
			yield from me.seek()

		elif me.cur.value == 'default':
			yield from me.seek()
			if me.cur.type != ':':
				warnings.warn(MissingToken(me.cur, ":"))
				me._index -= 1
			#stmt = DefaultStmt(first_token, me.cur)
			#scope.AddStmt(stmt)
			stmt = me.compiler.defaultstmt(scope, first_token, me.cur)
			yield from me.seek()
		else:
			#yield from me.load(1)
			nxt = yield from me.next(1)
			if me.cur.type == 'ID' and nxt.type == ':':
				label = me.cur.value
				#stmt = LabelStmt(label, first_token, me.cur)
				#scope.AddStmt(stmt)
				stmt = me.compiler.labelstmt(scope, me.cur, nxt)
				yield from me.seek(2)
			else:
				try:
					index = me._index
					yield from me.parse_vardecl(scope)
					return
				except NotTypeDescriptor:
					pass
				me._index = index
				#res = yield from me.parse_expression(scope)
				res = yield from me.parse_comma(scope)
				if me.cur.type != ';':
					warnings.warn(MissingToken(me.cur, ";"))
					me._index -= 1
					
				stmt = me.compiler.exprstmt(scope, res, me.cur)
				
				#stmt = ExprStmt(res, first_token, me.cur)
				#scope.AddStmt(stmt)
				yield from me.seek()

	def parse_for(me, scope):
		first_token = me.cur
		
		if me.cur.value != 'for':
			raise FatalError()
		yield from me.seek()
		
		if me.cur.type != '(':
			warnings.warn(MissingToken(me.cur, "("))
			me._index -= 1
		yield from me.seek()
		

		forscope = me.compiler.forscope(scope, first_token, me.cur)
		#forscope = For(first_token, me.cur)
		#scope.AddStmt(forscope)

		if me.cur.type != ';':
			try:
				index = me._index
				yield from me.parse_vardecl(forscope)
				#if me.cur.type != ';':
				#	warnings.warn(MissingToken(me.cur, ";"))
				#	me._index -= 1
				#yield from me.seek()
			except NotTypeDescriptor:
				me._index = index
				res = yield from me.parse_comma(forscope)
				#init = ExprStmt(res, first_token, me.cur)
				#forscope.AddStmt(init)
				stmt = me.compiler.exprstmt(forscope, res, me.cur)
				
				if me.cur.type != ';':
					warnings.warn(MissingToken(me.cur, ";"))
					me._index -= 1
					
				yield from me.seek()
		else:
			yield from me.seek()
		

		if me.cur.type != ';':
			res = yield from me.parse_expression(forscope)
			if me.cur.type != ';':
				warnings.warn(MissingToken(me.cur, ";"))
				me._index -= 1
				
			forscope.test = res
		else:
			forscope.test = None
		
		yield from me.seek()
		

		if me.cur.type != ')':
			res = yield from me.parse_comma(forscope)
			if me.cur.type != ')':
				warnings.warn(MissingToken(me.cur, ")"))
				me._index -= 1
				
			forscope.incl = res
		else:
			forscope.incl = None
		
		yield from me.seek()
		
		while me.cur.type == ')':
			## )を書きすぎた場合(よくある)
			msg = '")"に対応する"("が見つかりません。'
			warnings.warn(ParseError(me.cur, msg))
			yield from me.seek()

		#block = Block(forscope, me.cur, me.cur)
		if me.cur.type == '{':
			yield from me.parse_funcbody(forscope.body)
		else:
			yield from me.parse_funcstmt(forscope.body)
	
	def parse_if(me, scope):
		first_token = me.cur
		
		if me.cur.value != 'if':
			raise FatalError()
		yield from me.seek()
		
		if me.cur.type != '(':
			warnings.warn(MissingToken(me.cur, "("))
			me._index -= 1
		yield from me.seek()
		
		#ifscope = If(first_token, me.cur)
		#scope.AddStmt(ifscope)
		ifscope = me.compiler.ifscope(scope, first_token, me.cur)
		
		res = yield from me.parse_expression(ifscope)

		if me.cur.type != ')':
			warnings.warn(MissingToken(me.cur, ")"))
			me._index -= 1
			
		ifscope.test = res
		
		yield from me.seek()
		
		while me.cur.type == ')':
			## )を書きすぎた場合(よくある)
			msg = '")"に対応する"("が見つかりません。'
			warnings.warn(ParseError(me.cur, msg))
			yield from me.seek()

		#block = Block(ifscope, me.cur, me.cur)
		if me.cur.type == '{':
			yield from me.parse_funcbody(ifscope.body)
		else:
			yield from me.parse_funcstmt(ifscope.body)
		
		if me.cur.value != 'else':
			return
		
		yield from me.seek()
		if me.cur.type == '{':
			yield from me.parse_funcbody(ifscope.orelse)
		else:
			yield from me.parse_funcstmt(ifscope.orelse)
		
			
			
	def parse_while(me, scope):
		first_token = me.cur
		
		if me.cur.value != 'while':
			raise CFatalError()
		yield from me.seek()
		
		if me.cur.type != '(':
			warnings.warn(MissingToken(me.cur, "("))
			me._index -= 1
		yield from me.seek()
		
		new_scope = me.compiler.whilescope(scope, first_token, me.cur)
		#scope.AddStmt(new_scope)
		
		res = yield from me.parse_expression(new_scope)
		if me.cur.type != ')':
			warnings.warn(MissingToken(me.cur, ")"))
			me._index -= 1
			
		new_scope.test = res
		
		yield from me.seek()
		
		while me.cur.type == ')':
			## )を書きすぎた場合(よくある)
			msg = '")"に対応する"("が見つかりません。'
			warnings.warn(ParseError(me.cur, msg))
			yield from me.seek()
				
		if me.cur.type == '{':
			yield from me.parse_funcbody(new_scope.body)
		else:
			yield from me.parse_funcstmt(new_scope.body)

	def parse_dowhile(me, scope):
		first_token = me.cur
		
		if me.cur.value != 'do':
			raise FatalError()
		yield from me.seek()
		
		#new_scope = DoWhile(first_token, me.cur)
		#scope.AddStmt(new_scope)
		new_scope = me.compiler.dowhilescope(scope, first_token, me.cur)
		
		if me.cur.type == '{':
			yield from me.parse_funcbody(new_scope.body)
		else:
			warnings.warn(MissingToken(me.cur, "{"))
			return;

		if me.cur.value != 'while':
			warnings.warn(MissingToken(me.cur, "while"))
			me._index -= 1
		yield from me.seek()
		
		if me.cur.type != '(':
			warnings.warn(MissingToken(me.cur, "("))
			me._index -= 1
		yield from me.seek()
		
		res = yield from me.parse_expression(new_scope)
		if me.cur.type != ')':
			warnings.warn(MissingToken(me.cur, ")"))
			me._index -= 1
		yield from me.seek()
		
		while me.cur.type == ')':
			## )を書きすぎた場合(よくある)
			msg = '")"に対応する"("が見つかりません。'
			warnings.warn(ParseError(me.cur, msg))
			yield from me.seek()
		
		new_scope.test = res
		
		if me.cur.type != ';':
			warnings.warn(MissingToken(me.cur, ";"))
			me._index -= 1
		yield from me.seek()
		
				
			
			
			
	def parse_switch(me, scope):
		first_token = me.cur
		
		if me.cur.value != 'switch':
			raise FatalError()
			
		yield from me.seek()
		
		if me.cur.type != '(':
			warnings.warn(MissingToken(me.cur, "("))
			me._index -= 1
		yield from me.seek()
		
		#new_scope = Switch(first_token, me.cur)
		#scope.AddStmt(new_scope)
		new_scope = me.compiler.switchscope(scope, first_token, me.cur)
		
		res = yield from me.parse_expression(new_scope)
		if me.cur.type != ')':
			warnings.warn(MissingToken(me.cur, ")"))
			me._index -= 1
			
		new_scope.test = res
		
		yield from me.seek()
		

		while me.cur.type == ')':
			## )を書きすぎた場合(よくある)
			msg = '")"に対応する"("が見つかりません。'
			warnings.warn(ParseError(me.cur, msg))
			yield from me.seek()
				
		if me.cur.type == '{':
			yield from me.parse_funcbody(new_scope.body)
		else:
			warnings.warn(MissingToken(me.cur, "{"))
			return
			
			
				
			
	def parse_funcstmt(me, scope):
		with warnings.catch_warnings(record=True) as rec:
			warnings.filterwarnings('always')
			first_token = me.cur
			if me.cur.value == 'for':
				yield from me.parse_for(scope)
			elif me.cur.value == 'if':
				yield from me.parse_if(scope)
			elif me.cur.value == 'while':
				yield from me.parse_while(scope)
			elif me.cur.value == 'do':
				yield from me.parse_dowhile(scope)
			elif me.cur.value == 'switch':
				yield from me.parse_switch(scope)
			elif me.cur.value == '{':
				newscope = me.compiler.block(scope, me.cur)
				yield from me.parse_funcbody(newscope)
			else:
				yield from me.parse_func_simplestmt(scope)
		
		for w in rec:
			#print('from funcstmt', w)
			if isinstance(w.message, me.InsertComment):
				me.compiler.comment(scope, w.message.token)
			else:
				#import pdb;pdb.set_trace()
				warnings.warn_explicit(w.message, w.category, w.filename, w.lineno)#, r.module, r.registry)
				
				
	def parse_global(me, name=''):
		me.module = me.compiler.modulefile(name)
		yield from me.load()
		while 1:
			with warnings.catch_warnings(record=True) as rec:
				warnings.filterwarnings('always')
			#if 1:
				try:
					if me.cur.type == 'END':
						break 
					
					## 不正なトークン
					if me.cur.type != 'ID':
						warnings.warn(ParseUnexpectedToken(me.cur))
						yield from me.seek()
						continue
						
					
					yield from me.parse_vardecl(me.module)
				except NotTypeDescriptor as nt:
					warnings.warn(nt)
					#yield from me.parse_vardecl_tail(scope, me.compiler.errortype(), me.cur, '')
					yield from me.parse_vardecl_body(me.module, me.compiler.errortype(), '', set(), me.cur)
					if me.cur.type != ';':
						warnings.warn(ParseUnexpectedToken(me.cur))
					yield from me.seek()
				except NoueError as err:
					print(err, err.pos)
					raise
				for w in rec:					
					if isinstance(w.message, me.InsertComment):
						me.compiler.comment(me.module, w.message.token)
			for w in rec:					
				if isinstance(w.message, NoueError):
					me.module.haserror = True
					me.module.errors += [w]
				elif isinstance(w.message, NoueWarning):
					me.module.errors += [w]
				warnings.warn_explicit(w.message, w.category, w.filename, w.lineno)#, r.module, r.registry)
				#print('from global', w)
		return me.module

if __name__ == '__main__':
	import inspect
	lno = inspect.currentframe().f_lineno+2
	src = """
		struct error_t{
			int n
			int j;
		};
		int axxx;
		char ax[sizeof(struct error_t)];
		
		int strcmp(const char*, const char*);
		void printf(const char*, ...);
		struct test_t* p;
		size_t N = 0x00AABB;
		int G[2][2];
		int (*P)(int,char);
		
		struct test_t{
			int n;
			struct test2_t{
				double d;
			};
		};
		
		struct test_t t;
		struct test2_t t2;
		
		int g = 99;
		int g_n = 0;
		double d = 0.0, f = 0.0;
		double a[9][4][5];
		char c[] = "test";
		int k=0;
		int func(int n)
		{
			int AA[3];
			AA[0] = 1;
			P = (int(*)(int,char))0;
			N = sizeof(struct test_t);
			t.n = n;
			int x = 0;
			for(int i=0; i*3/3<n; ++i){
				x += i;
			}
			int j;
			
			for(x=0,j=0; ;){
				x += 1;
			}
			
			if(!strcmp("", "")){
				printf("test");
			}else{
				printf("test2%d %d", 0, 1);
			}
			// test
			
			//printf a;
			int *ar[8], nn;
			nn = 9;
			{nn = 8;}
			
			return 9;
		}
		typedef enum {A,B,C} E;
		E e;
		
		typedef struct{
			union{
				int a;
				char b;
			}u;
		}U;
		U u;
		
		int (*PTEST[8])(int);
		int TESTET()
		{
			const char*p;
			p = "test1" "test3";
			int n;
			n = (*PTEST[0])(1);
			TESTTET();
		}
		
		typedef struct {int n;}PyObject;
		typedef struct _file FILE;
		typedef int (*printfunc)(PyObject *, FILE *, int);
		char s[1] = "test";
		int a;
		char x2;
		int* (*const PX)(const void*, size_t);
		
		typedef struct{
			int n:2;
			unsigned int :8;
			unsigned :8;
			unsigned noname:8;
		}XXXX;
		XXXX xxxx;
		
		//error_t errorfunc(int n, error2_t c)
		//{
		//	return 0;
		//}
		//fa;
		
		
		int func1(int n)
		{
			char s[2] = "test";
			ffff
			/*@py:
				print('yse!')
				print('yes2!')
			*/
			return 0;
		}
		;
	"""
	lno = inspect.currentframe().f_lineno+1
	src = r"""
	int test(int n)
	{	
		int S2 = 99;
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
	tok = Tokenizer().tokenize(src, __file__, lno)
	
	class dummysize:
		def sizeof(me, *args):
			return 1
	parser = Parser(SyntaxCore(dummysize()))
	p = parser.parse_global()
	next(p)
	cnt = 0
	#with warnings.catch_warnings() as rec:
	with warnings.catch_warnings(record = True) as rec:
	#if 1:
		warnings.filterwarnings('always', category=NoueException)
		warnings.filterwarnings('error', category=NoueError)
		
		#warnings.filterwarnings('ignore', category=NoaffectStatement)
		try:
			for t in tok:
				if t and t[0].type == 'MC':
					#p.throw(parser.InsertComment(t[0]))
					continue
				#with warnings.catch_warnings():
					#warnings.filterwarnings('ignore')
				p.send(t)
			p.send([END()])
		except StopIteration as stop:
			module = stop.args[0]
			
	print('yes')
	#print(rec)
	#for w in rec:
	#	print(w.message.message())
	for e in parser.module.errors:
		print(e.message.message())
		
	for s in parser.module.statements:
		print(s.prototype.restype)
	#for f in parser.module.statements:
	#	if hasattr(f, 'errors'):
	#		for e in f.errors:
	#			print(e.message.message())
		
	#print(parser.module.statements[-1].statements[0].restype)
		