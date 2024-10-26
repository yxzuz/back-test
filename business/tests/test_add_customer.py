from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from business.models import Business, Queue, Entry


class AddCustomerViewTest(TestCase):
    """Tests for the add_customer view."""

    def setUp(self):
        """Set up test data for all tests."""
        self.user = User.objects.create_user(username="testuser", password="password")
        self.business = Business.objects.create(user=self.user, name="Test Business")
        self.queue = Queue.objects.create(
            business=self.business, name="Test Queue", alphabet="A"
        )

    def test_no_queue_redirect_to_home(self):
        """Test redirect to home if no queue exists."""
        self.client.login(username="testuser", password="password")
        Queue.objects.all().delete()
        response = self.client.get(reverse("business:add_customer"))
        self.assertRedirects(response, reverse("business:home"))

    def test_display_queues_if_exists(self):
        """Test queue display if queues exist."""
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse("business:add_customer"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "business/add_customer.html")
        self.assertIn("queues", response.context)
        self.assertEqual(response.context["queues"].count(), 1)

    def test_post_request_adds_customer(self):
        """Test adding a customer with POST request."""
        self.client.login(username="testuser", password="password")
        response = self.client.post(
            reverse("business:add_customer"), {"queue": self.queue.id}
        )
        self.assertEqual(Entry.objects.count(), 1)
        entry = Entry.objects.first()
        self.assertEqual(entry.queue, self.queue)
        self.assertEqual(entry.business, self.business)
        self.assertIsNotNone(entry.tracking_code)
        self.assertEqual(entry.status, "waiting")

        self.assertEqual(response.status_code, 200)
        self.assertIn("tracking_code", response.context)
