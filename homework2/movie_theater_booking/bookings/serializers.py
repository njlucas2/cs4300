from django.db import transaction
from rest_framework import serializers
from .models import Movie, Seat, Booking

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ["id", "title", "description", "release_date", "duration"]

class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ["id", "movie", "seat_number", "is_booked"]
        read_only_fields = ["is_booked"]

class BookingSerializer(serializers.ModelSerializer):
    # Hidden field so that the user can't change it.
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    movie_title = serializers.CharField(source="movie.title", read_only=True)
    seat_number = serializers.CharField(source="seat.seat_number", read_only=True)

    class Meta:
        model = Booking
        fields = ["id", "movie", "movie_title", "seat", "seat_number",
                  "user", "booking_date"]
        read_only_fields = ["booking_date"]
        extra_kwargs = {"seat": {"validators": []}}

    def validate(self, data):
        """Reject seats that belong to a different movie or are already taken."""
        if data["seat"].movie_id != data["movie"].id:
            raise serializers.ValidationError("That seat is not for this movie.")
        if data["seat"].is_booked:
            raise serializers.ValidationError("That seat is already booked.")
        return data

    def create(self, validated_data):
        """Create the booking and mark the seat as booked."""
        with transaction.atomic():
            seat = Seat.objects.select_for_update().get(pk=validated_data["seat"].pk)
            if seat.is_booked:  # re-check inside the lock
                raise serializers.ValidationError("That seat was just booked.")
            seat.is_booked = True
            seat.save()
            return super().create(validated_data)