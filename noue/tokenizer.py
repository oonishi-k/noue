#coding: utf8
import warnings

try:
	from .error import *
except SystemError:
	import imp
	noue = imp.load_source('noue', './__init__.py')
	from noue.error import *
import copy
def copy_tokens(tokens, src, define=None):
	tokens = copy.deepcopy(tokens)
	for t in tokens:
		t.file = src.file
		t.col  = src.col
		t.line = src.line
		t.line_string = src.line_string
		
		t.define = define
		if hasattr(src, 'define'):
			t.define.define = src.define
	return tokens

	

		
class CodeFragment(CodePositional):
	def __init__(me, type, file, line, col, line_string):
		CodePositional.__init__(me, file, line, col, line_string)
		me.type = type
		
	def __repr__(me):
		return '"%s"(%d,%d)'%(me.value,me.line,me.col)
		
	def ToString(me):
		raise
	
		
## 変数名など
class ID(CodeFragment):
	def __init__(me, value, file, line, col, line_string):
		CodeFragment.__init__(me, 'ID', file, line, col, line_string)
		me.value = value

## ファイル終端
class END(CodeFragment):
	def __init__(me):
		CodeFragment.__init__(me, 'END', '', -1, -1, '$FileEnd')

		

## 変数名など		
class Keyword(CodeFragment):
	def __init__(me, value, file, line, col, line_string):
		CodeFragment.__init__(me, value, file, line, col, line_string)
		me.value = value

class TokenInteger(CodeFragment):
	def __init__(me, s, suffix, file, line, col, line_string):
		CodeFragment.__init__(me, 'CI', file, line, col, line_string)
		
		me.suffix = suffix
		me.value  = eval((s.lstrip('0') if s[:2] != '0x' else s) or '0')
		me.s      = s
		
		
class TokenReal(CodeFragment):
	def __init__(me, s, suffix, file, line, col, line_string):
		CodeFragment.__init__(me, 'CR', file, line, col, line_string)

		me.suffix = suffix
		me.value  = eval(s)
		me.s      = s
		

		
class TokenDoubleQuote(CodeFragment):
	def __init__(me, value, prefix, file, line, col, line_string, encoding):
		CodeFragment.__init__(me, 'CS', file, line, col, line_string)
		me.value = eval(value)
		me.prefix = prefix
		me.encoding = encoding

	def __repr__(me):
		return '%s(%d,%d)'%(repr(me.value),me.line,me.col)
		

class TokenSingleQuote(CodeFragment):
	def __init__(me, value, prefix, file, line, col, line_string, encoding):
		CodeFragment.__init__(me, 'CC', file, line, col, line_string)
		me.value = eval(value)
		me.prefix = prefix # L, U
		me.encoding = encoding

		
class TokenComment(CodeFragment):
	def __init__(me, value, file, line, col, line_string):
		CodeFragment.__init__(me, 'MC', file, line, col, line_string)
		me.value = value
		
def skip_space(src):
	for i,c in enumerate(src):
		if c not in ' \t　':
			return i
	return i+1

		
