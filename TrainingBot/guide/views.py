from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from model.form import GuideForm
from model.models import User


def guide(request, id, guid):
    print('test')
    user = User.objects.filter(
        id=id,
        guid=guid
    )
    if not user.exists():
        return redirect('guide:bad_request')
    form = GuideForm()
    print('-----------')
    print(request.method)
    if request.method == 'POST':
        form = GuideForm(request.POST)
        if form.is_valid():
            return redirect('guide:success')
            #now in the object cd, you have the form as a dictionary.
        # else:
        #     response = {}
        #     for k in form.errors:
        #         response[k] = form.errors[k][0]
        #     print(response)
    context = {
        'form': form
    }
    return render(request, 'guide_main.html', context)


def send_form(request):
    print('-------------')
    return HttpResponse("Вы успешно отправили форму")