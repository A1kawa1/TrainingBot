from django import forms
from model.models import Guide
from django.core.exceptions import ValidationError


class GuideForm(forms.Form):
    def __init__(self, *args, **kwargs):
        question = Guide.objects.all()
        super().__init__(*args, **kwargs)
        for i in range(len(question)):
            field_name = f'answer{i+1}'
            lable = question[i].question
            help_text = question[i].advice
            if help_text != '':
                self.fields[field_name] = forms.IntegerField(
                    required=True,
                    label=lable,
                    help_text=help_text,
                    widget=forms.NumberInput(attrs={'style': 'width:20ch'})
                )
            else:
                self.fields[field_name] = forms.IntegerField(
                    required=True,
                    label=lable,
                    widget=forms.NumberInput(attrs={'style': 'width:20ch'})
                )

    def clean(self):
        question = Guide.objects.all()
        data = self.cleaned_data
        for i in range(len(question)):
            field_name = f'answer{i+1}'
            if not (question[i].answer1 <= data.get(field_name) <= question[i].answer2):
                raise ValidationError('Неверный ответ')
        return data
