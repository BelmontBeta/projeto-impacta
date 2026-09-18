from django.shortcuts import render


def home(request):
    return render(request, 'core/home.html')


def sobre(request):
    return render(request, 'core/sobre.html')


def desafios(request):
    return render(request, 'core/desafios.html')


def equipe(request):
    return render(request, 'core/equipe.html')