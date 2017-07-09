"""djangohuddle URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from djangohuddle.views import webhook, signup, thanks, simple_upload, event_form_upload, model_form_upload, home, eventList, userList, charityList, charitycontactList
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^admin/', admin.site.urls),
    url(r'^$', home),
    url(r'^webhook/$', webhook),
    url(r'^signup/$', signup, name='signup'),
    url(r'^home/$', home),
    url(r'^thanks/$', thanks),
    url(r'^events/$', eventList.as_view()),
    url(r'^users/$', userList.as_view()),
    url(r'^charity/$', charityList.as_view()),
    url(r'^charitycontact/$', charitycontactList.as_view()),
    url(r'^simple_upload/$', simple_upload),
    url(r'^model_form_upload/$', model_form_upload),
    url(r'^add_event/$', event_form_upload),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
