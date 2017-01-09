#-*- coding: utf-8 -*-
from __future__ import absolute_import
from pyparsing import (alphanums, alphas, Forward, Group, Keyword, Literal,
                       OneOrMore, Optional, QuotedString, restOfLine, Suppress, Word,
                       ZeroOrMore)

from . import ast

def from_parse_result(AstNode):
    return (lambda p, t, v: AstNode(*v))

# "Names (also called identifiers) in Lua can be any string of letters,
#  digits, and underscores, not beginning with a digit."
name = Word( alphas + "_", alphanums + "_" )

comment = Suppress(Literal('--') + restOfLine)

# XXX: we are cheating a lot here as there is also long bracket form... and some other differences...
literal_string = (QuotedString("'", "\\") | QuotedString('"', "\\")).setParseAction(lambda t, p, v: ast.LiteralString(*v))

exp = Forward()
explist = Forward()
tableconstructor = Forward()
# var ::=  Name
var = name.copy().setParseAction(from_parse_result(ast.Var))

# There is additional (":" + name) prefix which is moved here from
# functioncall definition
# args ::=  ‘(’ [explist] ‘)’ | tableconstructor | LiteralString
args = (Optional(Suppress(':') + var, default=None).setResultsName('method') +
        ((Suppress('(') + Optional(explist, default=[]) + Suppress(')')) | tableconstructor | Group(literal_string)).setResultsName('args'))


def function_or_method_call(parts):
    fun, method, args = parts[0], parts[1], parts[2]
    if method is None:
        return ast.FunctionCall(fun, list(args))
    else:
        return ast.MethodCall(fun, method, list(args))

# I've made a split of cases to avoid infinite recurrsion
# functioncall ::=  prefixexp args | prefixexp ‘:’ Name args
functioncall_simple = ((var | (Suppress('(') + exp + Suppress(')'))).setResultsName('fun') + args).setParseAction(function_or_method_call)

def fold_chain(t, p, c):
    i = iter(c[1:])
    return reduce(lambda fc, (m, a): function_or_method_call([fc, m, a]), zip(i, i), c[0])

functioncall_chain = (functioncall_simple +
                      OneOrMore(args)).setParseAction(fold_chain)
functioncall = functioncall_chain | functioncall_simple

# prefixexp ::= var | functioncall | ‘(’ exp ‘)’
prefixexp = (functioncall | var | (Suppress('(') + exp + Suppress(')')))

# exp ::=  nil | false | true | Numeral | LiteralString | ‘...’ | functiondef |
#          prefixexp | tableconstructor | exp binop exp | unop exp
exp << (Keyword('nil').setParseAction(from_parse_result(ast.Nil)) |
        (Keyword('true') | Keyword('false')).setParseAction(from_parse_result(ast.Boolean)) |
        literal_string | prefixexp | tableconstructor)

# explist ::= {exp `,´} exp
explist << Group(exp + ZeroOrMore(Suppress(",") + exp))

semicolon = Literal(';').setParseAction(from_parse_result(ast.Semicolon))

# varlist ::= var {`,´ var}
varlist = Group(var + ZeroOrMore(Suppress(",") + var)).setParseAction(lambda t, p, c: c)

# stat ::=  varlist `=´ explist
stat = (varlist + Suppress("=") + explist).setParseAction(lambda t, p, (e, v): ast.Assignment(list(e), list(v))) | functioncall | semicolon

# retstat ::= return [explist] [‘;’]
retstat = (Keyword("return") + Optional(explist) + semicolon)

# block ::= {stat} [retstat]
block = (Optional(ZeroOrMore(stat | retstat | comment), default=[])).setParseAction(from_parse_result(ast.Block))

#field ::= `[´ exp `]´ `=´ exp | Name `=´ exp | exp
#field = Group("[" + exp + "]" + Literal("=") + exp) ...
field = ((name + Suppress('=') + exp).setParseAction(from_parse_result(ast.NamedField)) |
         exp.copy().setParseAction(from_parse_result(ast.UnnamedField)))

# fieldsep ::= `,´ | `;´
fieldsep = Literal(",") | Literal(";")

# fieldlist ::= field {fieldsep field} [fieldsep]
fieldlist = field + ZeroOrMore(Suppress(fieldsep) + field) + Optional(fieldsep)

# tableconstructor ::= `{´ [fieldlist] `}´
tableconstructor << (Suppress("{") + Optional(fieldlist) + Suppress("}")).setParseAction(from_parse_result(ast.Table))

def parse(s):
    return block.parseString(s, parseAll=True)[0]
