from django.db import models
from django.utils.timezone import now
from django.core.validators import MaxValueValidator, MinValueValidator

# CarMake model to represent the make of a car
class CarMake(models.Model):
    name = models.CharField(max_length=100) 
    description = models.TextField(blank=True, null=True)  
    country = models.CharField(max_length=100, blank=True, null=True)  
    founding_year = models.IntegerField(
        blank=True, null=True,
        validators=[
            MinValueValidator(1886),  # Cars were invented in 1886
            MaxValueValidator(now().year)  # Founding year can't be in the future
        ]
    )  

    def __str__(self):
        return f"{self.name} ({self.country})"

# CarModel model to represent the model of a car
class CarModel(models.Model):
    CAR_TYPE_CHOICES = [
        ('Sedan', 'Sedan'),
        ('SUV', 'SUV'),
        ('Wagon', 'Wagon'),
    ]

    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE)  
    dealer_id = models.IntegerField() 
    name = models.CharField(max_length=100) 
    type = models.CharField(max_length=10, choices=CAR_TYPE_CHOICES) 
    year = models.IntegerField(
        validators=[
            MinValueValidator(1886),  # Cars were invented in 1886, so minimum value is 1886
            MaxValueValidator(now().year)  # Ensure the year is not in the future
        ]
    )

    def __str__(self):
        return f"{self.car_make.name} {self.name} ({self.type})"
