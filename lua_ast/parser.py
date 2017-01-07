#-*- coding: utf-8 -*-
from __future__ import absolute_import
from pyparsing import (alphanums, alphas, Forward, Group, Keyword, Literal,
                       OneOrMore, Optional, QuotedString, restOfLine, Suppress, Word,
                       ZeroOrMore)

from . import ast

# "Names (also called identifiers) in Lua can be any string of letters,
#  digits, and underscores, not beginning with a digit."
name = Word( alphas + "_", alphanums + "_" )

comment = Suppress(Literal('--') + restOfLine)

# XXX: we are cheating a lot here as there is also long bracket form...
literal_string = (QuotedString("'", "\\") | QuotedString('"', "\\")).setParseAction(ast.LiteralString.from_parse_result)

exp = Forward()
explist = Forward()
tableconstructor = Forward()

# args ::=  ‘(’ [explist] ‘)’ | tableconstructor | LiteralString
args = (Suppress('(') + Optional(explist, default=[]) + Suppress(')')) | tableconstructor | Group(literal_string)
# var ::=  Name
var = name.copy().setParseAction(ast.Var.from_parse_result)

# I've made a split of cases to avoid infinite recurrsion
# functioncall ::=  prefixexp args | prefixexp ‘:’ Name args
functioncall_simple = ((var | (Suppress('(') + exp + Suppress(')'))) + args).setParseAction(ast.FunctionCall.from_parse_result)
functioncall_chain = (functioncall_simple +
                      OneOrMore(args)).setParseAction(lambda t, p, c: reduce(ast.FunctionCall,
                                                                             map(list, c[1:]),
                                                                             ast.FunctionCall(*c[0])))
functioncall = functioncall_chain | functioncall_simple

# prefixexp ::= var | functioncall | ‘(’ exp ‘)’
prefixexp = (functioncall | var | (Suppress('(') + exp + Suppress(')')))

# exp ::=  nil | false | true | Numeral | LiteralString | ‘...’ | functiondef |
#          prefixexp | tableconstructor | exp binop exp | unop exp
exp << (Keyword('nil').setParseAction(ast.Nil.from_parse_result) |
        (Keyword('true') | Keyword('false')).setParseAction(ast.Boolean.from_parse_result) |
        literal_string | prefixexp | tableconstructor)

# explist ::= {exp `,´} exp
explist << Group(exp + ZeroOrMore(Suppress(",") + exp))

semicolon = Literal(';').setParseAction(ast.Semicolon.from_parse_result)

# varlist ::= var {`,´ var}
varlist = Group(var + ZeroOrMore(Suppress(",") + var)).setParseAction(lambda t, p, c: c)

# stat ::=  varlist `=´ explist
stat = (varlist + Suppress("=") + explist).setParseAction(ast.Assignment.from_parse_result) | functioncall | semicolon

# retstat ::= return [explist] [‘;’]
retstat = (Keyword("return") + Optional(explist) + semicolon)

# block ::= {stat} [retstat]
block = (Optional(ZeroOrMore(stat | retstat | comment), default=[])).setParseAction(ast.Block.from_parse_result)

#field ::= `[´ exp `]´ `=´ exp | Name `=´ exp | exp
#field = Group("[" + exp + "]" + Literal("=") + exp) ...
field = ((name + Suppress('=') + exp).setParseAction(ast.NamedField.from_parse_result) |
         exp.copy().setParseAction(ast.UnnamedField.from_parse_result))

# fieldsep ::= `,´ | `;´
fieldsep = Literal(",") | Literal(";")

# fieldlist ::= field {fieldsep field} [fieldsep]
fieldlist = field + ZeroOrMore(Suppress(fieldsep) + field) + Optional(fieldsep)

# tableconstructor ::= `{´ [fieldlist] `}´
tableconstructor << (Suppress("{") + Optional(fieldlist) + Suppress("}")).setParseAction(ast.Table.from_parse_result)

def parse(s):
    return block.parseString(s, parseAll=True)[0]
