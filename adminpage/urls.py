# -*- coding: utf-8 -*-
#
from django.conf.urls import url

from adminpage.views import *


__author__ = "caijc16"


urlpatterns = [
    url(r'^login/?$', Login.as_view()),
    url(r'^logout/?$', LogOut.as_view()),
    url(r'^activity/list/?$', ActivityList.as_view()),
    url(r'^activity/delete/?$', ActivityDelete.as_view()),

]
