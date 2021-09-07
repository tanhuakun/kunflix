from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from .models import Applications, Invites, RegisterAttempts, ForgetPassword
from axes.helpers import get_client_ip_address
from datetime import datetime, timezone
from django.contrib.auth.decorators import login_required, user_passes_test
import string
import random
from django.contrib.auth.models import User
from .tasks import forget_password_email



def start(request):
    return render(request, 'mylogin/frontpage_start.html')

def loginpage(request):
    if request.user.is_authenticated:
        return redirect('home_page')
    return render(request, 'mylogin/frontpage_login.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('home_page')
    return render(request, 'mylogin/frontpage_register.html')

def apply(request):
    return render(request, 'mylogin/frontpage_apply.html')

@require_http_methods(['POST'])
def check_login(request):
    data = request.POST.copy()
    username = data.get('Username')
    password = data.get('Password')
    user = authenticate(request = request, username=username, password=password)
    if user is not None:
        login(request, user)
        response = HttpResponse(reverse('home_page'), status = 200)
    else:
        response = HttpResponse("Invalid username or password!<br>You only have 6 attempts total before locked out.", status = 403)
    return response


@require_http_methods(['POST'])
def check_apply(request):
    data = request.POST.copy()
    name = data.get('Name')
    email = data.get('Email')

    if len(name) == 0 or len(email) == 0:
        return HttpResponse('Please enter a valid name and email...', status =403)

    reqIP = get_client_ip_address(request)
    reqIPobj = Applications.objects.filter(ip_address=reqIP)

    if reqIPobj is not None:
        counter = 0
        for q in reqIPobj:
            if (datetime.now(timezone.utc) - q.date).total_seconds() / (60 * 60) < 168:
                counter += 1
        if counter > 4:
            return HttpResponse('You have applied too many times. Please contact the site owner for more information.', status =  403)

    try:
        Applications.objects.get(email=email)
        return HttpResponse("That email is in use!", status =403)
    except Applications.DoesNotExist:
        application = Applications(name=name, email=email, ip_address=reqIP)
        application.save()
    
    return HttpResponse(reverse('applied'), status = 200)

@require_http_methods(['POST'])
def check_register(request):
    data = request.POST.copy()
    username = data.get('Username')
    password = data.get('Password')
    password2 = data.get('Password2')
    invcode = data.get('InvCode')
    if len(username) < 4 or len(password) < 4:
        return HttpResponse('Please ensure username and password is more than 3 characters.', status =403)
    if password2 != password:
        return HttpResponse('Both passwords do not match!', status = 403)
    
    reqIP = get_client_ip_address(request)
    reqIPobj = RegisterAttempts.objects.filter(ip_address=reqIP)

    if reqIPobj is not None:
        counter = 0
        for q in reqIPobj:
            if (datetime.now(timezone.utc) - q.date).total_seconds() / (60 * 60) < 168:
                counter += 1
        if counter > 4:
            return HttpResponse('You have tried to register too many times. Please contact the site owner for more information.', status =  403)
    
    try:
        myinv = Invites.objects.get(code=invcode)
    except Invites.DoesNotExist:
        new_attempt = RegisterAttempts(ip_address=reqIP)
        new_attempt.save()
        return HttpResponse('Are you sure you are allowed?', status = 403)
    
    try:
        User.objects.get(username=username)
        return HttpResponse('That username is taken!')
    except User.DoesNotExist:
        newuser = User.objects.create_user(username=username, password=password, email=myinv.email)
        myinv.delete()

    return HttpResponse(reverse('registered'), status = 200)


def applied(request):
    return render(request, 'mylogin/frontpage_applied.html')

def registered(request):
    return render(request, 'mylogin/frontpage_registered.html')

@require_http_methods(['POST', 'GET'])
def forget_password(request):
    if request.method == 'GET':
        return render(request, 'mylogin/frontpage_forget.html')
    else:
        reqIP = get_client_ip_address(request)
        reqIPobj = RegisterAttempts.objects.filter(ip_address=reqIP)

        if reqIPobj is not None:
            counter = 0
            for q in reqIPobj:
                if (datetime.now(timezone.utc) - q.date).total_seconds() / (60 * 60) < 168:
                    counter += 1
            if counter < 5:
                data = request.POST.copy()
                username = data.get('Username')
                email = data.get('Email')
                try:
                    u = User.objects.get(username=username)
                    if u.email == email:
                        forget_password_email.delay(username)
                except User.DoesNotExist:
                    new_attempt = RegisterAttempts(ip_address=reqIP)
                    new_attempt.save()
    return render(request, 'mylogin/frontpage_forget_done.html')

@require_http_methods(['POST', 'GET'])
def reset_password(request, key1, key2, name):
    if request.method == 'GET':
        myobj = ForgetPassword.objects.filter(key1=key1).filter(key2=key2)
        if myobj:
            if myobj[0].requser.username == name:
                context = {}
                context['location'] = request.build_absolute_uri()
                return render(request, 'mylogin/frontpage_reset.html', context)
    else:
        myobj = ForgetPassword.objects.filter(key1=key1).filter(key2=key2)
        if myobj:
            data = request.POST.copy()
            password = data.get('Password2')
            if myobj[0].requser.username == name:
                myobj[0].requser.set_password(password)
                myobj[0].requser.save()
                myobj[0].delete()
                return render(request, 'mylogin/frontpage_reset_done.html')
    return HttpResponse('', status=404)


            

@require_http_methods(['POST', 'GET'])
@user_passes_test(lambda u: u.is_superuser)
def approve(request):
    
    if request.method == "POST":
        if request.POST.get('Approved', False):
            myobj = Applications.objects.get(pk=request.POST['application_choice'])
            letters = string.ascii_letters
            code = ''.join(random.choice(letters) for i in range(18))
            new_invite = Invites(code=code, email=myobj.email)
            new_invite.save()
            send_mail(
                'Your Invite Code',
                f'Hello {myobj.name},\n' + \
                'You are now able to view the site on https://kunflix.ydns.eu. Firstly, you will need to register an account.\n' + \
                f'You can register by entering the code below on the registration page:\n\n{code}\n\n' + \
                'Please be sure to use usernames and passwords that are not used elsewhere.' + \
                'This is because I cannot guarantee the safety of this site and any username and password may be compromised in the future.\n' + \
                'Thank you for using this site! Please do not reply to this email as I cannot receive emails.',
                'huakun@kunflix.ydns.eu',
                [f'{myobj.email}'],
                fail_silently=False,
            )
            myobj.approved = True
            myobj.save()
        
    allobj = Applications.objects.filter(approved=False)
    context = { 'applications' : allobj}
    return render(request, 'mylogin/approve_page.html', context)

# Create your views here.
