from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from django.shortcuts import render, redirect, get_object_or_404
from .models import TourPackage, Vehicle, Route
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from django.utils import timezone



def index(request):
    top_packages = TourPackage.objects.order_by('-start_date')[:10]  # Adjust order_by field as per your requirement
    return render(request, "home.html", {'packages': top_packages})

def about(request):
    return render(request, "commonAbout.html")
#....................................................USER.............................................
def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        date_of_birth = request.POST.get('date_of_birth')
        profile_picture = request.FILES.get('profile_picture')
        bio = request.POST.get('bio')

        # Basic validation
        if not username or not password or not email or not first_name or not last_name:
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'user/register_user.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'user/register_user.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'user/register_user.html')

        # Create the User
        user = User.objects.create_user(username=username, password=password, email=email)

        # Create the UserProfile
        UserProfile.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            address=address,
            date_of_birth=date_of_birth,
            profile_picture=profile_picture,
            bio=bio,
        )

        # Log in the user
        login(request, user)
        messages.success(request, "Registration successful! You are now logged in.")
        return redirect('home')  # Replace with your desired redirect URL after registration

    return render(request, 'user/register_user.html')

def common_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('admin_dashboard')  # Redirect to admin dashboard
            elif hasattr(user, 'agency'):
                return redirect('agency_dashboard')  # Redirect to agency dashboard
            else:
                messages.success(request, "Logged in successfully!")
                return redirect('package_list')  # Redirect to the package list page
        else:
            messages.error(request, "Invalid credentials.")
    
    return render(request, 'login.html')



@login_required
def user_profile(request):
    # Get the user's profile
    profile = UserProfile.objects.get(user=request.user)
    
    # Render the user profile template with the profile data
    return render(request, 'user/user_profile.html', {'profile': profile})

@login_required
def update_user_profile(request):
    if request.method == 'POST':
        # Get the user object
        user = request.user

        # Get or create UserProfile instance
        profile = UserProfile.objects.get_or_create(user=user)

        # Update user's first name, last name, and email
        profile.first_name = request.POST.get('first_name').strip()
        profile.last_name = request.POST.get('last_name').strip()
        profile.phone_number = request.POST.get('phone_number').strip()
        profile.address = request.POST.get('address').strip()
        profile.date_of_birth = request.POST.get('date_of_birth') or None
        profile.bio = request.POST.get('bio').strip()

        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            profile_picture = request.FILES['profile_picture']
            fs = FileSystemStorage()
            filename = fs.save(profile_picture.name, profile_picture)  # Save the file
            profile.profile_picture = fs.url(filename)  # Set the URL to the profile picture

        profile.save()  # Save profile details
        return redirect('user_profile')  # Redirect to the user profile page after saving

    return render(request, 'user/user_profile.html') 

@login_required
def user_bookings(request):
    bookings = Booking.objects.filter(user=request.user).select_related('tour_package__agency')
    return render(request, 'user/user_bookings.html', {'bookings': bookings})


@login_required
def pay_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.payment_status == 'Pending':
        # Simulate payment logic here (e.g., payment gateway integration)
        booking.payment_status = 'Paid'
        booking.save()
        messages.success(request, "Your booking has been successfully paid.")
    else:
        messages.error(request, "This booking cannot be paid or is already paid.")

    return redirect('user_bookings')

# View to handle cancellation
@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.payment_status == 'Pending':
        booking.payment_status = 'Cancelled'
        booking.save()
        messages.success(request, "Your booking has been successfully cancelled.")
    else:
        messages.error(request, "This booking cannot be cancelled or is already paid.")

    return redirect('user_bookings')

# View All Tour Packages
@login_required
def package_list(request):
    packages = TourPackage.objects.all()  # Get all packages; you can filter this if necessary
    return render(request, 'user/package_list.html', {'packages': packages})


def search_packages(request):
    route_name = request.GET.get('route', '').strip()
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    # Start with all packages
    packages = TourPackage.objects.all()

    # Filter by route
    if route_name:
        # Get the routes that match the provided name
        matching_routes = Route.objects.filter(place_info__icontains=route_name)
        if matching_routes.exists():
            packages = packages.filter(agency__in=matching_routes.values_list('agency', flat=True))

    # Filter by price range
    if min_price:
        packages = packages.filter(price__gte=min_price)
    if max_price:
        packages = packages.filter(price__lte=max_price)

    context = {
        'packages': packages,
        'route': route_name,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'user/package_list.html', context)


