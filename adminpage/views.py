from django.shortcuts import render
from codex.baseerror import *
from codex.baseview import APIView
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from wechat.models import Activity
import datetime


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
            activity_to_be_deleted = Activity.objects.filter(id=self.input['id'])
        except Activity.DoesNotExist:
            raise ValidateError('The activity to be deleted does not exist.')
        activity_to_be_deleted.status = Activity.STATUS_DELETED
        activity_to_be_deleted.save()

