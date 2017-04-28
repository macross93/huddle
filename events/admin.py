from django.contrib import admin
from .models import charity, user, charitycontact, event

# Register your models here.
admin.site.register(charity)
admin.site.register(user)
admin.site.register(charitycontact)
admin.site.register(event)
