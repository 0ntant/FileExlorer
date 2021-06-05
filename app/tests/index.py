import unittest
import sys

sys.path.append('./../')

import model

class TestUM(unittest.TestCase):
    def setUP(self):
        pass
        
    def tearDown(self):
        pass
    
    def test_read_file_list(self):
        file_model = model.FileModel()
        self.assertIsInstance(file_model.read_file_list(), list)
        #self.assertEqual(file_model.read_file_list('fuck'), list())
        self.assertRaises(TypeError,file_model.read_file_list())

unittest.main()
