#coding: utf8
import warnings
import os.path
import copy
from collections import defaultdict
from functools import reduce


try:
	from .error import *
	from .tokenizer import *
except SystemError:
	import imp
	noue = imp.load_source('noue', './__init__.py')
	from noue.error import *
	from noue.tokenizer import *
	
def search_unnested_token(targets, tokens):
	res = []
	parenth = []
	
	for i,tok in enumerate(tokens):
		if tok.value in targets and not parenth:
			return res, tokens[i:]
		elif tok.type == '(':
			parenth += [')']
		elif tok.type == '{':
			parenth += ['{']
		elif tok.type == '[':
			parenth += [']']
		elif tok.type in (')', ']', '}'):
			if parenth[-1] != tok.type:
				raise
			parenth.pop()
		res += [tok]
	#print(tokens)
	raise

class ComplexMacro:
	def __init__(me, id):
		me.name = id.value
		me.token = id
	
		me.argcount = 0
		me.has_va_args = False
		me.args = {}
		me.body = [[]]
		
		
	def Replace(me, tokens):
		## tokensは'('以降をすべて(行末まで)与えること
		if len(tokens) < 2:
			raise
		org = tokens[0]
		args = []
		
		if tokens[0].type != '(':
			raise FatalError()
		
		if tokens[1].type != ')':
			while tokens:
				#arg, tokens = (yield from search_unnested_token({',', ')'}, tokens[1:]))
				arg, tokens = search_unnested_token({',', ')'}, tokens[1:])
				args += [arg]
				if tokens[0].type == ')': break
			else:
				raise
		else:
			tokens = tokens[1:]
		
		if not me.has_va_args and len(args) != me.argcount:
			#print(me.has_va_args, args)
			raise
			
		if me.argcount > 0 and me.argcount > len(args):
			raise
			
		res = []
		for bod in me.body:
			if type(bod) == int and bod >= 0:
				res += args[bod]
			elif type(bod) == int and bod == -1:
				if not me.has_va_args: raise
				#res += sum(args[me.argcount:], [])
				res += reduce(lambda a,b: a + [Keyword(',', '', 0, 0, '')] + b, args[me.argcount:])
			else:
				#print(bod)
				res += bod
		#print(res)
		res = copy_tokens(res, org, me.token)
		return res + tokens[1:]
		

		
	def Parse(me, tokens):
		## tokensは'('以降をすべて(行末まで)与えること
		tokens = me.DefineSignature(tokens)

		for i,tok in enumerate(tokens):
			if tok.type == 'ID' and tok.value in me.args:
				me.body += [me.args[tok.value], []]
			elif tok.type == 'ID' and tok.value == '__VA_ARGS__':
				me.body += [-1, []]
			else:
				me.body[-1] += [tok]
	
	def DefineSignature(me, tokens):
		## tokensは'('以降をすべて(行末まで)与えること
		if len(tokens) < 2:
			raise
			
		if tokens[1].type == ')':
			return tokens[2:]
			
		tokens = tokens[1:]
		#while tokens[0].type != ')' and tokens[0].type != '...':
		while tokens:
			if tokens[0].type == '...': break
			id,comma = tokens[:2]
			tokens = tokens[2:]
			
			if id.type != 'ID':
				raise
			me.args[id.value] = me.argcount
			me.argcount += 1
			
			if comma.type == ')': break
			if comma.type != ',': raise
		
		if tokens and tokens[0].type == '...':
			me.has_va_args = True
			if tokens[1].type != ')':
				msg = '不正なマクロです。'
				err = PreprocessError(t[-1], msg)
				warnings.warn(err)
			
			tokens = tokens[2:]
			
		return tokens
		
			
class ModuleObject:
	def __init__(me):
		me._macro_simple  = {}
		me._macro_complex = {}
		me._macro_pos = {}
		me._macro_undef = {}
		
		
