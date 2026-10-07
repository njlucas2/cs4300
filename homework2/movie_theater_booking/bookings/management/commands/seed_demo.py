import datetime
import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from bookings.models import Movie, Seat

MOVIES = [
    {
        "title": "Dune: Part Two",
        "description": "Paul Atreides joins the Fremen and seeks revenge "
                       "against those who destroyed his family.",
        "release_date": datetime.date(2024, 3, 1),
        "duration": 166,
    },
    {
        "title": "Spirited Away",
        "description": "A young girl wanders into a world of spirits and must "
                       "work in a bathhouse to free herself and her parents.",
        "release_date": datetime.date(2001, 7, 20),
        "duration": 125,
    },
    {
        "title": "Inception",
        "description": "A thief who steals secrets through dreams is offered "
                       "a chance to plant an idea instead.",
        "release_date": datetime.date(2010, 7, 16),
        "duration": 148,
    },
]

ROWS = "ABC"
SEATS_PER_ROW = 6


class Command(BaseCommand):
    help = "Create a demo user plus sample movies and seats."

    def handle(self, *args, **options):
        # Demo user
        password = os.environ.get("demo", "1234")
        user, created = User.objects.get_or_create(username="demo")
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write("Created demo user.")

        # Movies and their seats
        for data in MOVIES:
            movie, _ = Movie.objects.get_or_create(title=data["title"], defaults=data)
            for row in ROWS:
                for n in range(1, SEATS_PER_ROW + 1):
                    Seat.objects.get_or_create(movie=movie, seat_number=f"{row}{n}")

        self.stdout.write(self.style.SUCCESS("Demo data ready."))