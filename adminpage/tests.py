from django.test import TestCase
from adminpage.views import *
from django.contrib.auth.models import User
import json

# Mentions:
# Success code == 0
# Validate Error code == 3


superUserForTest = {'username': 'administrator',
                    'email': 'benjo@youknowthereisnotthiswebsite.com',
                    'password': 'guest2000'}
wrongUser1 = superUserForTest
wrongUser1['username'] = 'bdripistraitor'
wrongUser2 = superUserForTest
wrongUser2['password'] = 'prisoner9527'


## API 4 ##
class LoginTest(TestCase):
    def setUp(self):
        User.objects.create_superuser(username=superUserForTest['username'],
                                      email=superUserForTest['email'],
                                      password=superUserForTest['password'])

    def test_hasnot_login(self):
        rep = self.client.get('/api/a/login/')
        repObj = json.load(rep.content.decode('utf-8'))
        self.assertEqual(repObj['code'], 3)

    def test_log_in(self):
        rep = self.client.post('/api/a/login/', superUserForTest)
        self.assertEqual(rep.status_code, 200)
        repObj = json.load(rep.content.decode('utf-8'))
        self.assertEqual(repObj['code'], 0)

    def test_has_login(self):
        self.client.post('/api/a/login/', superUserForTest)
        rep = self.client.get('/api/a/login/')
        repObj = json.load(rep.content.decode('utf-8'))
        self.assertEqual(repObj['code'], 0)

    def test_failed_usr(self):
        rep = self.client.post('/api/a/login/', wrongUser1)
        repObj = json.load(rep.content.decode('utf-8'))
        self.assertEqual(repObj['code'], 3)

    def test_failed_pwd(self):
        rep2 = self.client.post('/api/a/login/', wrongUser2)
        repObj2 = json.load(rep2.content.decode('utf-8'))
        self.assertEqual(repObj2['code'], 3)

    def tearDown(self):
        pass


## API 5 ##
class LogOutTest(TestCase):
    def setUp(self):
        User.objects.create_superuser(username=superUserForTest['username'],
                                      email=superUserForTest['email'],
                                      password=superUserForTest['password'])

    def test_log_out(self):
        self.client.post('/api/a/login/', superUserForTest)
        rep = self.client.post('/api/a/logout/')
        repObj = json.load(rep.content.decode('utf-8'))
        self.assertEqual(repObj['code'], 0)

    def test_failed_not_logged_in(self):
        rep = self.client.post('/api/a/logout/')
        repObj = json.load(rep.content.decode('utf-8'))
        self.assertEqual(repObj['code'], 3)

    def tearDown(self):
        pass


## API 6 ##
#class ActivityListTest(TestCase):