@login_required
def agency_list(request):
    agencies = TravelAgency.objects.all()  # Fetch all agencies
    return render(request, 'user/agency_list.html', {'agencies': agencies})

@login_required
def view_agency_packages(request, agency_id):
    agency = get_object_or_404(TravelAgency, id=agency_id)
    packages = agency.packages.all()  # Fetch packages for the specific agency
    return render(request, 'user/package_list_by_agency.html', {'agency': agency, 'packages': packages})

# Book Package View
@login_required
def book_package(request, pk):
    package = get_object_or_404(TourPackage, pk=pk)
    # Assuming there are relationships to get routes and vehicles associated with the package
    route = Route.objects.filter(agency=package.agency).first()  # Fetch an associated route if exists
    vehicle = Vehicle.objects.filter(agency=package.agency).first()  # Fetch an associated vehicle if exists

    if request.method == "POST":
        num_people = request.POST.get('num_people')
        total_cost = package.price * int(num_people)  # Calculate total cost
        
        booking = Booking.objects.create(
            user=request.user,
            tour_package=package,
            num_people=num_people,
            total_cost=total_cost
        )
        messages.success(request, "Booking successful!")
        return redirect('package_list')  # Redirect to the package list or a booking confirmation page
    
    return render(request, 'user/book_package.html', {
        'package': package,
        'route': route,
        'vehicle': vehicle
    })
 # Updated template path

# Cancel Package View
@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)  # Ensure only the user can cancel their booking
    if request.method == "POST":
        booking.delete()
        messages.success(request, "Booking canceled successfully!")
        return redirect('package_list')  # Redirect to the package list or a confirmation page

    return render(request, 'user/cancel_booking.html', {'booking': booking})


def top_tour_packages(request):
    # Retrieve the top 10 packages ordered by the start date, latest first
    top_packages = TourPackage.objects.order_by('-start_date')[:100]  
    
    return render(request, 'user/commonDestinations.html', {'packages': top_packages})


#..............................................End...................................................

#.............................................Agency...................................................
def register_agency(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        agency_name = request.POST.get('agency_name')
        address = request.POST.get('address')
        contact_email = request.POST.get('contact_email')
        contact_number = request.POST.get('contact_number')
        website = request.POST.get('website')
        agency_image = request.FILES.get('agency_image')
        # Basic validation (you can expand this as needed)
        if not username or not password or not email or not agency_name:
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'agency/register_agency.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'agency/register_agency.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'agency/register_agency.html')

        # Create the User
        user = User.objects.create_user(username=username, password=password, email=email)

        # Create the TravelAgency entry linked to the user
        TravelAgency.objects.create(
            owner=user,
            name=agency_name,
            address=address,
            contact_email=contact_email,
            contact_number=contact_number,
            website=website,
            agency_image=agency_image
        )

        # Log in the user
        login(request, user)
        messages.success(request, "Registration successful! Your agency is pending approval.")
        return redirect('home')  # Replace with your desired redirect URL

    return render(request, 'agency/register_agency.html')



@login_required
def agency_profile(request):
    try:
        agency = request.user.agency  # Access related agency using `related_name="agency"`
    except ObjectDoesNotExist:
        messages.error(request, "No agency profile found.")
        return redirect('home')
    
    return render(request, 'agency/agency_profile.html', {'agency': agency})

@login_required
def update_agency_profile(request):
    agency = TravelAgency.objects.get(owner=request.user)

    if request.method == 'POST':
        # Get updated information
        agency.name = request.POST.get('agency_name')
        agency.address = request.POST.get('address')
        agency.contact_email = request.POST.get('contact_email')
        agency.contact_number = request.POST.get('contact_number')
        agency.website = request.POST.get('website')
        
        # Handle agency image upload
        if request.FILES.get('agency_image'):
            agency.agency_image = request.FILES['agency_image']
        
        agency.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('agency_profile')

    return render(request, 'agency/agency_profile.html', {'agency': agency})

def agency_dashboard(request):
    agency = request.user.agency

    # Fetch data for the dashboard
    total_tour_packages = TourPackage.objects.filter(agency=agency).count()
    total_bookings = Booking.objects.filter(tour_package__agency=agency).count()
    
    # To get the count of vehicles linked to the tour packages of the agency
    total_vehicles = Vehicle.objects.filter(agency=agency).count()
    
    total_routes = Route.objects.filter(agency=agency).count()

    context = {
        'agency': agency,
        'total_tour_packages': total_tour_packages,
        'total_bookings': total_bookings,
        'total_vehicles': total_vehicles,
        'total_routes': total_routes,
    }
    
    return render(request, 'agency/dashboard.html', context)


