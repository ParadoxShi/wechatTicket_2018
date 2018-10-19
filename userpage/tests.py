from django.test import TestCase, Client
from django.contrib.auth.models import User as djangoUser
from django.conf import settings
from wechat.models import *
import json
from datetime import timedelta
from django.utils import timezone
import os

# Create your tests here.

sys_superuser = {
    "username": "superuser",
    "email": '',
    "password": 'password'
}

act_published = {"id": 1,
                 "name": 'published',
                 "key": 'key1',
                 "place": 'hall',
                 "description": 'description',
                 "startTime": timezone.now() + timedelta(1000),
                 "endTime": timezone.now() + timedelta(2000),
                 "bookStart": timezone.now() - timedelta(500),
                 "bookEnd": timezone.now() + timedelta(500),
                 "totalTickets": 1000,
                 "status": Activity.STATUS_PUBLISHED,
                 "remainTickets": 1000,
                 "picUrl": "test_url"
}

ticket_valid = {"student_id": '2016010101',
                "unique_id": '201601010101',
                "activity": act_published,
                "status": Ticket.STATUS_VALID
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
        self.cl.post('/api/u/logout',sys_superuser)

    def test_getBindState(self):
        res = self.cl.get('api/u/user/bind')
        res_content = res.content.decode('utf-8')
        self.assertEqual(json.loads(res_content)['data'], '')
        # try to get bind state before binding

    def test_bind(self):
        res = self.cl.post('api/u/user/bind',student_id,password)
        res_content = res.content.decode('utf-8')
        self.assertEqual(json.loads(res_content)['code'], 0)
        # try to bind

    def test_getBindState_2(self):
        res = self.cl.get('api/u/user/bind')
        res_content = res.content.decode('utf-8')
        self.assertEqual(json.loads(res_content)['data'], '2016010101')
        # try to get bind state after binding

class activityDetailTest(TestCase):
    """
    Test For API 2
    """
    def setUp(self):
        djangoUser.objects.create_superuser(sys_superuser['username'], sys_superuser['email'],sys_superuser['password'])
        Activity(act_published).save()
        self.cl = Client()
        self.cl.post('api/u/login',sys_superuser)

    def tearDown(self):
        Activity.objects.all().delete()
        self.cl.post('/api/u/logout',sys_superuser)

    def test_getActivityDetail(self):
        res = self.cl.get('api/u/activity/detail',1)
        res_content = res.content.decode('utf-8')
        self.assertEqual(json.loads(res_content)['code'], 0)
        # try to get detail of a exist activity

    def test_getActivityDetail_2(self):
        res = self.cl.get('api/u/activity/detail',-1)
        res_content = res.content.decode('utf-8')
        self.assertNotEqual(json.loads(res_content)['code'], 0)
        # try to get detail of a non-existent activity

class ticketDetailTest(TestCase):
    """
    Test For API 3
    """
    def setUp(self):
        djangoUser.objects.create_superuser(sys_superuser['username'], sys_superuser['email'],sys_superuser['password'])
        Activity(act_published).save()
        Ticket(ticket_valid).save()
        self.cl = Client()
        self.cl.post('api/u/login',sys_superuser)

    def tearDown(self):
        Ticket.objects.all().delete()
        Activity.objects.all().delete()
        self.cl.post('/api/u/logout',sys_superuser)

    def test_getTicketDetail(self):
        res = self.cl.get('api/u/ticket/detail','201601010101')
        res_content = res.content.decode('utf-8')
        self.assertEqual(json.loads(res_content)['code'], 0)
        # try to get detail of a exist ticket

    def test_getTicketDetail_2(self):
        res = self.cl.get('api/u/ticket/detail','-1')
        res_content = res.content.decode('utf-8')
        self.assertNotEqual(json.loads(res_content)['code'], 0)
        # try to get detail of a non-existent ticket
        