_macroLine = lambda t: [TokenInteger(str(t.line), '', t.file, t.line, t.col, t.line_string)]
_macroFile = lambda t: [TokenDoubleQuote(repr(t.file), '', t.file, t.line, t.col, t.line_string, '')]


	
class Preprocessor:
	default_include = os.path.abspath(os.path.join(os.path.dirname(__file__), 'include'))
	default_encoding= 'utf8'
	def __init__(me, tok, includes=[], ignore_default_include=False):
		me.tok = tok
		me._macro_simple  = {}
		me._macro_complex = {}
		me._macro_special = {}
		me._macro_special['__LINE__'] = _macroLine
		me._macro_special['__FILE__'] = _macroFile
		
		if ignore_default_include:
			me.includes = [me.default_include] + includes
		else:
			me.includes = [me.default_include] + includes
		me.dir_encodings = {me.default_include:'utf8'}
		me.default_encoding = me.default_encoding
		return
		
	def read_line(me, it):
		t = next(it)
		try:
			while t and t[-1].type == '\\':
				t = t[:-1] + next(it)
		except StopIteration:
			msg = '不正なマクロです。'
			err = PreprocessError(t[-1], msg)
			warnings.warn(err)
			raise
		return t
		
		
		
	def eval(me, module, tokens, first):
		if not tokens:
			me.error(first)
			return 0
		
		tokens = list(me.read(module, tokens, iter([])))
		if not tokens:
			return 0
		#print(tokens)
		tokens = sum(tokens, [])
		#print(''.join([str(t.value) for t in tokens]))
		i = iter(tokens)
		new = []
		for t in i:
			if t.type != 'ID':
				new += [str(t.value)]
			else:
				if t.value == 'defined':
					#new += ['1**']
					nxt = next(i)
					while nxt.type == '(':
						new += [nxt.value]
						nxt = next(i)
					if nxt.type != 'ID':
						new += [str(nxt.value)]
					elif me.has_macro(module, nxt):
						new += ['1']
					else:
						new += ['0']
				else:
					first = t
					new += [str(t.value)]
		s = ' '.join([str(t.value) if t.type != 'ID' or t.value == 'defined' else str(me.has_macro(module, t) or None)
							for t in tokens])
		s = ' '.join(new)
		s = s.replace('&&', 'and')
		s = s.replace('||', 'or')
		s = s.replace('defined', '1**')
		s = s.replace('!=', '$NE$')
		s = s.replace('!', 'not')
		s = s.replace('$NE$', '!=')
		s = s.replace('#', '$')
		#print(s)
		try:
			return eval(s, {})
		except NameError as e:
			me.error(first, '未定義のプリプロセッサシンボル%sです'%e.args[0].split()[1])
			return 0
		except:
			me.error(first)
			return 0
		
	def error(me, tok, msg='不正なマクロです。', category=PreprocessError):
		err = category(tok, msg)
		warnings.warn(err)
		return
		
	def has_macro(me, module, id):
		if id.value in module._macro_undef:
			return False
		if id.value in me._macro_simple:
			return True
		if id.value in me._macro_complex:
			return True
		if id.value in me._macro_special:
			return True
			
		if id.value in module._macro_simple:
			return True
		if id.value in module._macro_complex:
			return True
		return False
		
	def undef(me, module, tokens):
		if len(tokens) == 2 or tokens[2].type != 'ID':
			me.error(t[1])
			return
		
		id = tokens[2]

		if not me.has_macro(module, id):
			msg = 'マクロ"%s"は定義されていません'%id.value
			warnings.warn(PPUserWarning(tokens[0], msg))
			return
			
		module._macro_undef[id.value] = tokens[0]
		
		
	def define(me, module, tokens):
		if len(tokens) == 2 or tokens[2].type != 'ID':
			me.error(t[1])
			return
			
		id = tokens[2]
		
		if me.has_macro(module, id):
			if id.value in module._macro_pos:
				pos = module._macro_pos[id.value]
				me.error(id, 'プリプロセッサシンボル"%s"が再定義されています\n'%id.value
						+ '(以前の定義"%s(%d)")'%(pos.file, pos.line))
			else:
				me.error(id, 'プリプロセッサシンボル"%s"が再定義されています'%id.value)
			return		
			
		if len(tokens) > 3 and tokens[3].type == '(' and tokens[3].col == id.col + len(id.value):
			## #define SYMBOL(...  の形。"("の前にスペースがあってはいけない
			macro = ComplexMacro(id)
			macro.Parse(tokens[3:])
			module._macro_complex[id.value] = macro
			module._macro_pos[id.value] = id
			if id.value in module._macro_undef:
				del module._macro_undef[id.value]
		else:
			module._macro_simple[id.value] = (id, tokens[3:])
			module._macro_pos[id.value] = id
			if id.value in module._macro_undef:
				del module._macro_undef[id.value]
			
			
	def pragma(me, module, tokens):
		if len(tokens) == 2 or tokens[2].type != 'ID':
			me.error(t[1])
			return
			
		if tokens[2].value == 'once':
			raise
		else:
			msg = 'pragma "%s"を無視します。'%tokens[2].value
			warnings.warn(PPUserWarning(tokens[0], msg))
			
	def open_include(me, module, name):
				encoding = me.default_encoding
				d = name
				while d != os.path.dirname(d):
					d = os.path.dirname(d)
					if d in me.dir_encodings:
						encoding = me.dir_encodings[d]
						break
				try:
					with open(name, encoding=encoding) as f:
						src = f.read()
				except UnicodeDecodeError as ue:
					me.error(tokens[2], msg='次のファイルの%sデコードに失敗しました。"%s"'%(encoding, name))
					return
				yield from me._read_source(module, src, name, 1, encoding)
		
		
	def include(me, module, tokens):
		if len(tokens) < 2 or tokens[0].type != '#' or tokens[1].value != 'include':
			raise FatalError()
			
		if len(tokens) == 2:
			me.error(t[1])
			return
		if tokens[2].type == 'CS':
			filename = tokens[2].value
			curdir = os.path.dirname(tokens[2].file)
			name = os.path.join(curdir, filename)
			name = os.path.abspath(name)
			
			if os.path.exists(name):
				#print(tokens[0].file)
				#print('\t->', name)
				return (yield from me.open_include(module, name))
				
			name = tokens[2].value.replace('/', '\\')
		elif tokens[2].type == '<':
			try:
				index = [t.type for t in tokens[3:]].index('>')
				filename = tokens[3].line_string[tokens[3].col:tokens[3+index].col]
			except:
				me.error(tokens[0])
				return
				
		for dir in me.includes:
			name = os.path.join(dir, filename)
			name = os.path.abspath(name)
			if os.path.exists(name):
				#print(tokens[0].file)
				#print('\t->', name)
				return (yield from me.open_include(module, name))

		me.error(tokens[0], 'includeファイル"%s"が見つかりません'%filename, IncludeFileNotFound)
		
	def directive(me, module, it, tokens):
		if not tokens or tokens[0].type != '#':
			me.error(tokens[0])
			return
			
		if len(tokens) == 1 or tokens[1].type != 'ID':
			me.error(tokens[0])
			return
			
		if tokens[1].value == 'line':
			if len(tokens) == 2:
				me.error(tokens[1])
				return
			lineno = me.eval(module, tokens[2:], tokens[0])
			it.throw(Tokenizer.ChangeLineno(lineno))
		elif tokens[1].value == 'error':
			if len(tokens) > 2:
				msg = tokens[2].line_string[tokens[2].col:]
			else:
				msg = ''
			warnings.warn(PPUserError(tokens[0], msg))
		elif tokens[1].value == 'warning':
			if len(tokens) > 2:
				msg = tokens[2].line_string[tokens[2].col:]
			else:
				msg = ''
			warnings.warn(PPUserWarning(tokens[0], msg))
		elif tokens[1].value == 'pragma':
			me.pragma(module, tokens)
		elif tokens[1].value == 'define':
			me.define(module, tokens)
		elif tokens[1].value == 'include':
			yield from me.include(module, tokens)
		elif tokens[1].value == 'undef':
			me.undef(module, tokens)
		else:
			msg = '不明なマクロです("#%s")'%tokens[1].value
			warnings.warn(PPUserWarning(tokens[0], msg))
			

		
	def read(me, module, tokens, it):
		t = [t for t in tokens if t.type != 'MC']
		
		if t and t[0].type == '#':
			if len(t) == 1 or t[1].type != 'ID':
				msg = '不正なマクロです。'
				err = PreprocessError(t[0], msg)
				warnings.warn(err)
			if t[1].value == 'if':
				if me.eval(module, t[2:], t[1]):
					yield from me.read_for_el(module, it, t[1])
					return
				else:
					yield from me.skip_for_el(module, it, t[1])
					return
			elif t[1].value == 'ifdef':
				if len(t) < 3 or t[2].type != 'ID':
					me.error(t[0])
				if me.has_macro(module, t[2]):
					yield from me.read_for_el(module, it, t[1])
					return
				else:
					yield from me.skip_for_el(module, it, t[1])
					return
			elif t[1].value == 'ifndef':
				if len(t) < 3 or t[2].type != 'ID':
					me.error(t[0])
				if not me.has_macro(module, t[2]):
					yield from me.read_for_el(module, it, t[1])
					return
				else:
					yield from me.skip_for_el(module, it, t[1])
					return
			elif t[1].value == 'else':
				me.error(t[0], '#elseに対応する#ifがありません')
				return
			elif t[1].value == 'elif':
				me.error(t[0], '#elifに対応する#ifがありません')
				return
			elif t[1].value == 'endif':
				me.error(t[0], '#endifに対応する#ifがありません')
				return
			else:
				yield from me.directive(module, it, t)
				return
		else:
			yield from me.yield_tokens(module, tokens, it)
			#yield t
			
	def yield_tokens(me, module, tokens, it):
		res = []
		for i,t in enumerate(tokens):
			if t.type == 'ID' and me.has_macro(module, t):
				if res:
					yield res
					res = []
				yield from me.replace_macro(module, tokens[i:], it)
				return
			elif t.type == 'MC':
				if res:
					yield res
					res = []
				yield [t]
			else:
				res += [t]
		if res:
			yield res
			
	def replace_macro(me, module, tokens, it):
		if not tokens or tokens[0].type != 'ID':
			raise FatalError()
			
		id = tokens[0]
		if id.value in me._macro_simple:
			t = copy_tokens(module._macro_simple[id.value][1], id, module._macro_simple[id.value][0])
			yield from me.yield_tokens(module, t + tokens[1:], it)
			return
		if id.value in me._macro_complex:
			if len(tokens) == 1 or tokens[1].type != '(':
				# '('が続いてなければ通常のID扱いでいい
				yield from me.yield_tokens(module, [id] + tokens[1:], it)
				return
			prcnt = 0
			res = []
			while 1:
				for t in tokens[1:]:
					if t.type == '(':
						prcnt += 1
					elif t.type == ')' and prcnt > 0:
						prcnt -= 1
					elif t.type == ')' and prcnt == 0:
						res += [t]
						break
					if t.type != 'MC':
						res += [t]
				else:
					try:
						ts = next(it)
						continue
					except StopIteration:
						me.error(tokens[1], msg="マクロ%sの()が閉じていません"%id.value)
						return
				break
			ts = me._macro_complex[id.value](res)
			yield from me.yield_tokens(module, ts + tokens[1:], it)
			return
		if id.value in me._macro_special:
			t = me._macro_special[id.value](id)
			yield from me.yield_tokens(module, t + tokens[1:], it)
			return
		if id.value in module._macro_simple:
			#print(module._macro_simple[id.value])
			#raise
			t = copy_tokens(module._macro_simple[id.value][1], id, module._macro_simple[id.value][0])
			yield from me.yield_tokens(module, t + tokens[1:], it)
			return
		if id.value in module._macro_complex:
			if len(tokens) == 1 or tokens[1].type != '(':
				# '('が続いてなければ通常のID扱いでいい
				yield [id]
				yield from me.yield_tokens(module, tokens[1:], it)
				return
			prcnt = 0
			res = [tokens[1]]
			ts = iter(tokens[2:])
			#import pdb;pdb.set_trace()
			while 1:
				for t in ts:
					if t.type == '(':
						prcnt += 1
					elif t.type == ')' and prcnt > 0:
						prcnt -= 1
					elif t.type == ')' and prcnt == 0:
						res += [t]
						break
					if t.type != 'MC':
						res += [t]
				else:
					try:
						ts = iter(next(it))
						continue
					except StopIteration:
						me.error(tokens[1], msg="マクロ%sの()が閉じていません"%id.value)
						return
				break
			rep = module._macro_complex[id.value].Replace(res)
			rep += list(ts)
			
			new = rep[:1]
			it = enumerate(rep[1:])
			for i,t in it:
				if t.type == '##':
					i,t = next(it)
					new[-1].value += t.value
				elif t.type == '#':
					i,t = next(it)
					#new[-1].value += t.value
					new += [TokenDoubleQuote(repr(t.value),'',t.file,t.line,t.col,t.line_string)]
				else:
					new += [t]
			rep = new
			#if id.value == 'GLOBE_STRUCT':
			#	import pdb;pdb.set_trace()
			yield from me.yield_tokens(module, rep, it)
			
			return
		raise FatalError()
				


	def read_for_endif(me, module, it, first):
		try:
			while 1:
				t = me.read_line(it)
					
				if not t:
					continue
					
				if t[0].type == '#':
					if len(t) > 1:
						if t[1].value == 'endif':
							return
				yield from me.read(module, t, it)
				
				
		except StopIteration:
			msg = 'マクロ"%s"は閉じていません'%first.value
			err = PreprocessError(first, msg)
			warnings.warn(err)
			raise
			
			
	def read_for_el(me, module, it, first):
		try:
			while 1:
				t = me.read_line(it)
					
				if not t:
					continue
					
				if t[0].type == '#':
					if len(t) > 1:
						if t[1].value == 'else':
							me.skip_for_endif(it, t[1])
							return
						elif t[1].value == 'elif':
							me.skip_for_endif(it, t[1])
							return
						elif t[1].value == 'endif':
							return	
				yield from me.read(module, t, it)
				
		except StopIteration:
			msg = 'マクロ"%s"は閉じていません'%first.value
			err = PreprocessError(first, msg)
			warnings.warn(err)
			raise
			
	def skip_for_el(me, module, it, first):
		try:
			while 1:
				t = me.read_line(it)
				if not t:
					continue

				if t[0].type == '#':
					if len(t) > 1:
						if t[1].value == 'else':
							yield from me.read_for_endif(module, it, first)
							return
						elif t[1].value == 'elif':
							if me.eval(module, t[2:], t[1]):
								yield from me.read_for_el(module, it, first)
								return
							else:
								yield from me.skip_for_el(module, it, first)
								return
						elif t[1].value == 'endif':
							return
						elif t[1].value == 'if':
							me.skip_for_endif(it, t[1])
						elif t[1].value == 'ifdef':
							me.skip_for_endif(it, t[1])
						elif t[1].value == 'ifndef':
							me.skip_for_endif(it, t[1])
		except StopIteration:
			msg = 'マクロ"%s"は閉じていません'%first.value
			err = PreprocessError(first, msg)
			warnings.warn(err)
			raise

	def skip_for_endif(me, it, first):
		try:
			while 1:
				t = me.read_line(it)
					
				if not t:
					continue
					
				if t[0].type == '#':
					if len(t) > 1:
						if t[1].value == 'endif':
							return
						elif t[1].value in ('if', 'ifndef', 'ifdef'):
							me.skip_for_endif(it, t[1])
		except StopIteration:
			msg = 'マクロ"%s"は閉じていません'%first.value
			err = PreprocessError(first, msg)
			warnings.warn(err)
			raise
			
		
	def getInclededFrom(me, module):
		return None
		
	def proccess(me, src, file, line, encoding=''):
		module = ModuleObject()
		yield from me._read_source(module, src, file, line, encoding)
		
	def _read_source(me, module, src, file, line, encoding):
		back = me.tok.encoding
		it = me.tok.tokenize(src, file, line, encoding)
		for t in it:
			#try:
			#	while t and t[-1].type == '\\':
			#		t = t[:-1] + next(it)
			#except StopIteration:
			#	msg = '不正なマクロです。'
			#	err = PreprocessError(t[-1], msg)
			#	warnings.warn(err)
			#	return
				
			if not t:
				continue
				
			yield from me.read(module, t, it)
		me.tok.encoding = back
				
		
