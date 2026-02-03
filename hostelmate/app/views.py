from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from .models import *
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json






# Create your views here.
def index(request):
    category = request.GET.get('category', 'gents')
    hostels = Hostel.objects.filter(category=category)

    if request.user.is_authenticated:
        user_requests = BookingRequest.objects.filter(user=request.user)

    request_map = {
        req.hostel_id: req for req in user_requests
    }

    for hostel in hostels:
        booking = request_map.get(hostel.id)
        hostel.booking = booking
    else:
        for hostel in hostels:
            hostel.booking = None


    return render(request, 'index.html', {
        'hostels': hostels,
        'selected_category': category
    })






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


@login_required
def owner_dashboard(request):
    if not request.user.is_staff:
        return redirect(index)

    if request.method == 'POST':
        image = request.FILES.get('image')  # 🔥 THIS LINE WAS MISSING

        Hostel.objects.create(
            owner=request.user,
            name=request.POST['name'],
            category=request.POST['category'],
            location=request.POST['location'],
            beds_available=request.POST['beds'],
            price=request.POST['price'],
            image=image  # 🔥 PASS IMAGE HERE
        )
        print(request.FILES)


        return redirect(owner_dashboard)

    hostels = Hostel.objects.filter(owner=request.user)
    requests = BookingRequest.objects.filter(
        hostel__owner=request.user,
        status='pending'
    )

    return render(request, 'owner_dashboard.html', {
        'hostels': hostels,
        'requests': requests
    })

    
@login_required
def update_beds(request, hostel_id):
    hostel = Hostel.objects.get(id=hostel_id, owner=request.user)
    hostel.beds_available = request.POST['beds']
    hostel.save()
    return redirect(owner_dashboard)

@login_required
def delete_hostel(request, hostel_id):
    hostel = Hostel.objects.get(id=hostel_id, owner=request.user)
    hostel.delete()
    return redirect(owner_dashboard)


@login_required
def send_request(request, hostel_id):
    hostel = Hostel.objects.get(id=hostel_id)

    if hostel.beds_available <= 0:
        return redirect(index)

    # ❌ Prevent duplicate request
    BookingRequest.objects.get_or_create(
        hostel=hostel,
        user=request.user,
        defaults={'status': 'pending'}
    )

    return redirect('hostel_detail', hostel_id=hostel.id)



@login_required
def accept_request(request, request_id):
    booking = BookingRequest.objects.get(
        id=request_id,
        hostel__owner=request.user
    )

    if booking.hostel.beds_available > 0:
        booking.status = 'accepted'
        booking.hostel.beds_available -= 1
        booking.hostel.save()
        booking.save()

    return redirect(owner_dashboard)


@login_required
def user_requests(request):
    bookings = BookingRequest.objects.filter(user=request.user)

    return render(request, 'requests.html', {
        'bookings': bookings
    })




def search_hostels(request):
    location = request.GET.get('location')
    category = request.GET.get('category', 'gents')

    hostels = Hostel.objects.filter(
        location__icontains=location,
        category=category
    )

    if request.user.is_authenticated:
        user_requests = BookingRequest.objects.filter(user=request.user)
        request_map = {req.hostel_id: req.status for req in user_requests}

        for hostel in hostels:
            hostel.request_status = request_map.get(hostel.id)
    else:
        for hostel in hostels:
            hostel.request_status = None

    return render(request, 'search_results.html', {
        'hostels': hostels,
        'location': location,
        'selected_category': category
    })

def hostel_detail(request, hostel_id):
    hostel = Hostel.objects.get(id=hostel_id)

    hostel.avg_rating = hostel.reviews.aggregate(
        Avg("rating")
    )["rating__avg"] or 0

    booking = None
    if request.user.is_authenticated:
        booking = BookingRequest.objects.filter(
            hostel=hostel,
            user=request.user
        ).first()

    return render(request, 'hostel_detail.html', {
        'hostel': hostel,
        'booking': booking
    })

@login_required
def pay_advance(request, booking_id):
    booking = BookingRequest.objects.get(
        id=booking_id,
        user=request.user,
        status='accepted'
    )

    # STEP 1: Show amount entry page
    if request.method == "GET":
        return render(request, "enter_advance.html", {
            "booking": booking
        })

    # STEP 2: Handle payment
    if request.method == "POST":
        amount = int(request.POST.get("amount")) * 100  # rupees → paise

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": "1"
        })

        return render(request, "payment.html", {
            "order": order,
            "booking": booking,
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "amount": amount
        })



@csrf_exempt
def payment_success(request):
    data = json.loads(request.body)

    booking = BookingRequest.objects.get(id=data["booking_id"])
    booking.is_paid = True
    booking.save()

    return redirect("hostel_detail", hostel_id=booking.hostel.id)


@login_required
def owner_payments(request):
    if not request.user.is_staff:
        return redirect('index')

    payments = BookingRequest.objects.filter(
        hostel__owner=request.user,
        status='accepted'
    ).select_related('hostel', 'user')

    return render(request, 'owner_payments.html', {
        'payments': payments
    })

@login_required
def owner_hostels(request):
    if not request.user.is_staff:
        return redirect(index)

    hostels = Hostel.objects.filter(owner=request.user)
    return render(request, "owner_hostels.html", {
        "hostels": hostels
    })


@login_required
def owner_requests(request):
    if not request.user.is_staff:
        return redirect(index)

    requests = BookingRequest.objects.filter(
        hostel__owner=request.user
    )

    return render(request, "owner_requests.html", {
        "requests": requests
    })

def about(request):
    return render(request, "about.html")
