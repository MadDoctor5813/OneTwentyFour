"""
Definition of urls for OneTwentyFourWeb.
"""

from datetime import datetime
from django.conf.urls import url
import django.contrib.auth.views

import app.forms
import app.views

from django.conf.urls import include
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    # Examples:
    url(r'^$', app.views.main, name='home'),
    url(r'^api/get_riding_data/(?P<riding_id>\d+)/', app.views.get_riding_data),

    url(r'^admin/', include(admin.site.urls)),
]
