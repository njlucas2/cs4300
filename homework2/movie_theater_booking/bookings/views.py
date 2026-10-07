from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Movie, Seat, Booking
from .serializers import MovieSerializer, SeatSerializer, BookingSerializer
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, get_object_or_404, redirect

class MovieViewSet(viewsets.ModelViewSet):
    """Full CRUD for movies."""
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class SeatViewSet(viewsets.ModelViewSet):
    """Seats with availability filtering and a booking shortcut."""
    serializer_class = SeatSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = Seat.objects.all()
        movie_id = self.request.query_params.get("movie")
        if movie_id:
            qs = qs.filter(movie_id=movie_id)
        if self.request.query_params.get("available") == "true":
            qs = qs.filter(is_booked=False)
        return qs

    @action(detail=True, methods=["post"],
            permission_classes=[permissions.IsAuthenticated])
    def book(self, request, pk=None):
        """POST /api/seats/<id>/book/ books this seat for the current user."""
        seat = self.get_object()
        serializer = BookingSerializer(
            data={"movie": seat.movie_id, "seat": seat.id},
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class BookingViewSet(viewsets.ModelViewSet):
    """Users create bookings and see only their own history."""
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "delete"]  # no editing a booking

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        instance.seat.is_booked = False
        instance.seat.save()
        instance.delete()

# ---------- Template (HTML) views ----------

def movie_list(request):
    """Home page: every movie as a card."""
    movies = Movie.objects.order_by("title")
    return render(request, "bookings/movie_list.html", {"movies": movies})

@login_required
def book_seat(request, movie_id):
    """Show the seat grid for a movie and handle a booking submission."""
    movie = get_object_or_404(Movie, pk=movie_id)

    if request.method == "POST":
        serializer = BookingSerializer(
            data={"movie": movie.id, "seat": request.POST.get("seat")},
            context={"request": request},
        )
        try:
            if serializer.is_valid():
                booking = serializer.save()
                messages.success(
                    request,
                    f"Booked seat {booking.seat.seat_number} for {movie.title}!",
                )
                return redirect("booking_history")
            errors = serializer.errors.get("non_field_errors")
            messages.error(request, errors[0] if errors else "That seat couldn't be booked.")
        except serializers.ValidationError as e:  # seat taken mid-request
            messages.error(request, e.detail[0])
        return redirect("book_seat", movie_id=movie.id)

    rows = {}
    for seat in movie.seats.all():
        rows.setdefault(seat.seat_number[0], []).append(seat)

    return render(request, "bookings/seat_booking.html",
                  {"movie": movie, "rows": rows})

@login_required
def booking_history(request):
    """The logged-in user's bookings, newest first."""
    bookings = (Booking.objects.filter(user=request.user)
                .select_related("movie", "seat"))
    return render(request, "bookings/booking_history.html", {"bookings": bookings})