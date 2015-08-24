import os
import app
import unittest
import urllib2
import tempfile
from flask_testing import LiveServerTestCase
from flask import Flask

class AppTestCase(LiveServerTestCase):
    def create_app(self):
        app = Flask(__name__)
        app.config['DATABASE_URI'] = 'sqlite:///testdb.db'
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['LIVESERVER_PORT'] = 8943 
        from app import views
        return app
    def test_server_is_up_and_running(self):
        print self.get_server_url()
        response = urllib2.urlopen(self.get_server_url())
        self.assertEqual(response.code, 200)
            

if __name__ == '__main__':
    unittest.main()
