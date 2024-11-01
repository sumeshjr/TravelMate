from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to the default User model
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=10, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    # Additional optional fields
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.first_name} {self.last_name}"

class TravelAgency(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name="agency")
    agency_image = models.ImageField(upload_to='agency/', blank=True, null=True)
    name = models.CharField(max_length=255)
    address = models.TextField()
    contact_email = models.EmailField()
    contact_number = models.CharField(max_length=20)
    website = models.URLField(blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    approved_on = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name


class Vehicle(models.Model):
    agency = models.ForeignKey(TravelAgency, on_delete=models.CASCADE)
    vehicle_type = models.CharField(max_length=100)  # e.g., Bus, Car, etc.
    seats_available = models.PositiveIntegerField()
    registration_number = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.vehicle_type} ({self.registration_number})"


class Route(models.Model):
    agency = models.ForeignKey(TravelAgency, on_delete=models.CASCADE)
    from_location = models.TextField()  # Starting location
    to_location = models.TextField()  # Destination location
    place_info = models.TextField()  # Description of places
    distance = models.DecimalField(max_digits=6, decimal_places=2)  # Distance in km
    images = models.ImageField(upload_to='routes/', blank=True, null=True)
    tips = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Route from {self.from_location} to {self.to_location} with distance: {self.distance} km" 

class TourPackage(models.Model):
    agency = models.ForeignKey(TravelAgency, on_delete=models.CASCADE, related_name="packages")
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    availability = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    package_image = models.ImageField(upload_to='package_images/', blank=True, null=True)
    vehicles = models.ManyToManyField(Vehicle, related_name="tour_packages")
    routes = models.ManyToManyField(Route, related_name="tour_packages") 
    def __str__(self):
        return self.title




# 4. Booking Model
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tour_package = models.ForeignKey(TourPackage, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    num_people = models.PositiveIntegerField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=50, choices=[
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Cancelled', 'Cancelled')
    ], default='Pending')
    
    def __str__(self):
        return f"Booking for {self.tour_package} by {self.user.username}"
    