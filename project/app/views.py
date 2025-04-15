from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Customer, Seller, AdminReg
from .forms import CustomerRegistrationForm, SellerRegistrationForm, AdminRegistrationForm, LoginForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Medicine, Category
from .forms import MedicineForm


def home(request):
    return render(request,'home.html')



# Customer Registration
def customer_register(request):
    if request.method == "POST":
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer registered successfully!")
            return redirect("login")
    else:
        form = CustomerRegistrationForm()
    return render(request, "customer/register.html", {"form": form, "user_type": "Customer"})



# Seller Registration
def seller_register(request):
    if request.method == "POST":
        form = SellerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Seller registered successfully!")
            return redirect("login")
    else:
        form = SellerRegistrationForm()
    return render(request, "seller/register.html", {"form": form, "user_type": "Seller"})



# Admin Registration
def admin_register(request):
    if request.method == "POST":
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Admin registered successfully!")
            return redirect("login")
    else:
        form = AdminRegistrationForm()
    return render(request, "admin/register.html", {"form": form, "user_type": "Admin"})



# Login View
def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            # Check in all user models
            user = None
            redirect_url = "login"  # Default in case of failure
            if Customer.objects.filter(email=email, password=password).exists():
                user = Customer.objects.get(email=email)
                request.session["user_type"] = "Customer"
                redirect_url = "customerhome"
            elif Seller.objects.filter(email=email, password=password).exists():
                user = Seller.objects.get(email=email)
                request.session["user_type"] = "Seller"
                request.session["user_id"] = user.id  # Store seller ID in session
                redirect_url = "sellerhome"

            elif AdminReg.objects.filter(email=email, password=password).exists():
                user = AdminReg.objects.get(email=email)
                request.session["user_type"] = "Admin"
                redirect_url = "adminhome"
            if user:
                request.session["user_id"] = user.id
                messages.success(request, f"Welcome {user.name}!")
                return redirect(redirect_url)  # Redirect based on user type
            else:
                messages.error(request, "Invalid credentials")
    form = LoginForm()
    return render(request, "login.html", {"form": form})



# Logout View
def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect("home")





def adminhome(request):
    return render(request,'admin/adminhome.html')



def customerhome(request):
    return render(request,'customer/customerhome.html')



def sellerhome(request):
    if "user_id" in request.session and request.session.get("user_type") == "Seller":
        seller_medicines = Medicine.objects.filter(seller_id=request.session["user_id"])
        return render(request, "seller/sellerhome.html", {"medicines": seller_medicines})
    return redirect("login")






# Add Medicine
def add_medicine(request):
    if "user_id" in request.session and request.session.get("user_type") == "Seller":
        if request.method == "POST":
            form = MedicineForm(request.POST, request.FILES)
            if form.is_valid():
                medicine = form.save(commit=False)
                medicine.seller_id = request.session["user_id"]  # Assign seller
                medicine.save()
                messages.success(request, "Medicine added successfully!")
                return redirect("sellerhome")
        else:
            form = MedicineForm()
        return render(request, "seller/add_medicine.html", {"form": form})
    return redirect("login")




# Edit Medicine
def edit_medicine(request, medicine_id):
    medicine = get_object_or_404(Medicine, id=medicine_id, seller_id=request.session["user_id"])
    if request.method == "POST":
        form = MedicineForm(request.POST, request.FILES, instance=medicine)
        if form.is_valid():
            form.save()
            messages.success(request, "Medicine updated successfully!")
            return redirect("sellerhome")
    else:
        form = MedicineForm(instance=medicine)
    return render(request, "seller/edit_medicine.html", {"form": form})




# Delete Medicine
def delete_medicine(request, medicine_id):
    medicine = get_object_or_404(Medicine, id=medicine_id, seller_id=request.session["user_id"])
    medicine.delete()
    messages.success(request, "Medicine deleted successfully!")
    return redirect("sellerhome")





from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Medicine, Category
from .forms import PrescriptionUploadForm

# View all medicines
def medicine_list(request):
    medicines = Medicine.objects.all()
    categories = Category.objects.all()
    query = request.GET.get('category')
    if query:
        medicines = medicines.filter(category__name__icontains=query)
    return render(request, 'customer/medicinelist.html', {'medicines': medicines, 'categories': categories})







