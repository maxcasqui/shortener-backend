from django.contrib import admin

from api.models import URL, AppUser

# Register your models here.
admin.site.register(AppUser)
admin.site.register(URL)