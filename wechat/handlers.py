# -*- coding: utf-8 -*-
#
from wechat.wrapper import WeChatHandler
from wechat.models import Activity, Ticket
from WeChatTicket import settings
import random
import uuid


__author__ = "Epsirom"


class ErrorHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self):
        return self.reply_text('ErrorHandler，服务器现在有点忙，暂时不能给您答复 T T')


class DefaultHandler(WeChatHandler):

    def check(self):
        return False

    def handle(self):
        print('ErrorHandler-hander')
        return self.reply_text(' DefaultHandler，没有找到您需要的信息:(')


class HelpOrSubscribeHandler(WeChatHandler):

    def check(self):
        return self.is_text('帮助', 'help') or self.is_event('scan', 'subscribe') or \
               self.is_event_click(self.view.event_keys['help'])

    def handle(self):
        return self.reply_single_news({
            'Title': self.get_message('help_title'),
            'Description': self.get_message('help_description'),
            'Url': self.url_help(),
        })


class UnbindOrUnsubscribeHandler(WeChatHandler):

    def check(self):
        return self.is_text('解绑') or self.is_event('unsubscribe')

    def handle(self):
        self.user.student_id = ''
        self.user.save()
        return self.reply_text(self.get_message('unbind_account'))


class BindAccountHandler(WeChatHandler):

    def check(self):
        return self.is_text('绑定') or self.is_event_click(self.view.event_keys['account_bind'])

    def handle(self):
        return self.reply_text(self.get_message('bind_account'))


class BookWhatHandler(WeChatHandler):

    def check(self):
        return self.is_text('抢啥') or self.is_event_click(self.view.event_keys['book_what'])

    def handle(self):
        acts = []
        if not self.user.student_id:
            return self.reply_text(self.get_message('bind_account'))
        act_list = Activity.objects.filter(status=Activity.STATUS_PUBLISHED)
        for item in act_list:
            print(item.id)
            acts.append({
                'Url': settings.get_url('u/activity', {'id': item.id}),
                'Title': '%s' % item.name,
                'Description': item.description,
                'PicUrl': item.pic_url
            })
        return self.reply_news(articles=acts)


class BookTicketHandler(WeChatHandler):

    def createUID(self, openid):
        uid = uuid.uuid4() + openid
        return uid

    def check(self):
        return self.is_text('抢票')

    def handle(self):
        if not self.user.student_id:
            return self.reply_text(self.get_message('bind_account'))
        activity_key = self.input[3:]   # str
        activity_list = Activity.objects.filter(key=activity_key)
        if len(activity_list) == 0:
            return self.reply_text('没有记录！')
        remain_count = activity_list[0].remain_tickets
        if remain_count > 0:
            owned_tickets = Ticket.objects.filter(student_id=self.user.student_id, activity__key=activity_key)
            if len(owned_tickets) > 0:
                return self.reply_text('您已经订过票了。')
            Ticket.objects.create(
                student_id=self.user.student_id,
                unique_id=self.createUID(openid=self.user.open_id),
                activity=activity_list[0],
                status=Ticket.STATUS_VALID
            )
            return self.reply_text('成功！')
        else:
            return self.reply_text('票已抢完。')


class BookEmptyHandler(WeChatHandler):

    def check(self):
        return self.is_event_click(self.view.event_keys['book_empty'])

    def handle(self):
        return self.reply_text(self.get_message('book_empty'))


class GetTicketHandler(WeChatHandler):

    def check(self):
        return self.is_text('查票') or self.is_event_click(self.view.event_keys['get_ticket'])

    def handle(self):
        tickets = []
        if not self.user.student_id:
            return self.reply_text(self.get_message('bind_account'))
        ticket_list = Ticket.get_by_studentId(student_id=self.user.student_id)
        for item in ticket_list:
            print(item.id)
            tickets.append({
                'Url': settings.get_url('/u/ticket', {'id': item.id}),
                'Title': '%s' % item.activity.name,
                'Description': item.activity.description,
                'PicUrl': item.activity.pic_url
            })
        return self.reply_news(articles=tickets)