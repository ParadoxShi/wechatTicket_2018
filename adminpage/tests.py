from django.test import TestCase, Client
from django.contrib.auth.models import User as djangoUser
from django.conf import settings
from wechat.models import *
import json
from datetime import timedelta
from django.utils import timezone
import os
from adminpage.views import *

# Mentions:
# Success code == 0
# Validate Error code == 3


sys_superuser = {
    "username": "superuser",
    "email": '',
    "password": 'password'
}

superUserForTest = {'username': 'administrator',
                    'email': 'benjo@youknowthereisnotthiswebsite.com',
                    'password': 'guest2000'}
wrongUser1 = {
    'username': 'bdripistraitor',
    'email': 'benjo@youknowthereisnotthiswebsite.com',
    'password': 'guest2000'
}
wrongUser2 = {
    'username': 'administrator',
    'email': 'benjo@youknowthereisnotthiswebsite.com',
    'password': 'prisoner9527'
}


## API 4 ##
class LoginTest(TestCase):
    def setUp(self):
        djangoUser.objects.create_superuser(superUserForTest['username'],
                                            superUserForTest['email'],
                                            superUserForTest['password'])

    def test_hasnot_login(self):
        rep = self.client.get('/api/a/login/')
        repObj = json.loads(rep.content.decode('utf-8'))
        self.assertEqual(repObj['code'], 3)

    def test_log_in(self):
        rep = self.client.post('/api/a/login/', superUserForTest)
        self.assertEqual(rep.status_code, 200)
        repObj = json.loads(rep.content.decode('utf-8'))
        self.assertEqual(repObj['code'], 0)

    def test_has_login(self):
        self.client.post('/api/a/login/', superUserForTest)
        rep = self.client.get('/api/a/login/')
        repObj = json.loads(rep.content.decode('utf-8'))
        self.assertEqual(repObj['code'], 0)

    def test_failed_usr(self):
        rep = self.client.post('/api/a/login/', wrongUser1)
        repObj = json.loads(rep.content.decode('utf-8'))
        self.assertEqual(repObj['code'], 3)

    def test_failed_pwd(self):
        rep2 = self.client.post('/api/a/login/', wrongUser2)
        repObj2 = json.loads(rep2.content.decode('utf-8'))
        self.assertEqual(repObj2['code'], 3)

    def tearDown(self):
        pass


## API 5 ##
class LogOutTest(TestCase):
    def setUp(self):
        djangoUser.objects.create_superuser(superUserForTest['username'],
                                            superUserForTest['email'],
                                            superUserForTest['password'])

    def test_log_out(self):
        self.client.post('/api/a/login/', superUserForTest)
        rep = self.client.post('/api/a/logout/', superUserForTest)
        repObj = json.loads(rep.content.decode('utf-8'))
        self.assertEqual(repObj['code'], 0)

    def test_failed_not_logged_in(self):
        rep = self.client.post('/api/a/logout/', superUserForTest)
        repObj = json.loads(rep.content.decode('utf-8'))
        self.assertEqual(repObj['code'], 3)

    def tearDown(self):
        pass


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
               "total_tickets": 1000,
               "status": Activity.STATUS_SAVED,
               "pic_url": "test_url",
               "start_time": timezone.now() + timedelta(1000),
               "end_time": timezone.now() + timedelta(2000),
               "book_start": timezone.now() + timedelta(500),
               "book_end": timezone.now() + timedelta(800),
}


def activity_liquid(act):

    liquid = {
        "id": act['id'],
        "name": act['name'],
        "key": act['key'],
        "place": act['place'],
        "description": act['description'],
        "startTime": act['start_time'],
        "endTime": act['end_time'],
        "bookStart": act['book_start'],
        "bookEnd": act['book_end'],
        "totalTickets": act['total_tickets'],
        "status": act['status'],
        "remainTickets": act['remain_tickets'],
        "picUrl": act["pic_url"]
    }
    return liquid


