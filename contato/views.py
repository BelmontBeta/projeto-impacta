from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import FeedbackForm


def contato(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Obrigado! Sua mensagem foi enviada com sucesso.'
            )

            return redirect('contato')

    else:
        form = FeedbackForm()

    return render(
        request,
        'contato/contato.html',
        {
            'form': form,
        }
    )