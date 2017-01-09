#-*- coding: utf-8 -*-
from __future__ import absolute_import
from .ast import semicolon

class Printer(object):
    """Not very smart or beautiful printer - no indentation, no styles etc."""

    @classmethod
    def generic_visit(cls, node):
        return str(node)

    @classmethod
    def visit_block(cls, node):
        result = []
        for s in node.statements:
            if s is semicolon:
                continue
            result.append(s.accept(cls))
        return '\n'.join(result)

    @classmethod
    def visit_var(cls, node):
        return node.name

    @classmethod
    def visit_literalstring(cls, node):
        return repr(node.value)

    @classmethod
    def visit_semicolon(cls, node):
        return ';'

    @classmethod
    def visit_functioncall(cls, node):
        function = node.function.accept(cls)
        arguments = cls._comma_separated_list(node.args)
        return '%s(%s)' % (function, arguments)

    @classmethod
    def visit_methodcall(cls, node):
        function = node.obj.accept(cls)
        method = node.method.name
        arguments = cls._comma_separated_list(node.args)
        return '%s:%s(%s)' % (function, method, arguments)

    @classmethod
    def visit_boolean(cls, node):
        if node.value:
            return 'true'
        return 'false'

    @classmethod
    def visit_table(cls, node):
        if not node.fields:
            return '{}'
        result = []
        result.append('{\n\t')
        result.extend(cls._intersperse((f.accept(cls) for f in node.fields), ',\n\t'))
        result.append('\n}')
        return ''.join(result)

    @classmethod
    def visit_assignment(cls, node):
        result = [cls._comma_separated_list(node.variables)]
        result.append('=')
        result.append(cls._comma_separated_list(node.expressions))
        return ' '.join(result)

    @classmethod
    def visit_unnamedfield(cls, node):
        return node.value.accept(cls)

    @classmethod
    def visit_namedfield(cls, node):
        result = [node.key]
        result.append('=')
        result.append(node.value.accept(cls))
        return ' '.join(result)

    @classmethod
    def visit_nil(cls, node):
        return 'nil'

    @classmethod
    def _comma_separated_list(cls, nodes):
        return ''.join(cls._intersperse(map(lambda n: n.accept(cls), nodes), ', '))

    @classmethod
    def _intersperse(cls, iterable, delimiter):
        it = iter(iterable)
        yield next(it)
        for x in it:
            yield delimiter
            yield x


def ast_to_string(ast):
    return ast.accept(Printer)

