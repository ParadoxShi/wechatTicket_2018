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

act_published = {
    "id": 1,
    "name": 'published',
    "key": 'key1',
    "place": 'hall',
    "description": 'description',
    "startTime": timezone.now() + timedelta(1000),
    "endTime": timezone.now() + timedelta(2000),
    "bookStart": timezone.now() + timedelta(500),
    "bookEnd": timezone.now() + timedelta(800),
    "totalTickets": 1000,
    "status": Activity.STATUS_PUBLISHED,
    "remainTickets": 1000,
    "picUrl": "test_url"
}

act_saved = {
    "id": 2,
    "name": 'saved',
    "key": 'key2',
    "place": 'hall',
    "description": 'description',
    "startTime": timezone.now() + timedelta(1000),
    "endTime": timezone.now() + timedelta(2000),
    "bookStart": timezone.now() + timedelta(500),
    "bookEnd": timezone.now() + timedelta(800),
    "totalTickets": 1000,
    "status": Activity.STATUS_SAVED,
    "remainTickets": 1000,
    "picUrl": "test_url"
}

test_user = {
    'open_id': '0001',
    "student_id": '2016010101',
    "password": '201601010101'
}

never_existed_user = {
    'openid': '0002',
    "student_id": '2016012345',
    "password": '201601010101'
}


ticket_valid = {
    "open_id": test_user['open_id'],
    "student_id": test_user['student_id'],
    "unique_id": '201601010101',
    "status": Ticket.STATUS_VALID
}


def activity_anti_liquid(act):
    liquid ={
        "id": act['id'],
        "name": act['name'],
        "key": act['key'],
        "place": act['place'],
        "description": act['description'],
        "start_time": act['startTime'],
        "end_time": act['endTime'],
        "book_start": act['bookStart'],
        "book_end": act['bookEnd'],
        "total_tickets": act['totalTickets'],
        "status": act['status'],
        "remain_tickets": act['remainTickets'],
        "pic_url": act["picUrl"]
    }
    return liquid


class UserBindTest(TestCase):
    """
    Test For API 1
    """
    def setUp(self):
        User.objects.get_or_create(open_id=test_user['open_id'])
        self.cl = Client()

    def tearDown(self):
        User.objects.get(open_id=test_user['open_id']).delete()

    def test_getBindState(self):
        res = self.cl.get('/api/u/user/bind', {'openid': test_user['open_id']})
        res_content = res.content.decode('utf-8')
        self.assertEqual(json.loads(res_content)['data'], '')

        res = self.cl.post('/api/u/user/bind', {'openid': test_user['open_id'], 'student_id': test_user['student_id'],
                                                'password': test_user['password']})
        res_content = res.content.decode('utf-8')
        self.assertEqual(json.loads(res_content)['code'], 0)

        res = self.cl.get('/api/u/user/bind', {'openid': test_user['open_id']})
        res_content = res.content.decode('utf-8')
        self.assertEqual(json.loads(res_content)['data'], test_user['student_id'])
        # try to get bind state after binding


class ActivityDetailTest(TestCase):
    """
    Test For API 2
    """
    def setUp(self):
        act_p = activity_anti_liquid(act_published)
        act_s = activity_anti_liquid(act_saved)
        Activity(**act_p).save()
        Activity(**act_s).save()
        self.cl = Client()

    def tearDown(self):
        Activity.objects.all().delete()

    def test_getActivityDetail(self):
        res = self.cl.get('/api/u/activity/detail', {'id': 1})
        res_content = res.content.decode('utf-8')
        self.assertEqual(json.loads(res_content)['code'], 0)
        # try to get detail of a exist activity

    def test_getActivityDetail_2(self):
        res = self.cl.get('/api/u/activity/detail', {'id': 2})
        res_content = res.content.decode('utf-8')
        self.assertNotEqual(json.loads(res_content)['code'], 0)
        # try to get detail of a non-existent activity


class TicketDetailTest(TestCase):
    """
    Test For API 3
    """
    def setUp(self):
        act_p = activity_anti_liquid(act_published)
        Activity(**act_p).save()
        Ticket.objects.create(
            student_id=ticket_valid['student_id'],
            unique_id=ticket_valid['unique_id'],
            activity=Activity.objects.get(id=act_p['id']),
            status=Ticket.STATUS_VALID
        )
        User(student_id=test_user['student_id'], open_id=test_user['open_id']).save()
        self.cl = Client()

    def tearDown(self):
        Ticket.objects.all().delete()
        Activity.objects.all().delete()
        User.objects.all().delete()

    def test_getValidTicketDetail(self):
        res = self.cl.get('/api/u/ticket/detail', {'openid': ticket_valid['open_id'], 'ticket': ticket_valid['unique_id']})
        res_content = res.content.decode('utf-8')
        self.assertEqual(json.loads(res_content)['code'], 0)
        # try to get detail of a exist ticket

    def test_getInvalidTicketDetail(self):
        res = self.cl.get('/api/u/ticket/detail', {'openid': ticket_valid['open_id'], 'ticket': 'asdfoa2349'})
        res_content = res.content.decode('utf-8')
        self.assertNotEqual(json.loads(res_content)['code'], 0)
        # try to get detail of a non-existent ticket

