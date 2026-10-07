from django.shortcuts import render

def boas_vindas(request):
    return render(request, "guardiao/boas_vindas.html")