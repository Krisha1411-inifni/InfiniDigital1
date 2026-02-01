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

from .models import Product, Cart, ClientUser
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

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Cart, Product

from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404, render

def cart(request):
    client_user_id = request.session.get('client_user_id')

    if not client_user_id:
        messages.warning(request, "Please signin first to add products to your cart.")
        return redirect('client_signup')   # your login URL name

    client_user = get_object_or_404(ClientUser, id=client_user_id)

    product_id = request.GET.get('product_id')

    if product_id:
        product = get_object_or_404(Product, id=product_id)

        cart_item, created = Cart.objects.get_or_create(
            user=client_user,
            product=product
        )

        if created:
            messages.success(request, "Product added to cart successfully.")
        else:
            messages.info(request, "This product is already in your cart.")

        return redirect('cart')

    cart_items = Cart.objects.filter(user=client_user)
    cart_total = 0
    for item in cart_items:
        cart_total += item.product.ProductDiscountPrice

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'cart_total': cart_total
    })

def client_signup(request):
    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'signup':
            username = request.POST.get('username')
            fname = request.POST.get('fname')
            lname = request.POST.get('lname')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if ClientUser.objects.filter(username=username).exists():
                messages.error(request, "Username already exists!")
                return redirect('client_signup')

            if ClientUser.objects.filter(email=email).exists():
                messages.error(request, "Email already exists!")
                return redirect('client_signup')

            if password != confirm_password:
                messages.error(request, "Passwords do not match!")
                return redirect('client_signup')

            client = ClientUser(
                username=username,
                email=email,
                password=password,
                first_name=fname,
                last_name=lname
            )
            client.set_password(password)
            client.save()

            subject = "Welcome to infiniDigital!!"
            message = "Hello " + client.first_name + "!! \n" + "Welcome to InfiniDigital!! \nThank you for visiting our website\n. We have also sent you a confirmation email, please confirm your email address. \n\nThanking You\nInfiniDigital"
            from_email = settings.EMAIL_HOST_USER
            to_list = [client.email]
            send_mail(subject, message, from_email, to_list, fail_silently=True)

            current_site = get_current_site(request)

            message2 = render_to_string("email_confirmation.html", {
                'name': client.first_name,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(client.pk)),
                'token': generate_token.make_token(client),
            })

            email = EmailMessage(
                subject="Confirm your email – InfiniDigital",
                body=message2,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[client.email],
            )
            email.content_subtype = "html"
            email.send()

            messages.success(request, "Account created successfully!")
            return redirect('client_signup')

        elif form_type == 'signin':
            username = request.POST.get('username')
            password = request.POST.get('password')

            try:
                client = ClientUser.objects.get(username=username)
            except ClientUser.DoesNotExist:
                messages.error(request, "Invalid credentials!")
                return redirect('client_signup')

            if not client.check_password(password):
                messages.error(request, "Invalid credentials!")
                return redirect('client_signup')

            if not client.is_active:
                messages.error(request, "Please verify your email first.")
                return redirect('client_signup')

            request.session['client_user_id'] = client.id

            messages.success(request, "Welcome Back!")
            return redirect('home')

    return render(request, "signup.html")


def client_activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        client = ClientUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, ClientUser.DoesNotExist):
        client = None

    if client is not None and generate_token.check_token(client, token):

        if client.is_active:
            messages.info(request, "Your account is already activated.")
            return redirect('client_signup')

        client.is_active = True
        client.save()

        request.session['client_user_id'] = client.id

        messages.success(request, "Account activated successfully!")
        return redirect('home')

    messages.error(request, "Activation link is invalid or expired.")
    return render(request, 'activation_failed.html')



def client_signout(request):
    request.session.pop('client_user_id',None)
    messages.success(request, "You have been logged out successfully 👋")
    return redirect('client_signup')

