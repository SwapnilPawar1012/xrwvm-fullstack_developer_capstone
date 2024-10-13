from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from datetime import datetime

from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .populate import initiate
from .models import CarMake, CarModel
from .restapis import get_request, analyze_review_sentiments, post_review


# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']

    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    if request.method == 'POST':
        logout(request)
        data = {"message": "Successfully logged out", "userName": ""}
        return JsonResponse(data)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)

# Create a `registration` view to handle sign up request
@csrf_exempt
def registration(request):
    if request.method == 'POST':
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)
            username = data.get('userName')
            password = data.get('password')
            first_name = data.get('firstName')
            last_name = data.get('lastName')
            email = data.get('email')

            if not all([username, password, first_name, last_name, email]):
                return JsonResponse({"error": "Missing required fields"}, status=400)

            # Check if the username already exists
            if User.objects.filter(username=username).exists():
                return JsonResponse({"error": "Username already exists"}, status=400)

            # Check if the email already exists
            if User.objects.filter(email=email).exists():
                return JsonResponse({"error": "Email already registered"}, status=400)

            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password, email=email)
            login(request, user)
            return JsonResponse({"userName": username, "status": "Authenticated"}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)
    
#Update the `get_dealerships` render list of dealerships all by default, particular state if state is passed
def get_dealerships(request, state="All"):
    if(state == "All"):
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/"+state
    dealerships = get_request(endpoint)
    return JsonResponse({"status":200,"dealers":dealerships})

# Create a `get_dealer_reviews` view to render the reviews of a dealer
def get_dealer_reviews(request, dealer_id):
    if(dealer_id):
        endpoint = "/fetchReviews/dealer/"+str(dealer_id)
        reviews = get_request(endpoint)
        for review_detail in reviews:
            response = analyze_review_sentiments(review_detail['review'])
            print(response)
            review_detail['sentiment'] = response['sentiment']
        return JsonResponse({"status":200,"reviews":reviews})
    else:
        return JsonResponse({"status":400,"message":"Bad Request"})

# Create a `get_dealer_details` view to render the dealer details
def get_dealer_details(request, dealer_id):
    if(dealer_id):
        endpoint = "/fetchDealer/"+str(dealer_id)
        dealership = get_request(endpoint)
        return JsonResponse({"status":200,"dealer":dealership})
    else:
        return JsonResponse({"status":400,"message":"Bad Request"})

# Create a `add_review` view to submit a review
# def add_review(request):
#     if(request.user.is_anonymous == False):
#         data = json.loads(request.body)
#         try:
#             response = post_review(data)
#             return JsonResponse({"status":200})
#         except:
#             return JsonResponse({"status":401,"message":"Error in posting review"})
#     else:
#         return JsonResponse({"status":403,"message":"Unauthorized"})
@csrf_exempt
def add_review(request):
    if request.method == 'POST':
        if request.user.is_authenticated:  # Check if the user is authenticated
            try:
                data = json.loads(request.body)
                
                # Validate data here (e.g., check required fields)
                if not all(key in data for key in ("name", "dealership", "review", "car_make", "car_model", "car_year", "purchase_date")):
                    return JsonResponse({"status": 400, "message": "Missing required fields."})
                
                # Handle the review submission logic
                response = post_review(data)  # Ensure post_review is defined elsewhere
                
                return JsonResponse({"status": 200, "message": "Review posted successfully."})
            except json.JSONDecodeError:
                return JsonResponse({"status": 400, "message": "Invalid JSON data."})
            except Exception as e:
                return JsonResponse({"status": 500, "message": f"Error in posting review: {str(e)}"})
        else:
            return JsonResponse({"status": 403, "message": "Unauthorized"})
    else:
        return JsonResponse({"status": 405, "message": "Method not allowed"})

def get_cars(request):
    try:
        count = CarMake.objects.count()
        print(f"Count of CarMake: {count}")

        if count == 0:
            print("get cars initiate")
            initiate()  

        car_models = CarModel.objects.select_related('car_make')
        cars = [{"CarModel": car_model.name, "CarMake": car_model.car_make.name} for car_model in car_models]
        print("get cars: ", cars)

        return JsonResponse({"CarModels": cars})

    except Exception as e:
        print(f"Error fetching car models: {e}")  # Log the error for debugging
        return JsonResponse({"error": "An error occurred while fetching car models."}, status=500)
