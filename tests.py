import os
from app.utils import check_answer, check_input
import app
import unittest

class TestCheckAnswer(unittest.TestCase):
    def test_numeric(self):
        answer = {"v1":"5"}
        self.assertTrue(check_answer("{v1} == 5",answer))
        self.assertTrue(check_answer("{v1} >= 3",answer))
        self.assertFalse(check_answer("{v1} > 5",answer))
        

if __name__ == '__main__':
    unittest.main()
