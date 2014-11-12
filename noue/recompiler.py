#coding: utf8
import ast as pyast


class ReParser:
	def __toline(ast, me, depth):
		args = ', '.join([arg.arg for arg in ast.args.args])
		print(ast.lineno, '\t'*depth + 'def ' + ast.name + '(%s)'%args + ':')
		for s in ast.body:
			me.toline(s, depth+1)
		return
	pyast.FunctionDef.__toline = __toline
	
	def __toline(ast, me, depth):
		print(ast.lineno, '\t'*depth + me.tosource(ast.value))
	pyast.Expr.__toline = __toline
	
	def __toline(ast, me, depth):
		print(ast.lineno, '\t'*depth + 'if '+ me.tosource(ast.test) + ':')
		for s in ast.body:
			me.toline(s, depth+1)
			
		if ast.orelse:
			print(ast.orelse[0].lineno, '\t'*depth + 'else:')
			for s in ast.orelse:
				me.toline(s, depth+1)
			
		return
	pyast.If.__toline = __toline
	
	def __toline(ast, me, depth):
		print(ast.lineno, '\t'*depth + 'while '+ me.tosource(ast.test) + ':')
		for s in ast.body:
			me.toline(s, depth+1)
		return
		
	pyast.While.__toline = __toline
	
	def __toline(ast, me, depth):
		print(ast.lineno, '\t'*depth + 'return '+ (me.tosource(ast.value) if ast.value else ''))
		return
		
	pyast.Return.__toline = __toline
	
	def __toline(ast, me, depth):
		print(ast.lineno, '\t'*depth + 'raise '+ (me.tosource(ast.exc) if ast.exc else ''))
		return
		
	pyast.Raise.__toline = __toline

	
	def __toline(ast, me, depth):
		target = ' = '.join([me.tosource(t) for t in ast.targets])
		value  = me.tosource(ast.value)
		print(ast.lineno, '\t'*depth + target + ' = ' + value)
		return
		
	pyast.Assign.__toline = __toline
	
	def __toline(ast, me, depth):
		target = ','.join([me.tosource(t) for t in ast.targets])
		print(ast.lineno, '\t'*depth + 'del ' + target)
		return
		
	pyast.Delete.__toline = __toline

	
	def __tosource(exp, me):
		return me.tosource(exp.value) + '.' + exp.attr
	pyast.Attribute.__tosource = __tosource
	
	
	def __tosource(exp, me):
		return me.tosource(exp.value) + '[%s]'%me.tosource(exp.slice)
	pyast.Subscript.__tosource = __tosource
	
	def __tosource(exp, me):
		lower = me.tosource(exp.lower) if exp.lower else ''
		upper = me.tosource(exp.upper) if exp.upper else ''
		step  = me.tosource(exp.step)  if exp.step else ''
		return '%s:%s:%s'%(lower, upper, step)
	pyast.Slice.__tosource = __tosource
	
	def __tosource(exp, me):
		return me.tosource(exp.value)
	pyast.Index.__tosource = __tosource
	
	def __tosource(exp, me):
		s = ''.join([me.tosource(e)+',' for e in exp.elts])
		return '('+s+')'
	pyast.Tuple.__tosource = __tosource
	
	def __tosource(exp, me):
		s = ', '.join([me.tosource(e) for e in exp.elts])
		return '['+s+']'
	pyast.List.__tosource = __tosource
	
	def __tosource(exp, me):
		return me.tosource(exp.body) + ' if ' + me.tosource(exp.test) + ' else ' + me.tosource(exp.orelse)
	pyast.IfExp.__tosource = __tosource
	
	def __tosource(exp, me):
		arg = ', '.join([me.tosource(a) for a in exp.args] + (['*'+me.tosource(exp.starargs)] if exp.starargs else []))
		
		return me.tosource(exp.func) + '(%s)'%arg
	pyast.Call.__tosource = __tosource
	
	def __tosource(exp, me):
		return me.tosource(exp.left) + ' ' + exp.op.__s + ' ' + me.tosource(exp.right)
	pyast.BinOp.__tosource = __tosource
	
	pyast.Add.__s = '+'
	pyast.Sub.__s = '-'
	pyast.Mult.__s = '*'
	pyast.Mod.__s = '%'
	pyast.Div.__s = '/'
	pyast.FloorDiv.__s = '//'
	
	pyast.BitOr.__s = '|'
	pyast.BitXor.__s = '^'
	
	
	def __tosource(exp, me):
		#print(exp.operand, exp.op)
		return exp.op.__s + ' ' + me.tosource(exp.operand)
	pyast.UnaryOp.__tosource = __tosource
	pyast.USub.__s = '-'
	pyast.UAdd.__s = '+'
	
	def __tosource(exp, me):
		return exp.id
	pyast.Name.__tosource = __tosource
	
	def __tosource(exp, me):
		return repr(exp.s)
	pyast.Str.__tosource = __tosource
	
	def __tosource(exp, me):
		return repr(exp.s)
	pyast.Bytes.__tosource = __tosource
	
	def __tosource(exp, me):
		return str(exp.n)
	pyast.Num.__tosource = __tosource
		
		
	def __tosource(exp, me):
		s = (' ' + exp.op.__s + ' ').join([me.tosource(v) for v in exp.values])
		return s
	pyast.BoolOp.__tosource = __tosource
	pyast.And.__s = 'and'
	pyast.Or.__s  = 'or'
	
	def __tosource(exp, me):
		s = ''.join([' ' + o.__s + ' ' + me.tosource(c) for o,c in zip(exp.ops, exp.comparators)])
		return me.tosource(exp.left) + s
	pyast.Compare.__tosource = __tosource
	pyast.Lt.__s  = '<'
	pyast.LtE.__s = '<='
	pyast.Gt.__s  = '<'
	pyast.GtE.__s = '<='
	pyast.Eq.__s  = '=='
	pyast.NotEq.__s  = '!='
	
	def toline(me, ast, depth):
		ast.__toline(me, depth)
		
	def tosource(me, exp):
		return exp.__tosource(me)

if __name__ == '__main__':
	s = pyast.parse('a =  -0').body[0]
	ReParser().toline(s, 0)