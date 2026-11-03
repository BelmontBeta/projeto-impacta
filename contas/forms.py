from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm

User = get_user_model()


class PerfilForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name"]
        labels = {
            "first_name": "Nome",
        }
        widgets = {
            "first_name": forms.TextInput(attrs={
                "autocomplete": "name",
                "maxlength": "150",
            }),
        }

    def clean_first_name(self):
        nome = self.cleaned_data["first_name"].strip()

        if not nome:
            raise forms.ValidationError("Informe seu nome.")

        return nome


class AlterarSenhaForm(PasswordChangeForm):
    pass