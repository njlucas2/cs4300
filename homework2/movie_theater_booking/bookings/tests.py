import datetime

from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Movie, Seat, Booking

def make_movie(title="Dune"):
    """Helper so every test creates movies the same way."""
    return Movie.objects.create(
        title=title,
        description="A test movie.",
        release_date=datetime.date(2024, 3, 1),
        duration=166,
    )


# ------------ Unit tests ------------------

class ModelTests(TestCase):
    """Model behavior and database-level constraints."""

    @classmethod
    def setUpTestData(cls):
        cls.movie = make_movie()
        cls.seat = Seat.objects.create(movie=cls.movie, seat_number="A1")
        cls.user = User.objects.create_user("alice", password="pass12345")

    def test_movie_str(self):
        self.assertEqual(str(self.movie), "Dune")

    def test_seat_str_shows_status(self):
        self.assertEqual(str(self.seat), "Dune - A1 (available)")

    def test_new_seat_is_available(self):
        self.assertFalse(self.seat.is_booked)

    def test_booking_str(self):
        booking = Booking.objects.create(movie=self.movie, seat=self.seat, user=self.user)
        self.assertEqual(str(booking), "alice: Dune seat A1")

    def test_duplicate_seat_number_for_same_movie_rejected(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Seat.objects.create(movie=self.movie, seat_number="A1")

    def test_same_seat_number_allowed_for_different_movie(self):
        other = make_movie("Arrival")
        Seat.objects.create(movie=other, seat_number="A1")  # should not raise
        self.assertEqual(Seat.objects.filter(seat_number="A1").count(), 2)

    def test_seat_cannot_have_two_bookings(self):
        Booking.objects.create(movie=self.movie, seat=self.seat, user=self.user)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Booking.objects.create(movie=self.movie, seat=self.seat, user=self.user)

    def test_deleting_movie_deletes_its_seats(self):
        movie = make_movie("Temp")
        Seat.objects.create(movie=movie, seat_number="B1")
        movie.delete()
        self.assertFalse(Seat.objects.filter(seat_number="B1").exists())


# ------------- Integration tests -----------

class APITestBase(APITestCase):
    """Shared data for all API tests: two movies, three seats, two users."""

    @classmethod
    def setUpTestData(cls):
        cls.movie = make_movie()
        cls.other_movie = make_movie("Arrival")
        cls.seat_a1 = Seat.objects.create(movie=cls.movie, seat_number="A1")
        cls.seat_a2 = Seat.objects.create(movie=cls.movie, seat_number="A2")
        cls.other_seat = Seat.objects.create(movie=cls.other_movie, seat_number="A1")
        cls.alice = User.objects.create_user("alice", password="pass12345")
        cls.bob = User.objects.create_user("bob", password="pass12345")


class MovieAPITests(APITestBase):

    def test_list_movies_anonymous(self):
        response = self.client.get(reverse("movie-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_movie(self):
        response = self.client.get(reverse("movie-detail", args=[self.movie.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Dune")

    def test_create_movie_requires_login(self):
        response = self.client.post(reverse("movie-list"), {"title": "X"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_movie_logged_in(self):
        self.client.force_authenticate(self.alice)
        data = {"title": "Heat", "description": "Crime film.",
                "release_date": "1995-12-15", "duration": 170}
        response = self.client.post(reverse("movie-list"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Movie.objects.filter(title="Heat").exists())

    def test_create_movie_missing_fields(self):
        self.client.force_authenticate(self.alice)
        response = self.client.post(reverse("movie-list"), {"title": "Incomplete"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_movie(self):
        self.client.force_authenticate(self.alice)
        url = reverse("movie-detail", args=[self.movie.id])
        response = self.client.patch(url, {"duration": 155})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.duration, 155)

    def test_delete_movie(self):
        self.client.force_authenticate(self.alice)
        response = self.client.delete(reverse("movie-detail", args=[self.movie.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class SeatAPITests(APITestBase):

    def test_filter_seats_by_movie(self):
        response = self.client.get(reverse("seat-list"), {"movie": self.movie.id})
        self.assertEqual(len(response.data), 2)

    def test_filter_available_seats(self):
        self.seat_a1.is_booked = True
        self.seat_a1.save()
        response = self.client.get(reverse("seat-list"),
                                   {"movie": self.movie.id, "available": "true"})
        self.assertEqual([s["seat_number"] for s in response.data], ["A2"])

    def test_book_action_books_seat(self):
        self.client.force_authenticate(self.alice)
        response = self.client.post(reverse("seat-book", args=[self.seat_a1.id]))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.seat_a1.refresh_from_db()
        self.assertTrue(self.seat_a1.is_booked)

    def test_book_action_rejects_booked_seat(self):
        self.client.force_authenticate(self.alice)
        self.client.post(reverse("seat-book", args=[self.seat_a1.id]))
        response = self.client.post(reverse("seat-book", args=[self.seat_a1.id]))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_book_action_requires_login(self):
        response = self.client.post(reverse("seat-book", args=[self.seat_a1.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_is_booked_cannot_be_set_directly(self):
        self.client.force_authenticate(self.alice)
        url = reverse("seat-detail", args=[self.seat_a1.id])
        self.client.patch(url, {"is_booked": True})
        self.seat_a1.refresh_from_db()
        self.assertFalse(self.seat_a1.is_booked)


class BookingAPITests(APITestBase):

    def book(self, seat, movie=None):
        """Helper: POST a booking for the logged-in user."""
        movie = movie or self.movie
        return self.client.post(reverse("booking-list"),
                                {"movie": movie.id, "seat": seat.id})

    def test_requires_login(self):
        response = self.client.get(reverse("booking-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_booking(self):
        self.client.force_authenticate(self.alice)
        response = self.book(self.seat_a1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["movie_title"], "Dune")
        self.seat_a1.refresh_from_db()
        self.assertTrue(self.seat_a1.is_booked)

    def test_double_booking_rejected(self):
        self.client.force_authenticate(self.alice)
        self.book(self.seat_a1)
        response = self.book(self.seat_a1)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Booking.objects.count(), 1)

    def test_seat_from_other_movie_rejected(self):
        self.client.force_authenticate(self.alice)
        response = self.book(self.other_seat, movie=self.movie)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_book_as_another_user(self):
        self.client.force_authenticate(self.alice)
        self.client.post(reverse("booking-list"),
                         {"movie": self.movie.id, "seat": self.seat_a1.id,
                          "user": self.bob.id})
        self.assertEqual(Booking.objects.get().user, self.alice)

    def test_history_only_shows_own_bookings(self):
        Booking.objects.create(movie=self.movie, seat=self.seat_a2, user=self.bob)
        self.client.force_authenticate(self.alice)
        self.book(self.seat_a1)
        response = self.client.get(reverse("booking-list"))
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["seat_number"], "A1")

    def test_cannot_view_another_users_booking(self):
        booking = Booking.objects.create(movie=self.movie, seat=self.seat_a2, user=self.bob)
        self.client.force_authenticate(self.alice)
        response = self.client.get(reverse("booking-detail", args=[booking.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cancel_booking_frees_seat(self):
        self.client.force_authenticate(self.alice)
        booking_id = self.book(self.seat_a1).data["id"]
        response = self.client.delete(reverse("booking-detail", args=[booking_id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.seat_a1.refresh_from_db()
        self.assertFalse(self.seat_a1.is_booked)

    def test_editing_booking_not_allowed(self):
        self.client.force_authenticate(self.alice)
        booking_id = self.book(self.seat_a1).data["id"]
        response = self.client.put(reverse("booking-detail", args=[booking_id]), {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


# ----- Template view tests ---------

class TemplateViewTests(TestCase):
    """The HTML pages: rendering, login protection, and booking via the form."""

    @classmethod
    def setUpTestData(cls):
        cls.movie = make_movie()
        cls.seat = Seat.objects.create(movie=cls.movie, seat_number="A1")
        cls.alice = User.objects.create_user("alice", password="pass12345")
        cls.bob = User.objects.create_user("bob", password="pass12345")

    def test_movie_list_page(self):
        response = self.client.get(reverse("movie_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bookings/movie_list.html")
        self.assertContains(response, "Dune")

    def test_book_seat_redirects_anonymous_to_login(self):
        response = self.client.get(reverse("book_seat", args=[self.movie.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_book_seat_page_shows_seats(self):
        self.client.force_login(self.alice)
        response = self.client.get(reverse("book_seat", args=[self.movie.id]))
        self.assertTemplateUsed(response, "bookings/seat_booking.html")
        self.assertContains(response, "A1")

    def test_book_seat_unknown_movie_404(self):
        self.client.force_login(self.alice)
        response = self.client.get(reverse("book_seat", args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_booking_through_form(self):
        self.client.force_login(self.alice)
        response = self.client.post(reverse("book_seat", args=[self.movie.id]),
                                    {"seat": self.seat.id})
        self.assertRedirects(response, reverse("booking_history"))
        self.seat.refresh_from_db()
        self.assertTrue(self.seat.is_booked)

    def test_booking_taken_seat_shows_error(self):
        Booking.objects.create(movie=self.movie, seat=self.seat, user=self.bob)
        self.seat.is_booked = True
        self.seat.save()
        self.client.force_login(self.alice)
        response = self.client.post(reverse("book_seat", args=[self.movie.id]),
                                    {"seat": self.seat.id}, follow=True)
        self.assertContains(response, "already booked")
        self.assertEqual(Booking.objects.count(), 1)

    def test_booking_without_seat_does_nothing(self):
        self.client.force_login(self.alice)
        self.client.post(reverse("book_seat", args=[self.movie.id]), {})
        self.assertEqual(Booking.objects.count(), 0)

    def test_history_page_shows_only_own_bookings(self):
        Booking.objects.create(movie=self.movie, seat=self.seat, user=self.bob)
        self.client.force_login(self.alice)
        response = self.client.get(reverse("booking_history"))
        self.assertContains(response, "haven")  # the empty-state message
        self.assertNotContains(response, "badge bg-success")