@login_required
def vehicle_list(request):
    # Get the agency associated with the logged-in user
    agency = request.user.agency
    
    # Get distinct vehicles associated with tour packages belonging to the agency
    vehicles = Vehicle.objects.filter(agency=agency) 
    
    # Render the vehicle list template with the retrieved vehicles
    return render(request, 'agency/vehicle_list.html', {'vehicles': vehicles, 'agency': agency})

@login_required
def vehicle_create(request):
    if request.method == "POST":
        vehicle_type = request.POST.get('vehicle_type')
        seats_available = request.POST.get('seats_available')
        registration_number = request.POST.get('registration_number')
        
        # Associate vehicle with the user's agency
        vehicle = Vehicle.objects.create(
            vehicle_type=vehicle_type,
            seats_available=seats_available,
            registration_number=registration_number,
            agency=request.user.agency  # Link to the agency
        )
        return redirect('vehicle_list')

    return render(request, 'agency/vehicle_form.html')

@login_required
def vehicle_update(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk, agency=request.user.agency)  # Ensure the vehicle belongs to the user's agency
    if request.method == "POST":
        vehicle.vehicle_type = request.POST.get('vehicle_type')
        vehicle.seats_available = request.POST.get('seats_available')
        vehicle.registration_number = request.POST.get('registration_number')
        vehicle.save()
        return redirect('vehicle_list')
    
    return render(request, 'agency/vehicle_form.html', {'vehicle': vehicle})

@login_required
def vehicle_delete(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk, agency=request.user.agency)  # Ensure the vehicle belongs to the user's agency
    if request.method == "POST":
        vehicle.delete()
        return redirect('vehicle_list')
    
    return render(request, 'agency/vehicle_confirm_delete.html', {'vehicle': vehicle})

# Similar CRUD views for Route
@login_required
def route_list(request):
    agency = request.user.agency
    routes = Route.objects.filter(agency=agency).distinct()  # Get routes related to the user's agency
    return render(request, 'agency/route_list.html', {'routes': routes})
@login_required
def route_create(request):
    if request.method == "POST":
        place_info = request.POST.get('place_info')
        distance = request.POST.get('distance')
        tips = request.POST.get('tips')
        from_location = request.POST.get('from_location')  # Get from_location from the form
        to_location = request.POST.get('to_location')      # Get to_location from the form
        
        # Associate route with the user's agency
        route = Route.objects.create(
            from_location=from_location,  # Add from_location
            to_location=to_location,      # Add to_location
            place_info=place_info,
            distance=distance,
            tips=tips,
            agency=request.user.agency  # Link to the agency
        )
        return redirect('route_list')

    return render(request, 'agency/route_form.html')


@login_required
def route_update(request, pk):
    route = get_object_or_404(Route, pk=pk, agency=request.user.agency)  # Ensure the route belongs to the user's agency
    if request.method == "POST":
        route.place_info = request.POST.get('place_info')
        route.distance = request.POST.get('distance')
        route.tips = request.POST.get('tips')
        route.save()
        return redirect('route_list')

    return render(request, 'agency/route_form.html', {'route': route})

@login_required
def route_delete(request, pk):
    route = get_object_or_404(Route, pk=pk, agency=request.user.agency)  # Ensure the route belongs to the user's agency
    if request.method == "POST":
        route.delete()
        return redirect('route_list')
    
    return render(request, 'agency/route_confirm_delete.html', {'route': route})


# Similar CRUD views for TourPackage
@login_required
def tour_package_list(request):
    agency = request.user.agency
    tour_packages = TourPackage.objects.filter(agency=agency)  # Get tour packages related to the agency
    return render(request, 'agency/tour_package_list.html', {'tour_packages': tour_packages})
@login_required
def tour_package_create(request):
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        price = request.POST.get('price')
        availability = request.POST.get('availability')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        vehicles = request.POST.getlist('vehicles')  # Get selected vehicles
        routes = request.POST.getlist('routes')      # Get selected routes
        package_image = request.FILES.get('package_image')  # Get uploaded image

        tour_package = TourPackage.objects.create(
            agency=request.user.agency,
            title=title,
            description=description,
            price=price,
            availability=availability,
            start_date=start_date,
            end_date=end_date,
            package_image=package_image  # Save the uploaded image
        )
        
        # Add selected vehicles and routes to the tour package
        tour_package.vehicles.set(vehicles)
        tour_package.routes.set(routes)
        
        return redirect('tour_package_list')

    # Filter vehicles and routes by the agency
    vehicles = Vehicle.objects.filter(agency=request.user.agency)
    routes = Route.objects.filter(agency=request.user.agency)

    return render(request, 'agency/tour_package_form.html', {
        'vehicles': vehicles,
        'routes': routes,
    })

