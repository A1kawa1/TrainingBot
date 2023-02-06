from django.shortcuts import render
from django.http import HttpResponse


def guide(request, id):
    return render(request, 'guide_main.html')


def send_form(request):
    print('-------------')
    return HttpResponse("Вы успешно отправили форму")