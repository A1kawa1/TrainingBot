from django.contrib import admin
from model.models import *


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'username')
    search_fields = ('id',)
    empty_value_display = '-пусто-'


class InfoUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'height', 'gender', 'ideal_weight')
    search_fields = ('user',)
    empty_value_display = '-пусто-'


class TargetUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'activity', 'cur_dci',
                    'cur_weight', 'target_weight')
    search_fields = ('user',)
    empty_value_display = '-пусто-'


class UserDayFoodAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'calories', 'time')
    search_fields = ('user',)
    empty_value_display = '-пусто-'


class MessageAdmin(admin.ModelAdmin):
    list_display = ('mesKey', 'order', 'message')
    search_fields = ('mesKey',)
    ordering = ('mesKey',)
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
admin.site.register(InfoUser, InfoUserAdmin)
admin.site.register(TargetUser, TargetUserAdmin)
admin.site.register(UserDayFood, UserDayFoodAdmin)
admin.site.register(ResultDayDci)
admin.site.register(UserProgram)
admin.site.register(Message, MessageAdmin)
