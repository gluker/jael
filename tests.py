import os
import app
import unittest
import tempfile

class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, app.app.config['DATABASE_URI'] = tempfile.mkstemp()
        app.app.config['DEBUG'] = True
        self.app = app.app.test_client()
        app.database.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.app.config['DATABASE_URI'])

    def test_unlogged(self):
        ans = self.app.get('/')
        print ans.data
        assert "/login/" and "Redirecting" in ans.data
        

if __name__ == '__main__':
    unittest.main()
