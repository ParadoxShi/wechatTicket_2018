# -*- coding: utf-8 -*-
#
from django.conf.urls import url

from adminpage.views import *


__author__ = "caijc16 and shis16"


urlpatterns = [
    url(r'^login/?$', Login.as_view()),
    url(r'^logout/?$', LogOut.as_view()),
    url(r'^activity/list/?$', ActivityList.as_view()),
    url(r'^activity/delete/?$', ActivityDelete.as_view()),
    url(r'^activity/create$', ActivityCreate.as_view()),
    url(r'^image/upload/?$', ImageUpload.as_view()),
    url(r'^activity/detail/?$', ActivityDetail.as_view()),
    url(r'^activity/menu/?$', WechatTicketMenu.as_view()),
    url(r'^activity/checkin/?$', CheckTicket.as_view())
]