## API 6 ##
class ActivityListTest(TestCase):
    def setUp(self):
        djangoUser.objects.create_superuser(superUserForTest['username'],
                                            superUserForTest['email'],
                                            superUserForTest['password'])
        Activity(**act_saved).save()
        Activity(**act_published).save()
        Activity(**act_deleted).save()

    def test_get_list(self):
        self.client.post('/api/a/login/', superUserForTest)
        rep = self.client.get('/api/a/activity/list/')
        repObj = json.loads(rep.content.decode('utf-8'))
        self.assertEqual(repObj['code'], 0)
        self.assertEqual(len(repObj['data']), 2)

    def test_failed_not_logged_in(self):
        rep = self.client.get('/api/a/activity/list/')
        repObj = json.loads(rep.content.decode('utf-8'))
        self.assertEqual(repObj['code'], 3)

    def tearDown(self):
        pass


## API 7 ##
class ActivityDeleteTest(TestCase):
    def setUp(self):
        djangoUser.objects.create_superuser(superUserForTest['username'],
                                            superUserForTest['email'],
                                            superUserForTest['password'])
        Activity(**act_saved).save()
        Activity(**act_published).save()
        Activity(**act_deleted).save()

    def test_del_activity(self):
        self.client.post('/api/a/login/', superUserForTest)
        rep = self.client.post('/api/a/activity/delete/', {'id': act_saved['id']})
        repObj = json.loads(rep.content.decode('utf-8'))
        self.assertEqual(repObj['code'], 0)

    def tearDown(self):
        pass


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


"""
class MenuTest(TestCase):
    '''
    Test for API 11
    This is not available on travisCI due to access_token error,
    I tried it on my PC and it worked!
    If you wish to test this, just cancel the comment and then open terminal and type 'python manage.py test'.
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

    def test_postMenu(self):
        res = self.cl.post('/api/a/activity/menu', {act_saved['id']: act_saved['id'], act_published['id']: act_published['id']})
        res_content = res.content.decode('utf-8')
        self.assertEqual(json.loads(res_content)['code'], 0)
"""

ticket_valid = {
    "open_id": '0003',
    "student_id": '2016010101',
    "unique_id": 'RDWS',
    "status": Ticket.STATUS_VALID
}


class checkInTest(TestCase):
    """
    Test For API 12
    """
    def setUp(self):
        djangoUser.objects.create_superuser(sys_superuser['username'], sys_superuser['email'],
                                            sys_superuser['password'])
        Activity(**act_published).save()
        User.objects.create(open_id=ticket_valid['open_id'], student_id=ticket_valid['student_id'])
        Ticket.objects.create(
            student_id=ticket_valid['student_id'],
            unique_id=ticket_valid['unique_id'],
            activity=Activity.objects.get(id=act_published['id']),
            status=Ticket.STATUS_VALID
        )
        self.cl = Client()
        self.cl.post('/api/a/login', sys_superuser)

    def tearDown(self):
        User.objects.all().delete()
        Ticket.objects.all().delete()
        Activity.objects.all().delete()
        self.cl.post('/api/a/logout', sys_superuser)

    def test_checkIn(self):
        res = self.cl.post('/api/a/activity/checkin', {'actId': act_published['id'], 'ticket': ticket_valid['unique_id']})
        res_content = res.content.decode('utf-8')
        self.assertEqual(json.loads(res_content)['code'], 0)
        self.assertEqual(json.loads(res_content)['data']['studentId'], ticket_valid['student_id'])
        # try to check in with activity id and ticket id

    def test_checkIn_2(self):
        res = self.cl.post('/api/a/activity/checkin', {'actId': act_published['id'], 'studentId': ticket_valid['student_id']})
        res_content = res.content.decode('utf-8')
        self.assertEqual(json.loads(res_content)['code'], 0)
        self.assertEqual(json.loads(res_content)['data']['ticket'], ticket_valid['unique_id'])
        # try to check in with activity id and student id

    def test_checkIn_3(self):
        res = self.cl.post('/api/a/activity/checkin', {'actId': act_published['id'], 'ticket': '', 'studentId': ''})
        res_content = res.content.decode('utf-8')
        self.assertNotEqual(json.loads(res_content)['code'], 0)
        # try to check in only with activity id

    def test_checkIn_4(self):
        res = self.cl.post('/api/a/activity/checkin', {'actId': -1, 'ticket': '', 'studentId': ticket_valid['student_id']})
        res_content = res.content.decode('utf-8')
        self.assertNotEqual(json.loads(res_content)['code'], 0)
        # try to check in with non-existent activity id and ticket id