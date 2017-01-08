from collections import namedtuple


class Node(object):

    @classmethod
    def from_parse_result(cls, tok, pos, children):
        return cls(*children)

    def accept(self, visitor, **kwargs):
        visit_method = getattr(visitor, 'visit_' + type(self).__name__.lower(), visitor.generic_visit)
        return visit_method(self, **kwargs)


class Block(namedtuple('Block', ['statements']), Node):

    def __new__(cls, *statements):
        return super(Block, cls).__new__(cls, list(statements))

class Assignment(namedtuple('Assignment', ['variables', 'expressions']), Node):

    def __new__(cls, variables, expressions):
        return super(Assignment, cls).__new__(cls, list(variables), list(expressions))


class LiteralString(namedtuple('LiteralString', ['value']), Node):

    def __new__(cls, value):
        return super(LiteralString, cls).__new__(cls, value)


class Var(namedtuple('Var', ['name']), Node):

    def __new__(cls, name):
        return super(Var, cls).__new__(cls, name)


class Table(namedtuple('Table', ['fields']), Node):

    def __new__(cls, *fields):
        return super(Table, cls).__new__(cls, list(fields))


class UnnamedField(namedtuple('UnnamedField', ['value']), Node):

    def __new__(cls, value):
        return super(UnnamedField, cls).__new__(cls, value)


class NamedField(namedtuple('NamedField', ['key', 'value']), Node):

    def __new__(cls, key, value):
        return super(NamedField, cls).__new__(cls, key, value)


class Boolean(namedtuple('Boolean', ['value']), Node):

    def __new__(cls, value):
        assert (value in ['true', 'false'])
        return super(Boolean, cls).__new__(cls, value == 'true')


class Nil(namedtuple('Nil', []), Node):

    _instance = None

    def __new__(cls, value):
        assert value is 'nil'
        if cls._instance is None:
            cls._instance = super(Nil, cls).__new__(cls)
        return cls._instance

nil = Nil('nil')

class Semicolon(namedtuple('Semicolon', []), Node):

    _instance = None

    def __new__(cls, value):
        assert value is ';'
        if cls._instance is None:
            cls._instance = super(Semicolon, cls).__new__(cls)
        return cls._instance

semicolon = Semicolon(';')

class FunctionCall(namedtuple('FunctionCall', ['function', 'args']), Node):

    def __new__(cls, fun, args):
        return super(FunctionCall, cls).__new__(cls, fun, list(args))
