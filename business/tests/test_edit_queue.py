from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from business.models import Business, Queue


class EditQueueTest(TestCase):
    """Test case for editing a queue in the business application."""

    def setUp(self):
        """Set up a user, a business and a queue instance for the tests."""
        self.user = User.objects.create_user(username="testuser", password="test1234")
        self.client.login(username="testuser", password="test1234")
        self.business = Business.objects.create(user=self.user, name="test business")
        self.queue = Queue.objects.create(
            business=self.business, name="Dining", alphabet="A", estimated_time=None
        )

    def test_edit_queue_function(self):
        """Test that a valid queue is updated successfully."""
        url = reverse("business:edit_queue", args=[self.queue.pk])
        form = {"name": "Take Away", "alphabet": "B"}

        response = self.client.post(url, form)
        self.queue.refresh_from_db()
        self.assertEqual(self.queue.name, "Take Away")
        self.assertEqual(self.queue.alphabet, "B")
        self.assertRedirects(
            response, reverse("business:home")
        )

    def test_invalid_edit_form_not_save(self):
        """Test that an invalid form does not update a queue."""
        url = reverse("business:edit_queue", args=[self.queue.pk])
        form = {"name": "", "alphabet": "B"}

        response = self.client.post(url, form)
        self.queue.refresh_from_db()
        self.assertEqual(self.queue.name, "Dining")
        self.assertEqual(self.queue.alphabet, "A")
        self.assertTemplateUsed(response, "business/show_entry.html")
