from django.shortcuts import render
from django.http import  HttpResponse
# Create your views here.
#методы при переходе на определенную стр

def index(request):
    return render(request, 'main/index.html')

def about(request):
    return render(request, 'main/about.html')