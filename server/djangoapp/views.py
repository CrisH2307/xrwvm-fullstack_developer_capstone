from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.csrf import csrf_exempt
from .populate import initiate
from .models import CarMake, CarModel
from .restapis import get_request, analyze_review_sentiments, post_review
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your views here.
def get_cars(request):
    count = CarMake.objects.count()
    if count == 0:
        initiate()
    car_models = CarModel.objects.select_related('car_make')
    cars = [
        {"CarModel": car_model.name, "CarMake": car_model.car_make.name}
        for car_model in car_models
    ]
    return JsonResponse({"CarModels": cars})

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data['userName']
            password = data['password']
        except (KeyError, json.JSONDecodeError) as e:
            return JsonResponse({"error": str(e)}, status=400)

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"userName": username, "status": "Authenticated"})
        return JsonResponse({"userName": username, "status": "Failed to authenticate"}, status=401)
    return JsonResponse({"error": "Invalid HTTP method"}, status=405)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return JsonResponse({"userName": ""})

# Create a `registration` view to handle sign up request
@csrf_exempt
def registration(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data['userName']
            password = data['password']
            first_name = data['firstName']
            last_name = data['lastName']
            email = data['email']
        except (KeyError, json.JSONDecodeError) as e:
            return JsonResponse({"error": str(e)}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({"userName": username, "error": "Username already registered"}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({"email": email, "error": "Email already registered"}, status=400)

        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password, email=email)
        login(request, user)
        return JsonResponse({"userName": username, "status": "Authenticated"})
    return JsonResponse({"error": "Invalid HTTP method"}, status=405)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request, state="All"):
    endpoint = "/fetchDealers" if state == "All" else f"/fetchDealers/{state}"

    try:
        dealerships = get_request(endpoint)
        return JsonResponse({"status": 200, "dealers": dealerships})
    except Exception as e:
        logger.error(f"Error fetching dealerships: {str(e)}")
        return JsonResponse({"status": 500, "error": str(e)})

# Create a `get_dealer_reviews` view to render the reviews of a dealer
def get_dealer_reviews(request, dealer_id):
    if dealer_id:
        try:
            endpoint = f"/fetchReviews/dealer/{dealer_id}"
            reviews = get_request(endpoint)
            for review_detail in reviews:
                response = analyze_review_sentiments(review_detail['review'])
                review_detail['sentiment'] = response.get('sentiment', 'unknown')
            return JsonResponse({"status": 200, "reviews": reviews})
        except Exception as e:
            logger.error(f"Error fetching reviews: {str(e)}")
            return JsonResponse({"status": 500, "error": str(e)})
    return JsonResponse({"status": 400, "message": "Bad Request"})

# Create a `get_dealer_details` view to render the dealer details
def get_dealer_details(request, dealer_id):
    if dealer_id:
        try:
            endpoint = f"/fetchDealer/{dealer_id}"
            dealership = get_request(endpoint)
            return JsonResponse({"status": 200, "dealer": dealership})
        except Exception as e:
            logger.error(f"Error fetching dealer details: {str(e)}")
            return JsonResponse({"status": 500, "error": str(e)})
    return JsonResponse({"status": 400, "message": "Bad Request"})

# Create a `add_review` view to submit a review
@csrf_exempt
def add_review(request):
    if not request.user.is_anonymous:
        try:
            data = json.loads(request.body)
            post_review(data)
            return JsonResponse({"status": 200})
        except Exception as e:
            logger.error(f"Error posting review: {str(e)}")
            return JsonResponse({"status": 500, "message": "Error in posting review"})
    return JsonResponse({"status": 403, "message": "Unauthorized"})
