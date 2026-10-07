from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Movie, Seat, Booking
from .serializers import MovieSerializer, SeatSerializer, BookingSerializer


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