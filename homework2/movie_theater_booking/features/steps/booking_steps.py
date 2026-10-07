import datetime

from behave import given, when, then
from django.contrib.auth.models import User
from django.urls import reverse
from bookings.models import Movie, Seat, Booking

@given('a movie called "{title}" with seats "{first}" and "{second}"')
def step_create_movie(context, title, first, second):
    context.movie = Movie.objects.create(
        title=title, description="A test movie.",
        release_date=datetime.date(2024, 3, 1), duration=166,
    )
    for number in (first, second):
        Seat.objects.create(movie=context.movie, seat_number=number)

@given('I am logged in as "{username}"')
def step_login(context, username):
    context.user = User.objects.create_user(username, password="pass12345")
    context.test.client.force_login(context.user)

@given('seat "{seat_number}" is already booked by "{username}"')
def step_seat_taken(context, seat_number, username):
    other = User.objects.create_user(username, password="pass12345")
    seat = Seat.objects.get(movie=context.movie, seat_number=seat_number)
    Booking.objects.create(movie=context.movie, seat=seat, user=other)
    seat.is_booked = True
    seat.save()

@when('I book seat "{seat_number}"')
def step_book(context, seat_number):
    seat = Seat.objects.get(movie=context.movie, seat_number=seat_number)
    context.response = context.test.client.post(
        reverse("book_seat", args=[context.movie.id]),
        {"seat": seat.id}, follow=True,
    )

@when("I visit my booking history")
def step_history(context):
    context.response = context.test.client.get(reverse("booking_history"))

@then('seat "{seat_number}" should be booked')
def step_seat_booked(context, seat_number):
    seat = Seat.objects.get(movie=context.movie, seat_number=seat_number)
    context.test.assertTrue(seat.is_booked)

@then('I should see "{text}"')
def step_see_text(context, text):
    context.test.assertContains(context.response, text)

@then("I should have {count:d} bookings")
def step_booking_count(context, count):
    context.test.assertEqual(
        Booking.objects.filter(user=context.user).count(), count
    )