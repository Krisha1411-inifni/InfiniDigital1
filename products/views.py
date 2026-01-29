from email import message_from_bytes

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.encoding import force_str, force_bytes
from django.contrib.sites.shortcuts import get_current_site
from base64 import urlsafe_b64decode
from django.core.mail import EmailMessage, send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings

from .models import Product
from .tokens import generate_token


# Create your views here.

def index(request):
    return render(request,'index.html')

def topic_detail(request,id):
    product = Product.objects.get(id = id)
    return render(request,'topics-detail.html',{"product":product})

def topic_listing(request):
    return render(request,'topic-listing.html')

def our_services(request):
    return render(request ,'our-services.html')

def template(request):
    return render(request, 'template.html')

def e_books(request):
    return render(request, 'e_books.html')

def pdfs(request):
    products = Product.objects.all()
    return render(request, 'pdfs.html', {'products': products})

def source_code(request):
    return render(request,'source_code.html')

def courses(request):
    return render(request,'courses.html')

def tools(request):
    return render(request,'tools.html')

def contact(request):
    return render(request,'contact.html')

def cart(request, id):
    product = Product.objects.get(id = id)
    return render(request,'cart.html',{"cartproduct" : product})


def signup(request):
    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'signup':
            username = request.POST.get('username')
            fname = request.POST.get('fname')
            lname = request.POST.get('lname')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists!")
                return redirect('signup')

            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists!")
                return redirect('signup')

            if password != confirm_password:
                messages.error(request, "Passwords do not match!")
                return redirect('signup')

            myuser = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=fname,
                last_name=lname
            )
            myuser.save()

            subject = "Welcome to infiniDigital!!"
            message = "Hello " + myuser.first_name + "!! \n" + "Welcome to InfiniDigital!! \nThank you for visiting our website\n. We have also sent you a confirmation email, please confirm your email address. \n\nThanking You\nInfiniDigital"
            from_email = settings.EMAIL_HOST_USER
            to_list = [myuser.email]
            send_mail(subject, message, from_email, to_list, fail_silently=True)

            current_site = get_current_site(request)

            message2 = render_to_string("email_confirmation.html", {
                'name': myuser.first_name,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
                'token': generate_token.make_token(myuser),
            })

            email = EmailMessage(
                subject="Confirm your email – InfiniDigital",
                body=message2,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[myuser.email],
            )
            email.content_subtype = "html"
            email.send()

            messages.success(request, "Account created successfully!")
            return redirect('signup')

        elif form_type == 'signin':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, "Welcome Back! Login successful!")

                return redirect('home')
            else:
                messages.error(request, "Invalid credentials!")
                return redirect('signup')

    return render(request, "signup.html")


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):

        if myuser.is_active:
            messages.info(request, "Your account is already activated.")
            return redirect('signup')

        myuser.is_active = True
        myuser.save()

        login(
            request,
            myuser,
            backend='django.contrib.auth.backends.ModelBackend'
        )

        messages.success(request, "Your account has been activated successfully!")
        return redirect('home')

    else:
        messages.error(request, "Activation link is invalid or expired.")
        return render(request, 'activation_failed.html')



def signout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully 👋")
    return redirect('signup')

