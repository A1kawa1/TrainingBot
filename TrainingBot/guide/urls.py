from django.urls import path
from django.views.generic import TemplateView
from guide.views import guide


app_name = 'guide'
urlpatterns = [
    path('<int:id>/<str:guid>/', guide, name='guide'),
    path(
        'success/',
        TemplateView.as_view(template_name='success.html'),
        name='success'
    ),
    path(
        'bad_request/',
        TemplateView.as_view(template_name='bad_request.html'),
        name='bad_request'
    )
]
