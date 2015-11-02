import os
from app.utils import check_answer
import app
import unittest

class TestCheckAnswer(unittest.TestCase):
    def test_numeric(self):
        answer = {"v1":"5"}
        self.assertTrue(check_answer("{v1} == 5",answer))
        self.assertTrue(check_answer("{v1} >= 3",answer))
        self.assertFalse(check_answer("{v1} > 5",answer))
    
    def test_correctness(self):
        answer = {"v2":"print(__globals__)"}
        self.assertRaises(SyntaxError,check_answer,"{v2} != 7",answer)
        answer.update({"v1":'(lambda fc=( lambda n: [ c for c in  ().__class__.__bases__[0].__subclasses__()  if c.__name__ == n ][0] ): fc("function")( fc("code")( 0,0,0,0,0,b"KABOOM",(),(),(),"","",0,b"" ),{} )())()' }) 
        self.assertRaises(Exception,check_answer,"{v1} != 7",answer)

    def test_lim(self):
        self.assertTrue(check_answer("limit({v1},x,0) == 0",{"v1":"sin(x)"}))
        self.assertFalse(check_answer("limit({v1},x,0) == 0",{"v1":"cos(x)"}))
        self.assertTrue(check_answer("limit({v1},x,oo) == 0",{"v1":"1/x"}))
        self.assertTrue(check_answer("limit({v1},x,0) == oo",{"v1":"1/x"}))
        
if __name__ == '__main__':
    unittest.main()
