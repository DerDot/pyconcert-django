from django.contrib import admin

from bookowl.models import Author, Book, Preview
from eventowl.admin import MoreItemsAdmin


@admin.register(Book)
class RecordAdmin(MoreItemsAdmin):
    list_display = ('title', 'date')


admin.site.register(Author)
admin.site.register(Preview)