class Tokenizer:
	def __init__(me):
		me.encoding = ''
		return
	
	delimiter1 = set(tuple(r'=+-*/%()<>{}[]!@#$%^&~:;|.,?'))
	delimiter2 = {
		'++', '--'
		, '&&', '||', '>>', '<<'
		, '::', '->', '.*'
		, '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^='
		, '<=', '>=', '==', '!='
	}
	delimiter2 = {
		'++', '--'
		, '&&', '||', '>>', '<<'
		, '->', '.*'
		, '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^='
		, '<=', '>=', '==', '!=', '##'
	}
	delimiter3 = {
		'->*', '>>=', '<<='
		, '...' # 可変引数用
	}

	keyword = {
		'asm', 'auto', 'break', 
		'case', 'const', 'continue', 'default', 'do',
		'else', 'enum', 'explicit', 'extern', 'for','goto', 
		'if', 'inline', 'register',  'return', 
		'signed', 'sizeof', 'static', 'struct', 'switch', 
		'typedef', 'union', 'unsigned', 'while', 
		#'int', 'short', 'long', 'char', 'wchar_t', 'size_t', 'double', 'float', #'long long'
		#'NULL',
	}
	
	space = ' \t　\\\n\r'
	string_prefix = {'L'}
	
	
	def tokenize_dq(me, s, file, line, col, org_string, prefix=''):
		if s[0] != '"':
			raise FatalError()
		pos = s.replace(r'\\', '$$').replace(r'\"', '%%').find('"', 1)
		if pos == -1:
			msg = '"が閉じていません。'
			err = TokenizeError(file, line, col-len(prefix), org_string, msg)
			warnings.warn(err)
			return []
			
		i = pos+1
		return [TokenDoubleQuote(s[:i], prefix, file, line, col-len(prefix), org_string, me.encoding)] \
				+ me.line_tokenize(s[i:], file, line, col+i, org_string)
				
				
	def tokenize_sq(me, s, file, line, col, org_string, prefix=''):
		if s[0] != "'":
			raise FatalError()
		pos = s.replace(r'\\', '$$').replace(r"\'", '%%').find("'", 1)
		if pos == -1:
			msg = "'が閉じていません。"
			err = TokenizeError(file, line, col-len(prefix), org_string, msg)
			warnings.warn(err)
			return []
			
		i = pos+1
		return [TokenSingleQuote(s[:i], prefix, file, line, col-len(prefix), org_string, me.encoding)] \
				+ me.line_tokenize(s[i:], file, line, col+i, org_string)
			
	
	def tokenize_num(me, s, file, line, col, org_string):
		if s[:2] == '0x':
			for i,c in enumerate(s[2:], 2):
				if not c.isdigit() and not('A' <= c.upper() <= 'F'):
					break
			else:
				return [TokenInteger(s, '', file, line, col, org_string)]
			
			rest = me.line_tokenize(s[i:], file, line, col+i, org_string)
			
			if rest and rest[0].type == 'ID' and rest[0].col == col+i:
				# 数字の後に連続してIDがあれば、それは数値のサフィックス(LとかLLUとか)
				return [TokenInteger(s[:i], rest[0].value, file, line, col, org_string)] + rest[1:]
			else:
				return [TokenInteger(s[:i], '', file, line, col, org_string)] + rest
		else:
			for i,c in enumerate(s):
				if not c.isdigit():
					break
			else:
				return [TokenInteger(s, '', file, line, col, org_string)]
				
			is_real = False
			if s[i] == '.':
				is_real = True
				i += 1
				for i,c in enumerate(s[i:], i):
					if not c.isdigit():
						break
				else:
					return [TokenReal(s, '', file, line, col, org_string)]
			
			if s[i] == 'e':
				is_real = True
				if s[i:i+2] == 'e+' or s[i:i+2] == 'e-':
					i += 2
				else:
					i += 1
					
				for i,c in enumerate(s[i:], i):
					if not c.isdigit():
						break
				else:
					return [TokenReal(s, '', file, line, col, org_string)]
					
			rest = me.line_tokenize(s[i:], file, line, col+i, org_string)
			if rest and rest[0].type == 'ID' and rest[0].col == col+i:
				# 数字の後に連続してIDがあれば、それは数値のサフィックス(LとかLLUとか)
				if is_real:
					return [TokenReal(s[:i], rest[0].value, file, line, col, org_string)] + rest[1:]
				else:
					return [TokenInteger(s[:i], rest[0].value, file, line, col, org_string)] + rest[1:]
			else:
				if is_real:
					return [TokenReal(s[:i], '', file, line, col, org_string)] + rest
				else:
					return [TokenInteger(s[:i], '', file, line, col, org_string)] + rest
			
	def tokenize_id(me, s, file, line, col, org_string):
		for i,c in enumerate(s):
			if c in me.delimiter1 or c in ('"', "'") or c in me.space:
				break
		else:
			return [ID(s, file, line, col, org_string)]
			
		
		if s[i] == '"' and s[:i] in me.string_prefix:
			return me.tokenize_dq(s[i:], file, line, col+i, org_string, s[:i])
		elif s[i] == "'" and s[:i] in me.string_prefix:
			return me.tokenize_sq(s[i:], file, line, col+i, org_string, s[:i])
		else:
			return [ID(s[:i], file, line, col, org_string)] \
					+ me.line_tokenize(s[i:], file, line, col+i, org_string)
		
			
	
	class CommentNotClosed(StopIteration): pass
	
	def line_tokenize(me, s, file, line, col, org_string):
		while s and s[0] in me.space:
			col += 1
			s = s[1:]
			
		if s == '': return []
		
		if s[:2] == '//':
			return [TokenComment(s[2:], file, line, col, org_string)]
			
		if s[:2] == '/*':
			if s[2:].find('*/') == -1:
				raise me.CommentNotClosed()
			
			last = s.find('*/', 2) + 2
			return [TokenComment(s[2:last-2], file, line, col, org_string)] \
						+ me.line_tokenize(s[last:], file, line, col+last, org_string)
		elif s[:3] in me.delimiter3:
			res = Keyword(s[:3], file, line, col, org_string)
			return [res] + me.line_tokenize(s[3:], file, line, col+3, org_string)
		elif s[:2] in me.delimiter2:
			res = Keyword(s[:2], file, line, col, org_string)
			return [res] + me.line_tokenize(s[2:], file, line, col+2, org_string)
		elif s[:1] in me.delimiter1:
			res = Keyword(s[:1], file, line, col, org_string)
			return [res] + me.line_tokenize(s[1:], file, line, col+1, org_string)
		elif s[0].isdigit():
			return me.tokenize_num(s, file, line, col, org_string)
		elif s[0] == '"':
			return me.tokenize_dq(s, file, line, col, org_string)
		elif s[0] == "'":
			return me.tokenize_sq(s, file, line, col, org_string)
		else:
			return me.tokenize_id(s, file, line, col, org_string)
			
	class ChangeLineno(Exception):
		def __init__(me, lno):
			me.lno = lno

	def tokenize(me, s, file, line, encoding=''):
		me.encoding = encoding
		lines = s.splitlines(False)
		it = enumerate(lines)
		
		for i,s in it:
			try:
				while s.rstrip() and s.rstrip()[-1] == '\\':
					_,s2 = next(it)
					s += '\n' + s2
			except StopIteration:
				msg = r'ソースが"\"で終わっています。'
				err = TokenizeError(file, line, col-len(prefix), org_string, msg)
				warnings.warn(err)

			try:
				while 1:
					try:
						res = me.line_tokenize(s, file, line+i, 0, s)
					except me.CommentNotClosed:
						s += '\n' + next(it)[1]
					else:
						break
				yield res
			except me.ChangeLineno as changelno:
				line = changelno.lno - i
				for r in res:
					r.line = line + i
				yield res
			
if __name__ == '__main__':
	import inspect
	tok = Tokenizer()
	lno = inspect.currentframe().f_lineno+1
	src = """
test
8 9999
"testai.pr"
a i j+8 
u_"4aa"
/*test*/
// tstacpihasrpc
/*a asrpchiasr
ars.hciih*/ ****
"'"
"""
	for t in tok.tokenize(src, __file__, lno):
		print(t)