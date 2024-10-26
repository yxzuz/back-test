from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from business.models import Business, Queue


class AddQueueTest(TestCase):
    """Test case for adding a queue in the business application."""

    def setUp(self):
        """Set up a user and a business instance for the tests."""
        self.user = User.objects.create_user(username="testuser", password="test1234")
        self.business = Business.objects.create(user=self.user, name="test business")
        self.client.login(username="testuser", password="test1234")

    def test_add_queue_function(self):
        """Test that a valid queue is added successfully."""
        url = reverse("business:add_queue")
        form = {"name": "Dining", "alphabet": "A"}
        response = self.client.post(url, form)
        self.assertEqual(Queue.objects.count(), 1)

        queue = Queue.objects.first()
        self.assertEqual(queue.name, "Dining")
        self.assertEqual(queue.alphabet, "A")
        self.assertEqual(queue.business, self.business)
        self.assertEqual(queue.estimated_time, None)

        self.assertRedirects(
            response, reverse("business:home")
        )

    def test_invalid_form_not_save(self):
        """Test that an invalid form does not create a queue."""
        url = reverse("business:add_queue")
        form = {"name": "", "alphabet": "A"}

        response = self.client.post(url, form)
        self.assertEqual(Queue.objects.count(), 0)
        self.assertTemplateUsed(response, "business/show_entry.html")
