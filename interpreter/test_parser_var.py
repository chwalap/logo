from interpreter.parser import new_parser, vars
import unittest


class TestParserLogoViriables(unittest.TestCase):
    def setUp(self):
        self.p = new_parser()

        vars["foo"] = 5.
        vars["bar"] = 18
        vars["biz"] = 'lambada'

    def test_variable_get_value(self):
        self.assertEqual(self.p.parse(":foo"), 5.)
        self.assertEqual(self.p.parse(":bar"), 18)
        self.assertEqual(self.p.parse(":biz"), 'lambada')
        self.assertEqual(self.p.parse(":foo + :bar"), 5. + 18)
        self.assertRaises(TypeError, lambda: self.p.parse(":foo + :biz"))

        # todo: add tests for procedure thing

    def test_variable_set_value(self):
        self.assertEqual(self.p.parse("make \"foo 1"), None)
        # todo: bug -> should parse :foo + :bar before calling the function
        self.assertEqual(self.p.parse("make \"biz :foo + :bar"), None)
        self.assertEqual(self.p.parse("make \"bar \"lalala"), None)
        self.assertEqual(self.p.parse(":foo = :foo + :bar"), 123)


if __name__ == '__main__':
    unittest.main()
