import unittest

from lua_ast.ast import Assignment, Boolean, Block, FunctionCall, LiteralString, NamedField, nil, semicolon, Table, UnnamedField, Var
from lua_ast import parse
from lua_ast import printer

class ParserTestCase(unittest.TestCase):

    def assertParsesFirstStatement(self, code, expected):
        self.assertEqual(parse(code)[0], expected)

    def assertParsesBlock(self, code, expected):
        self.assertEqual(parse(code), expected)

    def test_string(self):
        self.assertParsesFirstStatement('x = "lorem ipsum"', [Assignment([Var('x')], [LiteralString("lorem ipsum")])])

    def test_comments_are_ignored_at_the_end_of_line(self):
        self.assertParsesFirstStatement('x = "lorem ipsum" -- comment',
                                        [Assignment([Var('x')], [LiteralString("lorem ipsum")])])

    def test_mutilple_string_assignments(self):
        self.assertParsesBlock('x = "lorem ipsum"; y = "lipsum"',
                               Block(Assignment([Var('x')],
                                                  [LiteralString('lorem ipsum')]),
                                     semicolon,
                                     Assignment([Var('y')],
                                                [LiteralString('lipsum')])))

    def test_comments_lines_are_ignored(self):
        self.assertParsesBlock('x = "lorem ipsum"\n'
                               '-- comment\n'
                               '-- \n'
                               '-- another comment\n'
                               'y = "lipsum"',
                               Block(Assignment([Var('x')],
                                                  [LiteralString('lorem ipsum')]),
                                     Assignment([Var('y')],
                                                [LiteralString('lipsum')])))

    def test_nil(self):
        self.assertParsesFirstStatement('x = nil', [Assignment([Var('x')], [nil])])

    def test_empty_table(self):
        self.assertParsesFirstStatement('x = {}', [Assignment([Var('x')], [Table()])])

    def test_table_with_unnamed_fields(self):
        self.assertParsesFirstStatement('x = {"lorem ipsum", true}',
                          [Assignment([Var('x')],
                                      [Table(UnnamedField(LiteralString(value='lorem ipsum')),
                                             UnnamedField(Boolean('true')))])])

    def test_table_with_named_fields(self):
        self.assertParsesFirstStatement('x = {field1="lorem ipsum", field2=true}',
                          [Assignment([Var('x')],
                                      [Table(NamedField('field1', LiteralString('lorem ipsum')),
                                             NamedField('field2', Boolean('true')))])])

    def test_function_call_without_args(self):
        self.assertParsesFirstStatement('f()',
                          [FunctionCall(Var('f'), [])])

    def test_function_call_with_args_list(self):
        self.assertParsesFirstStatement('f(a)',
                          [FunctionCall(Var('f'), [Var('a')])])

    def test_function_call_with_arg_string(self):
        self.assertParsesFirstStatement('f "string"',
                          [FunctionCall(Var('f'), [LiteralString('string')])])

    def test_function_call_chain(self):
        self.assertParsesFirstStatement('f(a)(b)(c)',
                          [FunctionCall(FunctionCall(FunctionCall(Var('f'), [Var('a')]), [Var('b')]), [Var('c')])])

    def assertPrints(self, node, expected):
        self.assertEqual(printer.ast_to_string(node), expected)

    def test_print_assignment(self):
        self.assertPrints(Assignment([Var('x')], [LiteralString('test')]), "x = 'test'")

    def test_print_assignments(self):
        self.assertPrints(parse("x = 'first'; y = 'second'"), "x = 'first'\ny = 'second'")

    def test_print_functioncall_without_args(self):
        self.assertPrints(parse("f()"), "f()")

    def test_print_functioncall_with_single_arg(self):
        self.assertPrints(parse("f 'argument'"), "f('argument')")

    def test_print_functioncall_with_multiple_args(self):
        self.assertPrints(parse("f('argument',true,false)"), "f('argument', true, false)")

    def test_print_empty_table(self):
        self.assertPrints(Table(), "{}")

    def test_print_table_with_unnamed_fields(self):
        self.assertPrints(parse("x = {true, false, 'test', nil}"), "x = {\n\ttrue,\n\tfalse,\n\t'test',\n\tnil\n}")

    def test_print_table_with_named_fields(self):
        self.assertPrints(parse("x = {true = '1', false = '2'}"), "x = {\n\ttrue = '1',\n\tfalse = '2'\n}")

if __name__ == '__main__':
    unittest.main()
