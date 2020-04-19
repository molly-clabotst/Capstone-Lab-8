from django.urls import path
from . import views

urlpatterns = [
    path('', views.place_list, name='place_list'),
    path('visited', views.places_visited, name='places_visited'),
    # <int: var_name> allows for the insertion of a variable
    path('place/<int:place_pk>/was_visited', views.place_was_visited, name='place_was_visited'),
    path('place/<int:place_pk>', views.place_details, name='place_details'),
    path('place/<int:place_pk>/delete', views.delete_place, name='delete_place'),
]