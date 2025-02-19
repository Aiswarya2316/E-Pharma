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