from django.shortcuts import render, redirect, get_object_or_404
from .models import Medicine, Order
from .forms import PrescriptionUploadForm
def buy_medicine(request, medicine_id):
    medicine = get_object_or_404(Medicine, id=medicine_id)
    customer = Customer.objects.first()  # Assign a default customer (or create one if necessary)
    
    if request.method == "POST":
        form = PrescriptionUploadForm(request.POST, request.FILES)
        if form.is_valid():
            order = form.save(commit=False)
            order.medicine = medicine
            order.customer = customer  # Assign the default customer
            order.status = "Pending"
            order.save()
            return redirect("payment_page", order_id=order.id)
    
    else:
        form = PrescriptionUploadForm()

    return render(request, "customer/buymedicines.html", {"form": form, "medicine": medicine})





import razorpay
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from .models import Order

# Razorpay client initialization
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def payment_page(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Convert price to paisa (Razorpay expects amount in paisa)
    amount = int(order.medicine.price * 100)  

    # Create a Razorpay Order
    razorpay_order = razorpay_client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": "1"
    })

    context = {
        "order": order,
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "amount": amount,
        "payment_id": razorpay_order["id"]
    }
    return render(request, "customer/payment.html", context)




def payment_success(request):
    order_id = request.GET.get("order_id")
    payment_id = request.GET.get("payment_id")

    order = get_object_or_404(Order, id=order_id)

    if "user_id" in request.session:
        customer_id = request.session["user_id"]
        order.customer_id = customer_id
        order.status = "Paid"
        order.save()

        # Reduce stock after successful payment
        medicine = order.medicine
        if medicine.stock > 0:
            medicine.stock -= 1
            medicine.save()

    return redirect("booking_history")






def booking_history(request):
    if "user_id" in request.session and request.session.get("user_type") == "Customer":
        customer_id = request.session["user_id"]
        print("Logged-in User ID:", customer_id)  # Debugging

        try:
            customer = Customer.objects.get(id=customer_id)  # Fetch the specific customer
            orders = Order.objects.filter(customer=customer).order_by("-order_date")  # Filter only their orders

            return render(request, "customer/booking_history.html", {"orders": orders})
        except Customer.DoesNotExist:
            messages.error(request, "Customer not found.")
            return redirect("login")

    messages.error(request, "You need to log in to view your bookings.")
    return redirect("login")







from django.shortcuts import render, get_object_or_404
from .models import Order, Seller

def seller_booking_history(request):
    seller_id = request.session.get("user_id")  # Get logged-in seller's ID from session
    
    if not seller_id:
        return render(request, "error.html", {"message": "Seller not found. Please log in again."})

    seller = get_object_or_404(Seller, id=seller_id)  # Fetch seller by ID
    
    orders = Order.objects.filter(medicine__seller=seller).order_by("-order_date")  # Fetch seller's orders

    return render(request, "seller/booking_history.html", {"orders": orders, "seller": seller})






def viewbookings(request):
    users=Order.objects.all()
    return render(request,'admin/viewbooking.html',{'users':users})




def viewusers(request):
    users=Customer.objects.all()
    return render(request,'admin/viewusers.html',{'users':users})



def viewsellers(request):
    sellers=Seller.objects.all()
    return render(request,'admin/viewsellers.html',{'sellers':sellers})



def viewmedicines(request):
    medicine=Medicine.objects.all()
    return render(request,'admin/viewmedicines.html',{'medicine':medicine})



def about(request):
    return render(request,'customer/about.html')





from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .models import Customer

def customer_profile(request):
    customer_email = request.session.get('customer_email')  # Get logged-in customer's email
    if not customer_email:
        messages.error(request, "Please log in to view your profile.")
        return redirect('login')

    customer = Customer.objects.filter(email=customer_email).first()
    if not customer:
        messages.error(request, "Customer not found.")
        return redirect('login')

    return render(request, 'customer/profile.html', {'customer': customer})


def update_customer_profile(request):
    customer_email = request.session.get('customer_email')
    if not customer_email:
        messages.error(request, "Please log in to update your profile.")
        return redirect('login')

    customer = Customer.objects.filter(email=customer_email).first()
    if not customer:
        messages.error(request, "Customer not found.")
        return redirect('login')

    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        location = request.POST.get('location')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password and password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('update_customer_profile')

        customer.name = name
        customer.phone = phone
        customer.location = location
        if password:
            customer.password = make_password(password)  # Secure password storage
        customer.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('customer_profile')

    return render(request, 'customer/update_profile.html', {'customer': customer})




from django.shortcuts import redirect, get_object_or_404
from .models import Order

def cancel_booking(request, order_id):
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id)
        if order.status in ['Pending', 'Paid']:
            order.status = 'Cancelled'
            order.save()
    return redirect('booking_history')
