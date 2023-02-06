from django import forms
from bot.models import Guide
from django.core.exceptions import ValidationError


class GuideForm(forms.Form):
    def __init__(self, *args, **kwargs):
        question = Guide.objects.all()
        super().__init__(*args, **kwargs)
        for i in range(len(question)):
            field_name = f'answer{i+1}'
            lable = question[i].question
            self.fields[field_name] = forms.IntegerField(
                required=True,
                label=lable
            )

    def clean(self):
        question = Guide.objects.all()
        data = self.cleaned_data
        for i in range(len(question)):
            field_name = f'answer{i+1}'
            print(field_name, data.get(field_name), question[i].answer1, question[i].answer2)
            if not (question[i].answer1 <= data.get(field_name) <= question[i].answer2):
                raise ValidationError('Неверный ответ')
        return data
        