if __name__ == '__main__':
	import inspect
	tok = Tokenizer()
	
	lno = inspect.currentframe().f_lineno+1
	src = """
#define TEST(a,b) a+b
//#if TEST(0,1)
#if 1 == 0 || !defined (TEST)  || __LINE__ == 645
#error Yes!
#endif
#define TEST2 0
#if defined TEST2
#error error3
#endif
#if TEST(0
,1
)

yes
#endif
#if 0
#if 1
test
#elif 0
test3
#endif
#else
test1
test2
#else
#define TEST(a,b) a+b+__LINE__
#define TEST1 0
#error  エラーメッセージ！
#warning  warningメッセージ☆
#include"include/test.h"
#include<stdio.h>
88_Suf /*test comment*/
#endif
__LINE__
__FILE__
TEST1
"
TEST(__LINE__,1)
a.psrichap
#line 677
linetest
#line __LINE__+NODEF
linetest2
/
asrcp
"""

	lno = inspect.currentframe().f_lineno+1
	src = """
#define GLOBE_STRUCT( struct_tag, struct_name, name ) struct struct_tag { SHAPE *sp[F_MAX]; DBASE *dp[F_MAX]; int max_fileno; int dat_count; int max_count; struct_name *dat; char *ch; } name

typedef struct {
	GLOBE_STRUCT(globe_admin_poly_t__,       globe_admin_poly_t,       globe_admin_poly);
	GLOBE_STRUCT(globe_admin_line_t__,       globe_admin_line_t,       globe_admin_line);
	GLOBE_STRUCT(globe_admin_point_t__,      globe_admin_point_t,      globe_admin_point);
}X;
"""


	lno = inspect.currentframe().f_lineno+1
	src = """
#define TEST xxx
#define TEST1(x) x ## TEST ## __LINE__
#define TEST2(x) x TEST __LINE__
#define TEST3(x) x ## TEST __LINE__
TEST
TEST1(TESTA)
TEST1(TEST)
TEST2(TESTA)
TEST2(TEST)
TEST3(TESTA)
TEST3(TEST)
//TEST1(TEST1(X))
test test;
TEST1 (a)


#define TEST4(a,b) a b
#define TEST5 0,1
#define TEST6(a) a,0

//TEST4(TEST5)
//TEST4(TEST6(8))
TEST4(TEST5, TEST6(9))
TEST1(TEST5)

	
"""

	lno = inspect.currentframe().f_lineno+1
	_src = """
#ifdef HAVE_SSIZE_T
typedef ssize_t         Py_ssize_t;
#elif SIZEOF_VOID_P == SIZEOF_SIZE_T
typedef Py_intptr_t     Py_ssize_t;
#else
#   error "Python needs a typedef for Py_ssize_t in pyport.h."
#endif
"""

	src = r"""

#define X(t) t

#undef TESTAAA



X(int *) TESTAAA(int n)
{
	return 0;
}

"""
	file = __file__
	#file = r'C:\MyDocument\home\work\Python-3.4.1\Python-3.4.1\Python\pythonrun.c'
	#src = open(file).read()
	
	class ModDummy:
		pass
	
	pp = Preprocessor(Tokenizer(), includes=[r'C:\MyDocument\home\work\Python-3.4.1\Python-3.4.1\Include',
	                                         r'C:\MyDocument\home\work\Python-3.4.1\Python-3.4.1\PC'])
	it = pp.proccess(src, file, lno)
	rec = []
	with warnings.catch_warnings(record=True) as rec:
	#with warnings.catch_warnings() as rec:
		warnings.filterwarnings('error', category=NoueError)
		warnings.filterwarnings('error', category=PreprocessError)
		for t in it:
			#print(t)
			if t:
				#if t[0].file[-2:] == '.c':
				print('%d\t'%t[0].line, ' '.join([str(e.value) for e in t]))
			#for r in rec:
			#	print(r.message.message())
			#rec.clear()
			pass
	for r in rec:
		print(r.message.message())

