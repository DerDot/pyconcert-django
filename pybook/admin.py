from django.contrib import admin

from pybook.models import Author, Book, Preview

admin.site.register(Author)
admin.site.register(Book)
admin.site.register(Preview)