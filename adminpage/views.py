from django.shortcuts import render
from django.conf import settings
import os
import time

# Create your views here.
from codex.baseerror import *
from codex.baseview import APIView
from wechat.models import Activity, Ticket


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
                                           picUrl=self.input['picUrl'],
                                           startTime=self.input['startTime'],
                                           endTime=self.input['endTime'],
                                           bookStart=self.input['bookStart'],
                                           bookEnd=self.input['bookEnd'],
                                           totalTickets=self.input['totalTickets'],
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
            path = os.path.join(settings.IMAGE_PATH, img.name)
            with open(path, 'wb') as img_path:
                for p in img.chunks:
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
            item = Activity.get_by_id(self.input['id'])
            item['currentTime'] = time.time()
            item['bookedTickets'] = item.total_tickets - item.remain_tickets
            item['usedTickets'] = Ticket.objects.filter(activity=item.name, status=Ticket.STATUS_USED)
            return item
        except Exception as e:
            raise MySQLError('Query activity detail failed!')

    def post(self):
        if not self.request.user.is_authenticated():
            raise ValidateError('You need to login first.')
        #  self.check_input('id', 'name', 'place', 'description', 'picUrl',
        #                   'startTime', 'endTime', 'bookStart', 'bookend', 'totalTickets', 'status')
        try:
            activity = Activity.get_by_id(self.input['id'])
            if activity.status == Activity.STATUS_SAVED:
                activity.name = self.input['name']
                activity.place = self.input['place']
            activity.description = self.input['description']
            activity.pic_url = self.input['picUrl']
            current_time = time.time()
            if current_time < activity.end_time:
                activity.start_time = self.input['startTime']
                activity.end_time = self.input['endTime']
            if activity.status is not Activity.STATUS_SAVED:
                activity.book_start = self.input['bookStart']
            if current_time < activity.start_time:
                activity.book_end = self.input['bookend']
            if current_time < activity.book_start:
                activity.total_tickets = self.input['totalTickets']
            if activity.status is not Activity.STATUS_PUBLISHED:
                activity.status = self.input['status']
            activity.save()
        except Exception as e:
            raise MySQLError('Change activity detail failed!')
