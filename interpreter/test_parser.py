from interpreter.parser import new_parser
import unittest


class TestParserLogoSimpleMathExamples(unittest.TestCase):
    def setUp(self):
        self.p = new_parser()

    def test_binary_operator(self):
        # a op b
        self.assertEqual(self.p.parse("2 + 2"), 4)
        self.assertEqual(self.p.parse("5 * 10"), 50)
        self.assertEqual(self.p.parse("8 - 20"), -12)
        self.assertEqual(self.p.parse("2 / 16"), 0.125)

    def test_binary_operator_precedence(self):
        # a op b op c
        self.assertEqual(self.p.parse("2 + 2 * 2"), 6)
        self.assertEqual(self.p.parse("2 - 2 * 2"), -2)
        self.assertEqual(self.p.parse("2 + 2 / 2"), 3)
        self.assertEqual(self.p.parse("2 - 2 / 2"), 1)
        self.assertEqual(self.p.parse("1 + 2 + 100"), 103)
        self.assertEqual(self.p.parse("3 + 4 - 5"), 2)
        self.assertEqual(self.p.parse("3 - 4 + 5"), 4)
        self.assertEqual(self.p.parse("3 - 4 - 5"), -6)
        self.assertEqual(self.p.parse("3 * 4 * 5"), 60)
        self.assertEqual(self.p.parse("3 * 4 * 5"), 60)
        self.assertEqual(self.p.parse("3 / 3 * 5"), 5)
        self.assertEqual(self.p.parse("128 * 4 / 2"), 256)

    def test_binary_operator_parentheses(self):
        # (a op b) op c
        self.assertEqual(self.p.parse("(2 + 2) * 2"), 8)
        self.assertEqual(self.p.parse("(2 - 2) * 2"), 0)
        self.assertEqual(self.p.parse("(2 + 2) / 2"), 2)
        self.assertEqual(self.p.parse("(2 - 2) / 2"), 0)
        self.assertEqual(self.p.parse("(1 + 2) + 100"), 103)
        self.assertEqual(self.p.parse("(3 + 4) - 5"), 2)
        self.assertEqual(self.p.parse("(3 - 4) + 5"), 4)
        self.assertEqual(self.p.parse("(3 - 4) - 5"), -6)
        self.assertEqual(self.p.parse("(3 * 4) * 5"), 60)
        self.assertEqual(self.p.parse("(3 * 4) * 5"), 60)
        self.assertEqual(self.p.parse("(3 / 3) * 5"), 5)
        self.assertEqual(self.p.parse("(128 * 4) / 2"), 256)

        # a op (b op c)
        self.assertEqual(self.p.parse("2 * (2 + 2)"), 8)
        self.assertEqual(self.p.parse("2 * (2 - 2)"), 0)
        self.assertEqual(self.p.parse("2 / (2 + 2)"), 0.5)
        self.assertRaises(ZeroDivisionError,
                          lambda: self.p.parse("2 / (2 - 2)"))
        self.assertEqual(self.p.parse("1 + (2 + 100)"), 103)
        self.assertEqual(self.p.parse("3 + (4 - 5)"), 2)
        self.assertEqual(self.p.parse("3 - (4 + 5)"), -6)
        self.assertEqual(self.p.parse("3 - (4 - 5)"), 4)
        self.assertEqual(self.p.parse("3 * (4 * 5)"), 60)
        self.assertEqual(self.p.parse("3 * (4 * 5)"), 60)
        self.assertEqual(self.p.parse("3 / (3 * 5)"), 0.2)
        self.assertEqual(self.p.parse("128 * (4 / 2)"), 256)

    def test_boolean_operators(self):
        self.assertTrue(self.p.parse("2=2"))
        self.assertFalse(self.p.parse("2<>2"))
        self.assertTrue(self.p.parse("5<>8"))
        self.assertFalse(self.p.parse("123<>123"))
        self.assertTrue(self.p.parse("11.5=11.5"))
        self.assertFalse(self.p.parse("3.14<>3.14"))

        self.assertTrue(self.p.parse("2 + 2 = 4"))
        self.assertTrue(self.p.parse("3 - 3 = 0"))
        self.assertTrue(self.p.parse("24 + 0.0000001 <> 6 * 4"))
        self.assertTrue(self.p.parse("24 = 6 * 4"))
        self.assertTrue(self.p.parse("11.1 <> 22.3 / 2"))
        self.assertTrue(self.p.parse("11.1 = 22.2 / 2"))
        self.assertTrue(self.p.parse("6 + 2 <> 2 - 6"))
        self.assertTrue(self.p.parse("6 + 2 = 2 + 6"))
        self.assertTrue(self.p.parse("5 <> 4 * 8 - 15"))
        self.assertTrue(self.p.parse("5 = 4 + 1"))
        self.assertTrue(self.p.parse("88 / 4 + 2 * 3 <> 1"))
        self.assertTrue(self.p.parse("88 / 4 + 2 * 3 = 28"))

    def test_word_converters(self):
        self.assertEqual()


if __name__ == '__main__':
    unittest.main()
