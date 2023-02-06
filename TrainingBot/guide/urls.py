from django.urls import path
from guide.views import guide, send_form


app_name = 'guide'
urlpatterns = [
    path('<int:id>/', guide, name='guide'),
    path('send_form/', send_form, name='send_form')
]
