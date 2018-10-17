from codex.baseerror import *
from codex.baseview import APIView

from wechat.models import User
from wechat.models import Activity
from wechat.models import Ticket

import datetime


class UserBind(APIView):

    def validate_user(self):
        """
        input: self.input['student_id'] and self.input['password']
        raise: ValidateError when validating failed
        """
        self.check_input('openid', 'password')
        user = User.get_by_openid(self.input['openid'])
        if user is not None:
            raise ValidateError('You have already done this.')
        # 貌似暂时不需要实现这玩意了

    def get(self):
        self.check_input('openid')
        return User.get_by_openid(self.input['openid']).student_id

    def post(self):
        self.check_input('openid', 'student_id', 'password')
        user = User.get_by_openid(self.input['openid'])
        self.validate_user()
        user.student_id = self.input['student_id']
        user.save()


class ActivityView(APIView):
    def get(self):
        self.check_input('id')
        item = Activity.get_by_id(self.input['id'])
        if item.status is not Activity.STATUS_PUBLISHED:
            raise ValidateError('This activity is not published yet.')
        else:
            # del item.status
            res_item = {}
            res_item['name'] = item.name
            res_item['key'] = item.key
            res_item['description'] = item.description
            res_item['startTime'] = item.start_time.timestamp()
            res_item['endTime'] = item.end_time.timestamp()
            res_item['place'] = item.place
            res_item['bookStart'] = item.book_start
            res_item['bookEnd'] = item.book_end
            res_item['totalTickets'] = item.total_tickets
            res_item['picUrl'] = item.pic_url
            res_item['remainTickets'] = item.remain_tickets
            res_item['currentTime'] = datetime.datetime.now().timestamp()
            return res_item


class TicketView(APIView):
    def get(self):
        self.check_input('openid', 'ticket')
        user = User.get_by_openid(self.input['openid'])
        student_id = user.student_id
        detail = Ticket.get_a_ticket(student_id, self.input['ticket'])
        detail['currentTime'] = datetime.datetime().now().timestamp()
        return detail
