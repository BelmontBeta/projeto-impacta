from django import forms

from .models import Feedback


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback

        fields = ['nome', 'email', 'assunto', 'mensagem']

        labels = {
            'nome': 'Nome',
            'email': 'E-mail',
            'assunto': 'Assunto',
            'mensagem': 'Mensagem ou feedback',
        }

        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Digite seu nome'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Digite seu e-mail'}),
            'assunto': forms.TextInput(attrs={'placeholder': 'Digite o assunto'}),
            'mensagem': forms.Textarea(attrs={'placeholder': 'Digite sua mensagem ou feedback', 'rows': 6}),
        }