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

class checkInTest(TestCase):
    """
    Test For API 12
    """
    def setUp(self):
        djangoUser.objects.create_superuser(sys_superuser['username'], sys_superuser['email'],sys_superuser['password'])
        Activity(act_published).save()
        Ticket(ticket_valid).save()
        self.cl = Client()
        self.cl.post('api/a/login',sys_superuser)

    def tearDown(self):
        Ticket.objects.all().delete()
        Activity.objects.all().delete()
        self.cl.post('/api/a/logout', sys_superuser)

    def test_checkIn(self):
        self.cl.post('api/a/activity/checkin',1,'201601010101','')
        res_content = res.content.decode('utf-8')
        self.assertEqual(json.loads(res_content)['code'], 0)
        # try to check in with activity id and ticket id

    def test_checkIn_2(self):
        self.cl.post('api/a/activity/checkin',1,'','2016010101')
        res_content = res.content.decode('utf-8')
        self.assertEqual(json.loads(res_content)['code'], 0)
        # try to check in with activity id and student id

    def test_checkIn_3(self):
        self.cl.post('api/a/activity/checkin',1,'','')
        res_content = res.content.decode('utf-8')
        self.assertNotEqual(json.loads(res_content)['code'], 0)
        # try to check in only with activity id

    def test_checkIn_4(self):
        self.cl.post('api/a/activity/checkin',-1,'201601010101','')
        res_content = res.content.decode('utf-8')
        self.assertNotEqual(json.loads(res_content)['code'], 0)
        # try to check in with non-existent activity id and ticket id
