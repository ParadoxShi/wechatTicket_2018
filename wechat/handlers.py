# -*- coding: utf-8 -*-
#
from wechat.wrapper import WeChatHandler
from wechat.models import Activity, Ticket
from WeChatTicket import settings
from django.db import transaction
import time
import uuid


__author__ = "Epsirom"


class ErrorHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self):
        return self.reply_text('对不起，服务器现在有点忙，暂时不能给您答复 T T')


class DefaultHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self):
        return self.reply_text('对不起，没有找到您需要的信息:(')


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
            acts.append({
                'Url': settings.get_url('u/activity', {'id': item.id}),
                'Title': '%s' % item.name,
                'Description': item.description,
                'PicUrl': item.pic_url
            })
        return self.reply_news(articles=acts)


class BookTicketHandler(WeChatHandler):

    def createUID(self, openid):
        uid = str(uuid.uuid4()) + openid
        return uid

    def check(self):
        flag = False
        if self.is_text_command('抢票'):
            self.entry_type = 1
            flag = True
        elif self.is_msg_type('event') and (self.input['Event'] == 'CLICK')\
                and (self.input['EventKey'].startswith(self.view.event_keys['book_header'])):
            self.entry_type = 2
            flag = True
        return flag

    def handle(self):
        if not self.user.student_id:
            return self.reply_text(self.get_message('bind_account'))
        activity = None
        if self.entry_type == 1:
            activity_key = self.input['Content'][3:]
            activity = Activity.objects.get(key=activity_key)
        elif self.entry_type == 2:
            activity_id = self.input['EventKey'][len(self.view.event_keys['book_header']):]
            activity = Activity.objects.get(id=activity_id)
            activity_key = activity.key

        if activity is None:
            return self.reply_text('没有记录！')
        startTime = int(time.mktime(activity.book_start.timetuple()))
        endTime = int(time.mktime(activity.book_end.timetuple()))
        currentTime = int(time.time())
        if currentTime < startTime:
            return self.reply_text('抢票尚未开始！')
        if currentTime > endTime:
            return self.reply_text('抢票已经结束！')
        remain_count = activity.remain_tickets
        if remain_count > 0:
            owned_tickets = Ticket.objects.filter(student_id=self.user.student_id, activity__key=activity_key)
            for ticket in owned_tickets:
                if ticket.status != Ticket.STATUS_CANCELLED:
                    return self.reply_text('您已经订过票了！')
            with transaction.atomic():
                try:
                    Ticket.objects.create(
                        student_id=self.user.student_id,
                        unique_id=self.createUID(openid=self.user.open_id),
                        activity=activity,
                        status=Ticket.STATUS_VALID
                    )
                    activity.remain_tickets -= 1
                    activity.save()
                    return self.reply_text('成功！')
                except Exception as e:
                    return self.reply_text('失败！')

        else:
            return self.reply_text('票已抢完！')


class BookEmptyHandler(WeChatHandler):

    def check(self):
        return self.is_event_click(self.view.event_keys['book_empty'])

    def handle(self):
        return self.reply_text(self.get_message('book_empty'))


class GetTicketHandler(WeChatHandler):
    def check(self):
        return self.is_text('查票') or self.is_event_click(self.view.event_keys['get_ticket'])

    def handle(self):
        if not self.user.student_id:
            return self.reply_text(self.get_message('bind_account'))
        tickets = []
        this_user = self.user
        ticket_list = Ticket.get_by_studentId(student_id=this_user.student_id)
        if len(ticket_list) == 0:
            return self.reply_text('您还没有订票！')
        for ticket in ticket_list:
            tickets.append({
                'Url': settings.get_url('/u/ticket', {'openid': this_user.open_id, 'ticket': ticket.unique_id}),
                'Title': '%s' % ticket.activity.name,
                'Description': ticket.activity.description,
                'PicUrl': ticket.activity.pic_url
            })
        return self.reply_news(articles=tickets)


class TakeTicketHandler(WeChatHandler):
    def check(self):
        return self.is_text_command('取票')

    def handle(self):
        if not self.user.student_id:
            return self.reply_text(self.get_message('bind_account'))
        this_user = self.user
        activity_key = self.input['Content'][3:]
        owned_tickets = Ticket.objects.filter(student_id=this_user.student_id, activity__key=activity_key)
        if len(owned_tickets) == 0:
            return self.reply_text('您还没有订票！')

        ticket = owned_tickets[0]
        if ticket.status == Ticket.STATUS_CANCELLED:
            return self.reply_text('您已把这张票退了！')

        tickets = []
        for ticket in owned_tickets:
            tickets.append({
                'Url': settings.get_url('/u/ticket', {'openid': this_user.open_id, 'ticket': ticket.unique_id}),
                'Title': '%s' % ticket.activity.name,
                'Description': ticket.activity.description,
                'PicUrl': ticket.activity.pic_url
            })
        return self.reply_news(articles=tickets)


class WithdrawTicketHandler(WeChatHandler):
    def check(self):
        return self.is_text_command('退票')

    def handle(self):
        if not self.user.student_id:
            return self.reply_text(self.get_message('bind_account'))
        this_user = self.user
        activity_key = self.input['Content'][3:]
        owned_tickets = Ticket.objects.filter(student_id=this_user.student_id, activity__key=activity_key)
        if len(owned_tickets) == 0:
            return self.reply_text('您还没有订票！')
        for ticket in owned_tickets:
            if ticket.status == Ticket.STATUS_USED:
                return self.reply_text('您已检票了！')
            elif ticket.status == Ticket.STATUS_VALID:
                try:
                    activities = Activity.objects.get(key=activity_key)
                    ticket.status = Ticket.STATUS_CANCELLED
                    ticket.save()
                    activities.remain_tickets += 1
                    activities.save()
                    return self.reply_text('退票成功！')
                except Exception as e:
                    return self.reply_text('失败，请重试！')

        return self.reply_text('您已退过票了！')
