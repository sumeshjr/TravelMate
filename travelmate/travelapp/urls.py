from django.contrib import admin
from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    path('', index, name='home'),
    path('about/', about, name='about'),
    
    path('vehicles/', vehicle_list, name='vehicle_list'),
    path('vehicles/create/', vehicle_create, name='vehicle_create'),
    path('vehicles/update/<int:pk>/', vehicle_update, name='vehicle_update'),
    path('vehicles/delete/<int:pk>/', vehicle_delete, name='vehicle_delete'),
    
    path('routes/', route_list, name='route_list'),
    path('routes/create/', route_create, name='route_create'),
    path('routes/update/<int:pk>/', route_update, name='route_update'),
    path('routes/delete/<int:pk>/', route_delete, name='route_delete'),

    path('tour_packages/', tour_package_list, name='tour_package_list'),
    path('tour_packages/create/', tour_package_create, name='tour_package_create'),
    path('search_packages', search_packages, name='search_packages'),
    path('tour_packages/update/<int:pk>/', tour_package_update, name='tour_package_update'),
    path('tour_packages/delete/<int:pk>/', tour_package_delete, name='tour_package_delete'),
    path('agency_dashboard/', agency_dashboard, name='agency_dashboard'),
    path('register_agency/', register_agency ,name="register_agency" ),
    path('login/', common_login ,name="login" ),
    path('logout/', logout ,name="logout" ),
    path('profile/', agency_profile, name='agency_profile'),
    path('profile/update/', update_agency_profile, name='update_agency_profile'),
    
    
    path('register_user/', register_user, name='register_user'),
    path('packages/', package_list, name='package_list'),
    path('book/<int:pk>/', book_package, name='book_package'),
    path('cancel/<int:pk>/', cancel_booking, name='cancel_booking'),
    path('bookings/pay/<int:booking_id>/', pay_booking, name='pay_booking'),
    path('bookings/cancel/<int:booking_id>/',cancel_booking, name='cancel_booking'),
    path('user_bookings', user_bookings, name='user_bookings'),
    path('top_tour_packages', top_tour_packages, name='top_tour_packages'),
    path('agency_list', agency_list, name='agency_list'),
    path('agencies/<int:agency_id>/packages/', view_agency_packages, name='view_agency_packages'),
    path('user_profile/', user_profile, name='user_profile'),
    path('user_profile/update/', update_user_profile, name='update_user_profile'),

    path('travelAdmin/dashboard/', admin_dashboard, name='admin_dashboard'),  # Admin dashboard
    path('travelAdmin/users/', all_users, name='all_users'),  # View all users
    path('delete-user/<int:user_id>/', delete_user, name='delete_user'),
    path('travelAdmin/agencies/', manage_agencies, name='manage_agencies'), 
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)