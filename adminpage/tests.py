from django.test import TestCase

# Create your tests here.

sys_superuser = {
    "username": "superuser",
    "email": '',
    "password": 'password'
}

class userBindTest(TestCase):
    """
    Test For API 1
    """
    student_id = '2016010101'
    password = 'password'
    def setUp(self):
        djangoUser.objects.create_superuser(sys_superuser['username'], sys_superuser['email'],sys_superuser['password'])
        self.cl = Client()
        self.cl.post('api/u/login',sys_superuser)

    def tearDown(self):
        self.cl.post('/api/u/logout', sys_superuser)

    def test_getBindState(self):
        res = self.cl.get('api/u/user/bind')
        res_content = res.content.decode('utf-8')
        self.assertEqual(json.loads(res_content)['data'], '')

    def test_bind(self):
        res = self.cl.post('api/u/user/bind',student_id,password)
        res_content = res.content.decode('utf-8')
        self.assertEqual(json.loads(res_content)['code'], 0)

    def test_getBindState_2(self):
        res = self.cl.get('api/u/user/bind')
        res_content = res.content.decode('utf-8')
        self.assertEqual(json.loads(res_content)['data'], '2016010101')
