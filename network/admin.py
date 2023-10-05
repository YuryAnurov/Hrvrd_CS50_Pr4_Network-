from django.contrib import admin
from .models import Post, User


class UserAdmin(admin.ModelAdmin):
    filter_horizontal = ['follows']  # в лекции был тюпл ('follows', ) - но не прошло


class PostAdmin(admin.ModelAdmin):
    filter_horizontal = ['liked']


admin.site.register(Post, PostAdmin)
admin.site.register(User, UserAdmin)
