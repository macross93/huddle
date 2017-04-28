from django.contrib import admin
from .models import Charity, User, CharityContact, Event

# Register your models here.
admin.site.register(Charity)
admin.site.register(User)
admin.site.register(CharityContact)
admin.site.register(Event)
