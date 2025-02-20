from django.urls import path
from .import views
urlpatterns = [
    path('',views.home,name='home'),
    path("registercustomer/", views.customer_register, name="customer_register"),
    path("registerseller/", views.seller_register, name="seller_register"),
    path("registeradmin/", views.admin_register, name="admin_register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path('adminhome',views.adminhome,name='adminhome'),
    path('customerhome',views.customerhome,name='customerhome'),
    path('sellerhome',views.sellerhome,name='sellerhome'),
    path("add-medicine/", views.add_medicine, name="add_medicine"),
    path("edit-medicine/<int:medicine_id>/", views.edit_medicine, name="edit_medicine"),
    path("delete-medicine/<int:medicine_id>/", views.delete_medicine, name="delete_medicine"),
    path('viewmedicines/', views.medicine_list, name='medicine_list'),
    path('buy/<int:medicine_id>/', views.buy_medicine, name='buy_medicine'),
    path("payment/<int:order_id>/", views.payment_page, name="payment_page"),
    path("payment-success/", views.payment_success, name="payment_success"),
    path("booking-history/", views.booking_history, name="booking_history"),
    path("sellerbookings/", views.seller_booking_history, name="seller_booking_history"),
    path("viewusers/", views.viewusers, name="viewusers"),
    path("viewsellers/", views.viewsellers, name="viewsellers"),
    path("viewmedicine/", views.viewmedicines, name="viewmedicines"),
    path("viewbookings/", views.viewbookings, name="viewbookings"),
    path("about/", views.about, name="about"),
    path('profile/', views.customer_profile, name='customer_profile'),
    path('profileupdate/', views.update_customer_profile, name='update_customer_profile'),







]
