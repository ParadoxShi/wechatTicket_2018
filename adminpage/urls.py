# -*- coding: utf-8 -*-
#
from django.conf.urls import url

from adminpage.views import *


__author__ = "ParadoxShi"


urlpatterns = [
    url(r'^activity/create$', ActivityCreate.as_view()),
    url(r'^image/upload/?$', ImageUpload.as_view()),
]
