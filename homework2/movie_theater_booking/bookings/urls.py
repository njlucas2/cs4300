from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"movies", views.MovieViewSet)
router.register(r"seats", views.SeatViewSet, basename="seat")
router.register(r"bookings", views.BookingViewSet, basename="booking")

urlpatterns = [
    path("api/", include(router.urls)),
    # template page routes get added here in section 4
]