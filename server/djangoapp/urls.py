# Uncomment the imports before you add the code
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'djangoapp'
urlpatterns = [
    # Path for user registration
    path('register/', views.registration, name='register'),

    # Path for login
    path('login/', views.login_user, name='login'),

    # Path for logout
    path('logout/', views.logout_request, name='logout'),

    # Path for getting cars
    path('get_cars/', views.get_cars, name='get_cars'),

    # Path for getting dealerships with optional state
    path('get_dealers/', views.get_dealerships, name='get_dealers'),
    path('get_dealers/<str:state>/', views.get_dealerships, name='get_dealers_by_state'),

    # Path for getting dealer details
    path('dealer/<int:dealer_id>/', views.get_dealer_details, name='dealer_details'),

    # Path for getting dealer reviews
    path('reviews/dealer/<int:dealer_id>/', views.get_dealer_reviews, name='dealer_reviews'),
    # path for dealer reviews view

    # path for add a review view
    path('add_review/', views.add_review, name='add_review'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
