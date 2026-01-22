from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from .models import *





# Create your views here.
def index(request):
    return render(request,'index.html')

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # OWNER (STAFF)
            if user.is_staff:
                return redirect(owner_dashboard)

            # NORMAL USER
            return redirect(index)

        else:
            return render(request, 'login.html', {
                'error': 'Invalid username or password'
            })

    return render(request, 'login.html')

def register_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        cnf_password = request.POST['cnf_password']
        role = request.POST.get('role', 'user')  # NEW

        if password != cnf_password:
            return render(request, 'register.html', {
                'error': 'Passwords do not match'
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # OWNER → STAFF
        if role == 'owner':
            user.is_staff = True
            user.save()

        return redirect(login_user)

    return render(request, 'register.html')

def logout_user(request):
    logout(request)
    return redirect(login_user)



def owner_dashboard(request):
    return render(request,'owner_dashboard.html')