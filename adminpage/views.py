from django.shortcuts import render
from codex.baseerror import *
from codex.baseview import APIView
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.utils import timezone
from wechat.models import Activity
from wechat.models import Ticket
from wechat.views import CustomWeChatView
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
        if not self.request.user.is_authenticated():
            raise ValidateError('Has not logged in!')
        else:
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
            activity_to_be_deleted.status = Activity.STATUS_DELETED
            activity_to_be_deleted.save()
        except Activity.DoesNotExist:
            raise ValidateError('The activity to be deleted does not exist.')


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
            path = os.path.join(settings.IMAGE_PATH, img.name)
            with open(path, 'wb') as img_path:
                for p in img.chunks():
                    img_path.write(p)
            url = settings.SITE_DOMAIN + '/img/Upload/' + img.name
            return url
        except Exception as e:
            raise FileError('Failed to upload image.')


class ActivityDetail(APIView):
    """
    API 10
    """

    def get(self):
        if not self.request.user.is_authenticated():
            raise ValidateError('You need to login first.')
        self.check_input('id')
        try:
            activity = Activity.get_by_id(self.input['id'])
            if activity.status == Activity.STATUS_DELETED:
                raise ValidateError('The activity has been deleted.')

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

            start_Time = self.input['startTime'].timestamp()
            end_Time = self.input['endTime'].timestamp()
            book_Start = self.input['bookStart'].timestamp()
            book_End = self.input['bookEnd'].timestamp()
            current_Time = datetime.datetime.now().timestamp()
            # use xxxx_Xxxx to compare time
            if start_Time >= end_Time:
                raise LogicError('Activity end time should be later than activity start time.')
            if book_Start >= book_End:
                raise LogicError('Book end time should be later than book start time.')
            if book_End >= end_Time:
                raise LogicError('Activity end time should be later than book end time.')
            if current_Time > end_Time and activity.start_time != self.input['startTime']:
                raise LogicError('Activity start time can not be changed after the activity ends.')
            if current_Time > end_Time and activity.end_time != self.input['endTime']:
                raise LogicError('Activity end time can not be changed after the activity ends.')
            if activity.status is Activity.STATUS_PUBLISHED and activity.book_start != self.input['bookStart']:
                raise LogicError('Book start time can not be changed after the activity publishes.')
            if current_Time > start_Time and activity.book_end != self.input['bookEnd']:
                raise LogicError('Book end time can not be changed after the activity starts.')
            if current_Time > book_Start and activity.total_tickets != self.input['totalTickets']:
                raise LogicError('Total tickets can not be changed after the book starts.')
            if activity.status is Activity.STATUS_PUBLISHED and activity.status != self.input['status']:
                raise LogicError('Activity status can not be changed after the activity publishes.')
            
            activity.start_time = self.input['startTime']
            activity.end_time = self.input['endTime']
            activity.book_start = self.input['bookStart']
            activity.book_end = self.input['bookEnd']
            activity.total_tickets = self.input['totalTickets']
            activity.status = self.input['status']
            activity.save()
        except Exception as e:
            raise MySQLError('Change activity detail failed!')


class Menu(APIView):

    def get_current_menu_ids(self):
        '''
        Copy From wechat/view.py
        :param
        :return: ids
        '''
        try:
            current_menu = CustomWeChatView.lib.get_wechat_menu()
            existed_buttons = list()
            for btn in current_menu:
                if btn['name'] == '抢票':
                    existed_buttons += btn.get('sub_button', list())
            activity_ids = list()
            for btn in existed_buttons:
                if 'key' in btn:
                    activity_id = btn['key']
                    if activity_id.startswith(CustomWeChatView.event_keys['book_header']):
                        activity_id = activity_id[len(CustomWeChatView.event_keys['book_header']):]
                    if activity_id and activity_id.isdigit():
                        activity_ids.append(int(activity_id))
            return activity_ids
        except Exception as e:
            raise MenuError('Failed to get ids.')

    def get(self):
        if not self.request.user.is_authenticated():
            raise ValidateError('Sorry, you are not logged in.')
        activity_ids = self.get_current_menu_ids()
        try:
            current_activities = Activity.objects.filter(status=Activity.STATUS_PUBLISHED,
                                                         book_end__gt=timezone.now()
                                                        )
        except Exception as e:
            raise MySQLError('Failed to get current activities.')
        try:
            activityList = []
            index = 0
            for activity in current_activities:
                if activity.id in activity_ids:
                    index += 1
                    real_index = index
                else:
                    real_index = 0
                activityList.append({
                        'id': activity.id,
                        'name': activity.name,
                        'menuIndex': real_index
                    })
            return activityList
        except Exception as e:
            raise MenuError('Failed to get menu.')

    def post(self):
        if not self.request.user.is_authenticated():
            raise ValidateError('Sorry, you are not logged in.')
        # self.check_input('id')
        try:
            in_act = self.input
            activities = Activity.objects.filter(id__in=in_act)
            CustomWeChatView.update_menu(activities)

        except Exception as e:
            raise MenuError('Failed to update menu.')


class Checkin(APIView):

    def post(self):
        if not self.request.user.is_authenticated():
            raise ValidateError('You need to login first.')
        try:
            if 'ticket' in self.input:
                ticket = Ticket.get_by_id(self.input['ticket'])
                res = {
                    'ticket': ticket.unique_id,
                    'studentId': ticket.student_id
                }
                return res
            elif 'studentId' in self.input:
                tickets = Ticket.get_by_studentId(self.input['studentId'])

                input_id = self.input['actId']

                for ticket in tickets:
                    if str(ticket.activity.id) == input_id:
                        res = {
                            'ticket': ticket.unique_id,
                            'studentId': ticket.student_id
                        }
                        return res
                raise MySQLError('Find ticket failed!')
            else:
                raise ValidateError('You need to input your ticketId or studentId.')
        except Exception as e:
            raise LogicError('Check ticket failed!')

