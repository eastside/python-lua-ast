import unittest

from lua_ast.ast import (Assignment, Block, Boolean, FunctionCall,
                         LiteralString, MethodCall, NamedField, nil, semicolon,
                         Table, UnnamedField, Var)
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

    def test_method_call_without_args(self):
        self.assertParsesFirstStatement('o:f()',
                          [MethodCall(Var('o'), Var('f'), [])])

    def test_function_call_with_args_list(self):
        self.assertParsesFirstStatement('f(a)',
                                        [FunctionCall(Var('f'), [Var('a')])])

    def test_method_call_with_args_list(self):
        self.assertParsesFirstStatement('o:f(a)',
                                        [MethodCall(Var('o'), Var('f'), [Var('a')])])

    def test_function_call_with_arg_string(self):
        self.assertParsesFirstStatement('f "string"',
                          [FunctionCall(Var('f'), [LiteralString('string')])])

    def test_method_call_with_arg_string(self):
        self.assertParsesFirstStatement('o:f "string"',
                                        [MethodCall(Var('o'), Var('f'), [LiteralString('string')])])

    def test_function_chain_of_two_calls(self):
        self.assertParsesFirstStatement('f(a)(b)',
                          [FunctionCall(FunctionCall(Var('f'), [Var('a')]), [Var('b')])])

    def test_method_chain_of_two_calls(self):
        self.assertParsesFirstStatement('o:m1(a):m2(b)',
                          [MethodCall(MethodCall(Var('o'), Var('m1'), [Var('a')]), Var('m2'), [Var('b')])])

    def test_mixed_chain_of_two_calls(self):
        self.assertParsesFirstStatement('o:m1(a)(b)',
                          [FunctionCall(MethodCall(Var('o'), Var('m1'), [Var('a')]), [Var('b')])])

    def test_function_call_chain(self):
        self.assertParsesFirstStatement('f(a)(b)(c)',
                          [FunctionCall(FunctionCall(FunctionCall(Var('f'), [Var('a')]), [Var('b')]), [Var('c')])])

    def test_method_call_chain(self):
        self.assertParsesFirstStatement('o:m1(a):m2(b, c):m3(d, e, f)',
                                        [MethodCall(MethodCall(MethodCall(Var('o'), Var('m1'),
                                                                          [Var('a')]),
                                                               Var('m2'), [Var('b'), Var('c')]),
                                                    Var('m3'), [Var('d'), Var('e'), Var('f')])])

    def test_function_call_chain_with_strings_arguments(self):
        self.assertParsesFirstStatement('f "a" "b" "c"',
                          [FunctionCall(FunctionCall(FunctionCall(Var('f'), [LiteralString('a')]), [LiteralString('b')]), [LiteralString('c')])])

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

    def test_print_functioncall_chain(self):
        self.assertPrints(parse("f(a)(b, c, d)(e)"), "f(a)(b, c, d)(e)")

    def test_print_method(self):
        self.assertPrints(parse("o:m()"), "o:m()")

    def test_print_methodcall_chain(self):
        self.assertPrints(parse("o:m1(a):m2(b, c, d):m3(e)"), "o:m1(a):m2(b, c, d):m3(e)")

    def test_print_empty_table(self):
        self.assertPrints(Table(), "{}")

    def test_print_table_with_unnamed_fields(self):
        self.assertPrints(parse("x = {true, false, 'test', nil}"), "x = {\n\ttrue,\n\tfalse,\n\t'test',\n\tnil\n}")

    def test_print_table_with_named_fields(self):
        self.assertPrints(parse("x = {true = '1', false = '2'}"), "x = {\n\ttrue = '1',\n\tfalse = '2'\n}")

if __name__ == '__main__':
    unittest.main()
