Feature: Booking movie seats
  As a moviegoer
  I want to reserve a seat for a movie
  So that I have a guaranteed spot at the showing

  Background:
    Given a movie called "Dune" with seats "A1" and "A2"

  Scenario: Booking an available seat
    Given I am logged in as "alice"
    When I book seat "A1"
    Then seat "A1" should be booked
    And I should see "Booked seat A1 for Dune!"

  Scenario: Trying to book a seat someone else has
    Given seat "A1" is already booked by "bob"
    And I am logged in as "alice"
    When I book seat "A1"
    Then I should see "already booked"
    And I should have 0 bookings

  Scenario: Seeing my booking history
    Given I am logged in as "alice"
    When I book seat "A2"
    And I visit my booking history
    Then I should see "Dune"
    And I should have 1 bookings