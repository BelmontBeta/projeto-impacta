from django import forms

from .models import DicaMeta, MetaEquipe, Registro, Sugestao


class RegistroForm(forms.ModelForm):
    class Meta:
        model = Registro
        fields = ['tipo', 'quantidade', 'data', 'observacao']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def clean_quantidade(self):
        valor = self.cleaned_data['quantidade']
        if valor <= 0:
            raise forms.ValidationError('A quantidade precisa ser maior que zero.')
        return valor


class SugestaoForm(forms.ModelForm):
    class Meta:
        model = Sugestao
        fields = ['texto']
        widgets = {
            'texto': forms.TextInput(attrs={'placeholder': 'Escreva sua sugestão'}),
        }

class MetaEquipeForm(forms.ModelForm):
    class Meta:
        model = MetaEquipe
        fields = ['titulo', 'prazo']
        widgets = {
            'titulo': forms.TextInput(attrs={'placeholder': 'Ex.: Reduzir 10% do desperdício no mês'}),
            'prazo': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }


class DicaMetaForm(forms.ModelForm):
    class Meta:
        model = DicaMeta
        fields = ['texto']