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
    ordering = ('-time',)
    empty_value_display = '-пусто-'


class MessageAdmin(admin.ModelAdmin):
    list_display = ('mesKey', 'order', 'message')
    search_fields = ('mesKey',)
    ordering = ('mesKey',)
    empty_value_display = '-пусто-'


class ResultDayDciAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'calories', 'deficit', 'cur_weight')
    search_fields = ('user',)
    ordering = ('-date',)
    empty_value_display = '-пусто-'


class UserProgramAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_start', 'start_dci', 'cur_dci', 'phase1',
                    'phase2', 'cur_day', 'cur_weight', 'achievement')
    search_fields = ('user',)
    empty_value_display = '-пусто-'


class RemindUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'remind_first', 'remind_second')
    search_fields = ('user',)
    ordering = ('user',)
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
admin.site.register(InfoUser, InfoUserAdmin)
admin.site.register(TargetUser, TargetUserAdmin)
admin.site.register(UserDayFood, UserDayFoodAdmin)
admin.site.register(ResultDayDci, ResultDayDciAdmin)
admin.site.register(UserProgram, UserProgramAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(RemindUser, RemindUserAdmin)
admin.site.register(UserStageGuide)
