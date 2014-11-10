#coding; utf8


# コンパイルエラー型定義
# 2014/10/20
# auhtor: k.oonishi

# coding: utf8

import warnings

class CodePositional:
	def __init__(me, file, line, col, line_string):
		me.file   = file
		me.line   = line
		me.col    = col
		me.line_string = line_string
		
class NoueException(Warning):
	## positional: トークンオブジェクト
	def __init__(me, positional, msg):
		#me.file   = positional.file
		#me.lineno = positional.line
		#me.col    = positional.col
		me.msg    = msg
		#me.line_string = positional.line_string
		
		me.pos = positional
		
	def message(me):
		s  = me.msg + '\n'
		s += '>%s(%d,%d)\n'%(me.pos.file,me.pos.line, me.pos.col)
		s += '>' + '\n>'.join(me.pos.line_string.splitlines())
		pos = me.pos
		while hasattr(pos, 'define'):
			s += '\n\t>%s(%d,%d)\n'%(pos.define.file,pos.define.line, pos.define.col)
			s += '\t>'+ '\n\t>'.join(pos.define.line_string.splitlines())
			pos = pos.define
		return s
	
	
class NoueError(NoueException):
	def message(me):
		return 'error(%s)'%type(me).__name__ + ': ' + NoueException.message(me)
	
class NoueWarning(NoueException):
	def message(me):
		return 'warning(%s)'%type(me).__name__ + ': ' + NoueException.message(me)
	
class PPUserError(NoueError):
	pass
	
class PPUserWarning(NoueWarning):
	pass
	
class FatalError(Exception):
	pass

class CompileError(NoueError):
	pass
	
class TokenizeError(NoueError):
	def __init__(me, file, line, col, line_string, msg):
		pos = CodePositional(file, line, col, line_string)
		NoueError.__init__(me, pos, msg)
		
class PreprocessError(NoueError):
	pass
	
class PreprocessError(NoueWarning):
	pass

	
class IncludeFileNotFound(PreprocessError):
	pass


class SyntaxError(NoueError):
	def __init__(me, tok, msg):
		NoueError.__init__(me, tok, msg)

class ParseError(CompileError):
	def __init__(me, tok, msg):
		NoueError.__init__(me, tok, msg)
		
class ParseUnexpectedToken(ParseError):
	def __init__(me, tok):
		msg = '"%s"は不正です。'%tok.value
		ParseError.__init__(me, tok, msg)

class MissingToken(ParseUnexpectedToken):
	def __init__(me, tok, delim):
		ParseUnexpectedToken.__init__(me, tok)
		me.msg = '"%s"が必要です。'	%delim
		
class MissingSemicolon(MissingToken):
	def __init__(me, tok):
		MissingToken.__init__(me, tok, ";")

class SemanticError(CompileError):
	def __init__(me, tok, msg):
		NoueError.__init__(me, tok, msg)
		
class DefineDuplication(SemanticError):
	def __init__(me, newstmt, oldstmt):
		msg = '"%s"はすでに定義されています。\n' \
		'\t%s(%d)\n'\
		'\t%s'%(newstmt.id, oldstmt.first_token.file
				, oldstmt.first_token.line, oldstmt.first_token.line_string,)
		NoueError.__init__(me, newstmt.first_token, msg)

class InvalidTydename(SemanticError):
	def __init__(me, id):
		msg = '"%s"は不正な型名です'%id.value
		SemanticError.__init__(me, id, msg)
		
		

		
class NotConstInteger(SemanticError):
	def __init__(me, exp):
		msg = 'constな整数値が必要です'
		NoueError.__init__(me, exp.first_token, msg)
		
class InvalidArrayType(SemanticError):
	def __init__(me, tok, typ):
		msg = '"%s"の配列型は不正です'%typ.name
		NoueError.__init__(me, tok, msg)

	
class NotDefined(SemanticError):
	def __init__(me, tok):
		msg = '%sは定義されていません。'%tok.value
		NoueError.__init__(me, tok, msg)
		
class NotTypeDescriptor(NoueError):
	def __init__(me, tok):
		msg = '型識別子が必要です'
		NoueError.__init__(me, tok, msg)
		
		
class NotFunction(NoueError):
	def __init__(me, tok):
		msg = '関数ではありません'
		NoueError.__init__(me, tok, msg)
		
class OldStyleFunction(NoueError):
	def __init__(me, tok):
		NoueError.__init__(me, tok.file, tok.line, tok.col, tok.line_string, '')

class TypeError(SemanticError):
	def __init__(me, pos, msg):
		NoueError.__init__(me, pos, msg)
		
class CastError(SemanticError):
	def __init__(me, pos, target_type, source_type):
		msg = '%sを%sに変換できません'%(source_type.name, target_type.name)
		TypeError.__init__(me, pos, msg)
	
class BinOpTypeError(TypeError):
	def __init__(me, op, left, right):
		msg = '二項演算 "{left}" {op} "{right}"は不正です'.format(
					left=left.restype.name, right=right.restype.name, op=op)
		NoueError.__init__(me, left.first_token, msg)
		
class InvalidSizeof(TypeError):
	def __init__(me, tok, typ):
		msg = '"%s"に対するsizeofは不正です'%typ.name
		NoueError.__init__(me, tok, msg)

		
	
class UnsafeImplicitConversion(NoueWarning):
	def __init__(me, pos, lefttype, righttype):
		msg = '"{right}"から"{left}"への暗黙の変換が行われました。'.format(
					left=lefttype.name, right=righttype.name)
		NoueWarning.__init__(me, pos, msg)
		
class CallingUnknownFunction(NoueWarning):
	def __init__(me, id):
		msg = '不明な関数"%s"が呼ばれました'%id.value
		NoueWarning.__init__(me, id, msg)
		
class NoaffectStatement(NoueWarning):
	def __init__(me, pos):
		msg = 'ステートメントに効果がありません'
		NoueWarning.__init__(me, pos, msg)



class Integer2PointerConversion(NoueWarning):
	def __init__(me, pos, restype):
		msg = 'ポインタ型とはサイズの違う整数型"{type}"がポインタ型に変更されました'.format(
					type=restype.name)
		NoueWarning.__init__(me, pos, msg)
		
