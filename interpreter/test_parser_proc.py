from lparser import new_parser, procedures
import unittest


class TestParserLogoProcedures(unittest.TestCase):

    def setUp(self):
        self.p = new_parser()

    def test_simple_procedures(self):
        self.assertEqual(self.p.parse(
            "get_666", debug=True, tracking=True), 666)
        self.assertEqual(self.p.parse("f2 33"), 43)
        self.assertEqual(self.p.parse("f3 f1 f2 10"), 40)


if __name__ == '__main__':
    unittest.main()
