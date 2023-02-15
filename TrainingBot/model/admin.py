from django.contrib import admin
from model.models import *


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'username')
    search_fields = ('id',)
    empty_value_display = '-пусто-'


class GuideAdmin(admin.ModelAdmin):
    list_display = ('id', 'advice', 'question', 'answer1', 'answer2')
    search_fields = ('advice',)
    empty_value_display = '-пусто-'


class InfoUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'height', 'gender', 'ideal_weight')
    search_fields = ('user',)
    empty_value_display = '-пусто-'


class TargetUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'activity', 'period', 'cur_dci', 'cur_weight', 'target_weight')
    search_fields = ('user',)
    empty_value_display = '-пусто-'


class UserStageGuideAdmin(admin.ModelAdmin):
    list_display = ('user', 'stage', 'question')
    search_fields = ('user',)
    empty_value_display = '-пусто-'


class FoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'calories')
    search_fields = ('name',)
    empty_value_display = '-пусто-'


class UserFoodAdmin(admin.ModelAdmin):
    list_display = ('food', 'user')
    search_fields = ('user',)
    empty_value_display = '-пусто-'


class UserDayFoodAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'calories', 'time')
    search_fields = ('user',)
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
admin.site.register(InfoUser, InfoUserAdmin)
admin.site.register(TargetUser, TargetUserAdmin)
admin.site.register(UserStageGuide, UserStageGuideAdmin)
admin.site.register(Food, FoodAdmin)
admin.site.register(UserFood, UserFoodAdmin)
admin.site.register(Guide, GuideAdmin)
admin.site.register(UserDayFood, UserDayFoodAdmin)
