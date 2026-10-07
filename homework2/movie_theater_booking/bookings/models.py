from django.db import models
from django.contrib.auth.models import User


class Movie(models.Model):
    """A film that can be shown and booked."""
    title = models.CharField(max_length=200)
    description = models.TextField()
    release_date = models.DateField()
    duration = models.PositiveIntegerField(help_text="Length in minutes")

    def __str__(self):
        return self.title

class Seat(models.Model):
    """A seat for a specific movie. Each movie has its own set of seats."""
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="seats")
    seat_number = models.CharField(max_length=10)   # e.g. "A1"
    is_booked = models.BooleanField(default=False)

    class Meta:
        unique_together = ("movie", "seat_number")
        ordering = ["seat_number"]

    def __str__(self):
        status = "booked" if self.is_booked else "available"
        return f"{self.movie.title} - {self.seat_number} ({status})"

class Booking(models.Model):
    """Records that a user booked a particular seat for a movie."""
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="bookings")
    seat = models.OneToOneField(Seat, on_delete=models.CASCADE, related_name="booking")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    booking_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-booking_date"]

    def __str__(self):
        return f"{self.user.username}: {self.movie.title} seat {self.seat.seat_number}"