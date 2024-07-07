from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required

def home(request):
    if request.method == 'POST':
        login_form = AuthenticationForm(request, data=request.POST)
        if login_form.is_valid():
            user = login_form.get_user()
            login(request, user)
            return redirect('home')
    else:
        login_form = AuthenticationForm()

    context = {
        'login_form': login_form,
        'is_logged_in': request.user.is_authenticated,
    }
    return render(request, 'CuracaoArchive/home.html', context)

def knowledge(request):
    return render(request, 'CuracaoArchive/knowledge.html')

def education(request):
    return render(request, 'CuracaoArchive/education.html')

def technology(request):
    return render(request, 'CuracaoArchive/technology.html')

def guidance(request):
    return render(request, 'CuracaoArchive/guidance.html')

def information(request):
    return render(request, 'CuracaoArchive/information.html')

def sponsors(request):
    return render(request, 'CuracaoArchive/sponsors.html')

def splikami_online(request):
    return render(request, 'CuracaoArchive/splikami_online.html')

def contact(request):
    return render(request, 'CuracaoArchive/contact.html')

