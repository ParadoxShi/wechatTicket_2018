from django.shortcuts import render
from codex.baseerror import *
from codex.baseview import APIView
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from wechat.models import Activity
from wechat.models import Ticket
import datetime
from django.conf import settings
import os
import time


class Login(APIView):

    def get(self):
        if not self.request.user.is_authenticated():
            raise ValidateError('Has not logged in!')

    def post(self):
        self.check_input('username', 'password')
        user = auth.authenticate(username=self.input['username'], password=self.input['password'])
        if user is not None:
            if user.is_active:
                auth.login(self.request, user)
                return
        raise ValidateError('Oops, login failed.....')


class LogOut(APIView):

    def post(self):
        try:
            auth.logout(self.request)
        except Exception:
            raise ValidateError('Log out failed?!')


class ActivityList(APIView):

    def get(self):
        if self.request.user.is_authenticated():
            activities = Activity.objects.all()
            activityList = []
            for activity in activities:
                if activity.status >= 0:
                    activityObj = {
                        'id': activity.id,
                        'name': activity.name,
                        'description': activity.description,
                        'startTime': activity.start_time.timestamp(),
                        'endTime': activity.end_time.timestamp(),
                        'place': activity.place,
                        'bookStart': activity.book_start.timestamp(),
                        'bookEnd': activity.book_end.timestamp(),
                        'currentTime': datetime.datetime.now().timestamp()
                    }
                    if activity.status == Activity.STATUS_PUBLISHED:
                        activityObj['status'] = 1
                    else:
                        activityObj['status'] = 0
                    activityList.append(activityObj)
            return activityList
        else:
            raise ValidateError('Sorry, you are not logged in.')


class ActivityDelete(APIView):

    def post(self):
        self.check_input('id')
        try:
            activity_to_be_deleted = Activity.objects.get(id=self.input['id'])
        except Activity.DoesNotExist:
            raise ValidateError('The activity to be deleted does not exist.')
        activity_to_be_deleted.status = Activity.STATUS_DELETED
        activity_to_be_deleted.save()


class ActivityCreate(APIView):
    def post(self):
        if not self.request.user.is_authenticated():
            raise ValidateError('You need to login first.')
        self.check_input('name', 'key', 'place', 'description', 'picUrl', 'startTime', 'endTime', 'bookStart', 'bookEnd', 'totalTickets', 'status')
        try:
            item = Activity.objects.create(name=self.input['name'],
                                           key=self.input['key'],
                                           place=self.input['place'],
                                           description=self.input['name'],
                                           pic_url=self.input['picUrl'],
                                           start_time=self.input['startTime'],
                                           end_time=self.input['endTime'],
                                           book_start=self.input['bookStart'],
                                           book_end=self.input['bookEnd'],
                                           total_tickets=self.input['totalTickets'],
                                           remain_tickets=self.input['totalTickets'],
                                           status=self.input['status']
                                          )
            return item.id
        except Exception as e:
            raise MySQLError('Create activity failed!')


class ImageUpload(APIView):
    def post(self):
        if not self.request.user.is_authenticated():
            raise ValidateError('You need to login first.')
        self.check_input('image')
        try:
            img = self.input['image'][0]
            print(img)
            path = os.path.join(settings.IMAGE_PATH, img.name)
            with open(path, 'wb') as img_path:
                for p in img.chunks():
                    img_path.write(p)
            url = settings.SITE_DOMAIN + '/img/Upload/' + img.name
            return url
        except Exception as e:
            raise FileError('Failed tp upload image.')


class ActivityDetail(APIView):

    def get(self):
        if not self.request.user.is_authenticated():
            raise ValidateError('You need to login first.')
        self.check_input('id')
        try:
            activity = Activity.get_by_id(self.input['id'])
            item = {}

            item['name'] = activity.name
            item['key'] = activity.key
            item['description'] = activity.description
            item['startTime'] = activity.start_time.timestamp()
            item['endTime'] = activity.end_time.timestamp()
            item['place'] = activity.place
            item['bookStart'] = activity.book_start.timestamp()
            item['bookEnd'] = activity.book_end.timestamp()
            item['totalTickets'] = activity.total_tickets
            if activity.status == Activity.STATUS_PUBLISHED:
                item['status'] = 1
            else:
                item['status'] = 0
            item['picUrl'] = activity.pic_url

            item['currentTime'] = datetime.datetime.now().timestamp()
            item['bookedTickets'] = activity.total_tickets - activity.remain_tickets
            item['usedTickets'] = Ticket.objects.filter(activity_id=activity.id, status=Ticket.STATUS_USED).count()
            return item
        except Exception as e:
            raise MySQLError('Query activity detail failed!')

    def post(self):
        if not self.request.user.is_authenticated():
            raise ValidateError('You need to login first.')
        #  self.check_input('id', 'name', 'place', 'description', 'picUrl',
        #                   'startTime', 'endTime', 'bookStart', 'bookEnd', 'totalTickets', 'status')
        try:
            activity = Activity.get_by_id(self.input['id'])
            if activity.status == Activity.STATUS_SAVED:
                activity.name = self.input['name']
                activity.place = self.input['place']
            activity.description = self.input['description']
            activity.pic_url = self.input['picUrl']
            current_time = datetime.datetime.now().timestamp()

            # 这一段的顺序比较重要，牵涉到数据库date对象和str对象的转换

            if current_time < activity.start_time.timestamp():
                activity.book_end = self.input['bookEnd']

            if current_time < activity.end_time.timestamp():
                activity.start_time = self.input['startTime']
                activity.end_time = self.input['endTime']

            if current_time < activity.book_start.timestamp():
                activity.total_tickets = self.input['totalTickets']

            if activity.status is not Activity.STATUS_SAVED:
                activity.book_start = self.input['bookStart']

            if activity.status is not Activity.STATUS_PUBLISHED:
                activity.status = self.input['status']
            activity.save()
        except Exception as e:
            raise MySQLError('Change activity detail failed!')
