from django.contrib import admin
from eventowl.models import UserProfile, VisitorLocation


class MoreItemsAdmin(admin.ModelAdmin):
    list_per_page = 500


admin.site.register(UserProfile, MoreItemsAdmin)
admin.site.register(VisitorLocation, MoreItemsAdmin)