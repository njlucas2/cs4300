from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"movies", views.MovieViewSet)
router.register(r"seats", views.SeatViewSet, basename="seat")
router.register(r"bookings", views.BookingViewSet, basename="booking")

urlpatterns = [
    path("", views.movie_list, name="movie_list"),
    path("movies/<int:movie_id>/book/", views.book_seat, name="book_seat"),
    path("history/", views.booking_history, name="booking_history"),
    path("api/", include(router.urls)),
]