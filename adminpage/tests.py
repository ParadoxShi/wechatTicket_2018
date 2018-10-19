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
                 "start_time": timezone.now() + timedelta(1000),
                 "end_time": timezone.now() + timedelta(2000),
                 "book_start": timezone.now() - timedelta(500),
                 "book_end": timezone.now() + timedelta(500),
                 "total_tickets": 1000,
                 "status": Activity.STATUS_PUBLISHED,
                 "remain_tickets": 1000,
                 "pic_url": "test_url"
}

act_saved = {"id": 2,
             "name": 'saved',
             "key": 'key2',
             "place": 'hell',
             "description": 'description',
             "start_time": timezone.now() + timedelta(1000),
             "end_time": timezone.now() + timedelta(2000),
             "book_start": timezone.now() - timedelta(500),
             "book_end": timezone.now() + timedelta(500),
             "total_tickets": 1000,
             "status": Activity.STATUS_SAVED,
             "remain_tickets": 1000,
             "pic_url": "test_url"
}

act_deleted = {"id": 3,
               "name": 'published',
               "key": 'key3',
               "place": 'hall',
               "description": 'description',
               "start_time": timezone.now() + timedelta(1000),
               "end_time": timezone.now() + timedelta(2000),
               "book_start": timezone.now() + timedelta(500),
               "book_end": timezone.now() + timedelta(800),
               "total_tickets": 1000,
               "status": Activity.STATUS_DELETED,
               "remain_tickets": 1000,
               "pic_url": "test_url"
}

act_changed_detail = {
               "name": 'changed',
               "place": 'East Hall',
               "description": 'This is a new description.',
               "total_tickets": 500,
               "status": Activity.STATUS_SAVED,
               "pic_url": "test_url",
               "start_time": timezone.now() + timedelta(1000),
               "end_time": timezone.now() + timedelta(2000),
               "book_start": timezone.now() + timedelta(500),
               "book_end": timezone.now() + timedelta(800),
}


def activity_liquid(act):
    liquid ={
        "id": act['id'],
        "name": act['name'],
        "key": act['key'],
        "place": act['place'],
        "description": act['description'],
        "startTime": act['start_time'],
        "endTime": act['start_time'],
        "bookStart": act['start_time'],
        "bookEnd": act['start_time'],
        "totalTickets": act['total_tickets'],
        "status": act['status'],
        "remainTickets": act['remain_tickets'],
        "picUrl": act["pic_url"]
    }
    return liquid


class CreateActivityTest(TestCase):
    """
    Test For API 8
    """
    def setUp(self):
        djangoUser.objects.create_superuser(sys_superuser['username'], sys_superuser['email'], sys_superuser['password'])
        self.cl = Client()
        self.cl.post('/api/a/login', sys_superuser)

    def tearDown(self):
        Activity.objects.all().delete()
        self.cl.post('/api/a/logout', sys_superuser)

    def test_createPublishedActivity(self):
        res = self.cl.post('/api/a/activity/create', activity_liquid(act_published))
        res_content = res.content.decode('utf-8')
        self.assertEqual(json.loads(res_content)['code'], 0)

    def test_createSavedActivity(self):
        res = self.cl.post('/api/a/activity/create', activity_liquid(act_saved))
        res_content = res.content.decode('utf-8')
        self.assertEqual(json.loads(res_content)['code'], 0)


class UploadImageTest(TestCase):
    """
    Test For API 9
    """
    def setUp(self):
        djangoUser.objects.create_superuser(sys_superuser['username'], sys_superuser['email'], sys_superuser['password'])
        self.cl = Client()
        self.cl.post('/api/a/login', sys_superuser)

    def tearDown(self):
        self.cl.post('/api/a/logout', sys_superuser)

    def test_upload_image(self):
        path = os.path.join(settings.BASE_DIR, 'static/夜明けより前の君へ.jpg')
        with open(path, 'rb') as img:
            res = self.cl.post('/api/a/image/upload', {'image': img})
        res_content = res.content.decode('utf-8')
        self.assertEqual(json.loads(res_content)['code'], 0)


class ActivityDetailTest(TestCase):
    """
    Test For API 10
    """
    def setUp(self):
        djangoUser.objects.create_superuser(sys_superuser['username'], sys_superuser['email'],sys_superuser['password'])
        self.cl = Client()
        self.cl.post('/api/a/login', sys_superuser)
        Activity(**act_saved).save()

    def tearDown(self):
        Activity.objects.all().delete()
        self.cl.post('/api/a/logout', sys_superuser)

    def test_getDetail(self):
        res = self.cl.get('/api/a/activity/detail', {'id': act_saved['id']})
        res_content = res.content.decode('utf-8')
        self.assertEqual(json.loads(res_content)['code'], 0)

    def test_postDetail(self):
        copy_act = act_saved.copy()
        copy_act.update(act_changed_detail)
        # copy_act.pop('key')
        # copy_act.pop('remainTickets')
        res = self.cl.post('/api/a/activity/detail', activity_liquid(copy_act))
        res_content = res.content.decode('utf-8')
        self.assertEqual(json.loads(res_content)['code'], 0)
        item = Activity.objects.get(id=act_saved["id"])
        item_to_dict = {
            "id": item.id,
            "key": item.key,
            "name": item.name,
            "place": item.place,
            "description": item.description,
            "start_time": item.start_time,
            "end_time": item.end_time,
            "book_start": item.book_start,
            "book_end": item.book_end,
            "total_tickets": item.total_tickets,
            "status": item.status,
            "pic_url": item.pic_url,
            "remain_tickets": item.remain_tickets
        }
        print(copy_act)
        print(item_to_dict)
        self.assertDictEqual(copy_act, item_to_dict)


"""
class MenuTest(TestCase):
    '''
    Test for API 11
    This is not available on travisCI
    Due to access_token error
    '''
    def setUp(self):
        djangoUser.objects.create_superuser(sys_superuser['username'], sys_superuser['email'], sys_superuser['password'])
        self.cl = Client()
        self.cl.post('/api/a/login', sys_superuser)
        Activity(**act_saved).save()
        Activity(**act_published).save()
        Activity(**act_deleted).save()

    def tearDown(self):
        self.cl.post('/api/a/logout', sys_superuser)
        Activity.objects.all().delete()

    def test_getMenu(self):
        res = self.cl.get('/api/a/activity/menu')
        res_content = res.content.decode('utf-8')
        self.assertEqual(json.loads(res_content)['code'], 0)

    def test_addToMenu(self):
        res = self.cl.post('/api/a/activity/menu', {'activity_ids': [act_saved['id'], act_published['id']]})
        res_content = res.content.decode('utf-8')
        self.assertEqual(json.loads(res_content)['code'], 0)

    def test_deleteInMenu(self):
        res = self.cl.post('/api/a/activity/menu', {'activity_ids': []})
        res_content = res.content.decode('utf-8')
        self.assertEqual(json.loads(res_content)['code'], 0)
"""