@login_required
def tour_package_update(request, pk):
    tour_package = get_object_or_404(TourPackage, pk=pk)
    if request.method == "POST":
        tour_package.title = request.POST.get('title')
        tour_package.description = request.POST.get('description')
        tour_package.price = request.POST.get('price')
        tour_package.availability = request.POST.get('availability')
        tour_package.start_date = request.POST.get('start_date')
        tour_package.end_date = request.POST.get('end_date')
        
        vehicles = request.POST.getlist('vehicles')  # Get selected vehicles
        routes = request.POST.getlist('routes')      # Get selected routes
        package_image = request.FILES.get('package_image')  # Get uploaded image

        # Update the package image only if a new one is uploaded
        if package_image:
            tour_package.package_image = package_image
        
        # Update selected vehicles and routes for the tour package
        tour_package.vehicles.set(vehicles)
        tour_package.routes.set(routes)
        
        tour_package.save()
        return redirect('tour_package_list')

    vehicles = Vehicle.objects.filter(agency=request.user.agency)
    routes = Route.objects.filter(agency=request.user.agency)

    return render(request, 'agency/tour_package_form.html', {
        'tour_package': tour_package,
        'vehicles': vehicles,
        'routes': routes,
    })


@login_required
def tour_package_delete(request, pk):
    tour_package = get_object_or_404(TourPackage, pk=pk)
    if request.method == "POST":
        tour_package.delete()
        return redirect('tour_package_list')

    return render(request, 'agency/tour_package_confirm_delete.html', {'tour_package': tour_package})

#.....................................END..............................................
#.............................................ADMIN......................................
@login_required
def admin_dashboard(request):
    # Only allow superuser to access this view
    if not request.user.is_superuser:
        return redirect('home')  # Redirect if not a superuser
    return render(request, 'travelAdmin/dashboard.html')

@login_required
def all_users(request):
    if not request.user.is_superuser:
        return redirect('home')  # Redirect if not a superuser
    
    users = UserProfile.objects.select_related('user').all()
    return render(request, 'travelAdmin/all_users.html', {'users': users})


@login_required
def delete_user(request, user_id):
     if not request.user.is_superuser:
        return redirect('home')  # Only superusers can delete users
    
     user_profile = get_object_or_404(UserProfile, id=user_id)
    
    # Delete the user profile and the associated user
     user_profile.user.delete()
     messages.success(request, "User deleted successfully.")
     return redirect('all_users')

@login_required
def manage_agencies(request):
    agencies = TravelAgency.objects.all()  # Get all agencies

    if request.method == 'POST':
        if 'update' in request.POST:
            agency_id = request.POST.get('agency_id')
            agency = get_object_or_404(TravelAgency, id=agency_id)
            agency.name = request.POST.get('name', agency.name)
            agency.address = request.POST.get('address', agency.address)
            agency.contact_email = request.POST.get('contact_email', agency.contact_email)
            agency.contact_number = request.POST.get('contact_number', agency.contact_number)
            agency.website = request.POST.get('website', agency.website)
            
            if request.FILES.get('agency_image'):
                agency.agency_image = request.FILES['agency_image']

            agency.save()
            messages.success(request, 'Agency updated successfully!')

        elif 'approve' in request.POST:
            agency_id = request.POST.get('agency_id')
            agency = get_object_or_404(TravelAgency, id=agency_id)
            agency.is_approved = True
            agency.approved_on = timezone.now()  # Assuming you want to set the approval time
            agency.save()
            messages.success(request, 'Agency approved successfully!')

        elif 'delete' in request.POST:
            agency_id = request.POST.get('agency_id')
            agency = get_object_or_404(TravelAgency, id=agency_id)
            agency.delete()
            messages.success(request, 'Agency deleted successfully!')

        return redirect('manage_agencies')  # Redirect to the same page to display the messages

    context = {
        'agencies': agencies,
    }
    return render(request, 'travelAdmin/manage_agencies.html', context)

from django.contrib.auth import logout as auth_logout
def logout(request):
    auth_logout(request)  # Call the built-in logout function
    return render(request, "home.html")

#.................................................END..............................................