from django.test import TestCase, Client
from wechat.models import Activity, User
import datetime
import xml.etree.ElementTree as etree


test_open_id = '0247'
test_student_id = '2016013247'

test_xml_str = """
<xml>
    <ToUserName><![CDATA[user]]></ToUserName>
    <FromUserName><![CDATA[%s]]></FromUserName>
    <CreateTime>1348831860</CreateTime>
    <MsgType>text</MsgType>
    <MsgId>1293081923923912</MsgId>
    <Content><![CDATA[%s]]></Content>
</xml>
"""

act_published = Activity(id=5,
                         name='act1',
                         key='key1',
                         place='Hall',
                         description='published act',
                         start_time=datetime.datetime().now(),
                         end_time=datetime.datetime().now(),
                         book_start=datetime.datetime.now(),
                         book_end=datetime.datetime().now(),
                         total_tickets=1000,
                         status=Activity.STATUS_PUBLISHED,
                         remain_tickets=1000
                        )


class BookTicketCase(TestCase):

    def setUp(self):
        User(open_id=test_open_id, student_id=test_student_id).save()
        self.cl = Client()
        act_published.save()
        self.send_package = test_xml_str % (test_open_id, '抢票 key1')

    def tearDown(self):
        User.objects.get(open_id=test_open_id).delete()
        Activity.objects.get(id=5).delete()

    def test_book(self):
        res = self.cl.post('/wechat', self.send_package, content_type='application/xml')
        res_str = res.content.decode('utf-8')
        root = etree.fromstring(res_str)
        self.assertEqual(root.find('Content').text, '成功！')
