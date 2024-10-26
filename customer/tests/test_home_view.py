"""Tests for home page."""

from datetime import timedelta
from django.utils import timezone
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from customer.models import Customer, CustomerQueue
from business.models import Business, Queue, Entry


class HomeViewTests(TestCase):
    """Test HomeView."""

    @classmethod
    def setUpTestData(cls):
        """Create setup data for tests."""
        # create three users
        User.objects.create_user(username="testuser1", password="123")
        User.objects.create_user(username="testuser2", password="123")
        User.objects.create_user(username="testuser3", password="123")

        User.objects.create_user(username="owner1", password="123")
        User.objects.create_user(username="owner2", password="123")

        owners = User.objects.filter(username__startswith="owner")
        customers = User.objects.filter(username__startswith="testuser")
        business = ["Teenoi", "Sushiro"]
        queue_type = ["Big", "Small"]
        for customer in User.objects.filter(username__startswith="testuser"):
            Customer.objects.create(user=customer)

        for i in range(len(business)):
            Business.objects.create(user=owners[i], name=business[i])
        for b in Business.objects.all():
            for q in queue_type:
                Queue.objects.create(business=b, name=q, alphabet=q[0])

        current_time = timezone.now()  # Get current time
        time_diff = timedelta(minutes=5)
        entry_counter = 0
        for idx, b in enumerate(Business.objects.all()):

            for q in Queue.objects.filter(business=b):
                for _ in range(len(customers)):
                    # Assign time_in values
                    # (user1 has the earliest time)
                    time_in = (
                        current_time
                        - (idx * time_diff)
                        + timedelta(minutes=entry_counter)
                    )
                    # Create entry
                    Entry.objects.create(
                        # name=q.alphabet, queue=q, business=q.business, time_in=time_in
                        queue=q,
                        business=q.business,
                        time_in=time_in,
                    )
                    entry_counter += 8

    def setUp(self):
        """Log in a test user before each test.

        This method is called before each test, ensuring that the user is authenticated.
        """
        super().setUp()
        self.client.login(username="testuser1", password="123")

    @classmethod
    def create_customer_queue(cls):
        """Create CustomerQueue instances for testing.

        This method populates the CustomerQueue model with entries associated
        with the 'Teenoi' and 'Sushiro' businesses.
        """
        entries = Entry.objects.filter(business__name="Teenoi", queue__name="Big")
        entries2 = Entry.objects.filter(business__name="Sushiro", queue__name="Small")
        customers = Customer.objects.all()
        for i in range(len(customers)):
            CustomerQueue.objects.create(customer=customers[i], entry=entries[i])
            CustomerQueue.objects.create(customer=customers[i], entry=entries2[i])

    def test_authenticated_enter_tracking_code(self):
        """Test that a customer (authenticated user) can add entry to their customer queue.

        As an authenticated user,
        when I enter my tracking code,
        the entry with associate tracking code will belong to me
        and my customer queue will contain this particular queue with status waiting.
        """
        big_entry_teenoi = Entry.objects.filter(
            business__name="Teenoi", queue__name="Big"
        )
        # entry Big Teenoi
        response = self.client.post(
            reverse("customer:home"),
            {"track-code": big_entry_teenoi.first().tracking_code},
            follow=True,
        )
        customer_queue = CustomerQueue.objects.filter(
            customer__user__username="testuser1"
        )
        expected_queue_added = CustomerQueue.objects.get(
            customer__user__username="testuser1", entry=big_entry_teenoi.first()
        )
        self.assertIn(
            expected_queue_added,
            customer_queue,
            "The expected entry was not found in the customer queue.",
        )

        # Follow the redirect
        self.assertRedirects(response, reverse("customer:home"))

        self.assertQuerySetEqual(
            response.context["customer_queue_list"], [expected_queue_added]
        )

        self.assertContains(response, "This entry is added to your queue history.")

    def test_visitor_enter_tracking_code(self):
        """Test that visitor can see queue based on tracking code,
        but it won't be saved into their customer queue.
        """
        self.client.logout()
        HomeViewTests.create_customer_queue()

        big_entry_teenoi = Entry.objects.filter(
            business__name="Teenoi", queue__name="Big"
        )

        response = self.client.post(
            reverse("customer:home"),
            {"track-code": big_entry_teenoi.first().tracking_code},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        expected_queue_added = CustomerQueue.objects.get(
            entry__tracking_code=big_entry_teenoi.first().tracking_code
        )
        self.assertIn(expected_queue_added, response.context["customer_queue_list"])

    def test_access_wrong_tracking_code(self):
        """Test that users receive error messages when entered invalid tracking code."""
        response = self.client.post(
            reverse("customer:home"), {"track-code": "wrong-code"}, follow=True
        )
        self.assertContains(response, "The track code is incorrect.", status_code=200)

        # visitors
        self.client.logout()
        response = self.client.post(
            reverse("customer:home"), {"track-code": "wrong-code"}, follow=True
        )
        self.assertContains(response, "The track code is incorrect.", status_code=200)

    def test_user_add_same_tracking_code(self):
        """Test that user cannot add the same tracking code to CustomerQueue
        and other people cannot add other people tracking code into their CustomerQueue.
        """
        HomeViewTests.create_customer_queue()
        big_entry_teenoi = Entry.objects.filter(
            business__name="Teenoi", queue__name="Big"
        )
        username = self.client.session["_auth_user_id"]  # Get the user ID
        user = User.objects.get(
            pk=username
        )  # Fetch the user object to get the username

        self.client.post(
            reverse("customer:home"),
            {"track-code": big_entry_teenoi.first().tracking_code},
            follow=True,
        )

        self.assertEqual(
            CustomerQueue.objects.filter(
                customer__user=user,
                entry__tracking_code=big_entry_teenoi.first().tracking_code,
            ).count(),
            1,
        )

        self.client.logout()
        self.client.login(username="testuser2", password="123")
        response = self.client.post(
            reverse("customer:home"),
            {"track-code": big_entry_teenoi.first().tracking_code},
            follow=True,
        )
        self.assertContains(
            response, "You can&#x27;t access someone else entry!", status_code=200
        )

    def test_cancel_not_owner(self):
        """Test that only the owner of entry can cancel their queue
        and cannot delete entries that haven't been added to customer queue.
        """
        HomeViewTests.create_customer_queue()
        big_entry_teenoi = Entry.objects.filter(
            business__name="Teenoi", queue__name="Big"
        )
        self.client.logout()
        self.client.login(username="testuser2", password="123")  # not owner of entry

        response = self.client.post(
            reverse(
                "customer:cancel-queue",
                kwargs={"entry_id": big_entry_teenoi.first().id},
            ),
            follow=True,
        )
        self.assertContains(
            response, "You do not have the authority to delete this entry."
        )
        self.assertEqual(
            CustomerQueue.objects.filter(entry__id=big_entry_teenoi.first().id).count(),
            1,
        )

        response = self.client.post(
            reverse(
                "customer:cancel-queue",
                kwargs={"entry_id": big_entry_teenoi.first().id},
            ),
            follow=True,
        )
        self.assertContains(
            response, "You do not have the authority to delete this entry."
        )

        # Entry that hasn't been added to the customer queue can't
        # be canceled by the user.
        response = self.client.post(
            reverse("customer:cancel-queue", kwargs={"entry_id": 5}), follow=True
        )
        self.assertContains(response, "This entry does not exist in customer queue.")
        self.assertEqual(Entry.objects.filter(id=5).count(), 1)

    def test_cancel_visitor(self):
        """Visitor cannot cancel any entry."""
        HomeViewTests.create_customer_queue()
        big_entry_teenoi = Entry.objects.filter(
            business__name="Teenoi", queue__name="Big"
        )
        self.client.logout()
        response = self.client.post(
            reverse(
                "customer:cancel-queue",
                kwargs={"entry_id": big_entry_teenoi.first().id},
            ),
            follow=True,
        )
        self.assertContains(
            response, "You do not have the authority to delete this entry."
        )
        self.assertEqual(
            CustomerQueue.objects.filter(entry__id=big_entry_teenoi.first().id).count(),
            1,
        )

        # Entry that hasn't been added to the customer queue can't be canceled
        # by the user.
        response = self.client.post(
            reverse("customer:cancel-queue", kwargs={"entry_id": 5}), follow=True
        )
        self.assertContains(response, "This entry does not exist in customer queue.")
        self.assertEqual(Entry.objects.filter(id=5).count(), 1)

    def test_cancel_other_status(self):
        """Test that user cannot cancel other status (not waiting)."""
        HomeViewTests.create_customer_queue()
        small_queue_sushiro = CustomerQueue.objects.filter(
            entry__business__name="Sushiro", entry__queue__name="Small"
        ).last()

        small_queue_sushiro.entry.status = "checked in"
        small_queue_sushiro.entry.save()

        self.client.logout()

        response = self.client.post(
            reverse(
                "customer:cancel-queue",
                kwargs={"entry_id": small_queue_sushiro.entry.id},
            ),
            follow=True,
        )
        self.assertEqual(
            Entry.objects.filter(id=small_queue_sushiro.entry.id).count(), 1
        )

        self.client.login()
        self.client.login(username="testuser3", password="123")
        response = self.client.post(
            reverse(
                "customer:cancel-queue",
                kwargs={"entry_id": small_queue_sushiro.entry.id},
            ),
            follow=True,
        )
        self.assertEqual(
            Entry.objects.filter(id=small_queue_sushiro.entry.id).count(), 1
        )
        self.assertContains(response, "You cannot to cancel this entry.")

    def test_get_queue_before(self):
        """Check if the queue is retrieved correctly under specified conditions."""
        HomeViewTests.create_customer_queue()
        small_queue_zero = CustomerQueue.objects.filter(
            entry__business__name="Sushiro", entry__queue__name="Small"
        ).first()

        small_queue_one = CustomerQueue.objects.filter(
            entry__business__name="Sushiro", entry__queue__name="Small"
        )[1]

        small_queue_last = CustomerQueue.objects.filter(
            entry__business__name="Sushiro", entry__queue__name="Small"
        ).last()

        self.assertEqual(small_queue_last.entry.get_queue_position(), 2)
        self.assertEqual(small_queue_zero.entry.get_queue_position(), 0)

        small_queue_one.entry.status = "checked in"
        small_queue_one.entry.save()
        self.assertEqual(small_queue_last.entry.get_queue_position(), 1)

        small_queue_last.entry.status = "checked in"
        small_queue_last.entry.save()
        self.assertEqual(small_queue_last.entry.get_queue_position(), 1)
