"""Provide test for authentication."""

import django.test
from django.urls import reverse
from django.contrib.auth.models import User
from business.models import Business
from customer.models import Customer


class UserAuthTest(django.test.TestCase):
    """Test authentication system."""

    def setUp(self):
        """Superclass setUp creates a Client object and initializes test database."""
        super().setUp()
        self.email1 = "test@customer.com"
        self.username1 = "customer"
        self.password1 = "1234"
        self.user1 = User.objects.create_user(
            email=self.email1,
            username=self.username1,
            password=self.password1,
        )
        self.user1.save()
        Customer.objects.create(user=self.user1)

        self.email2 = "test@business.com"
        self.business_name = "test shop"
        self.username2 = "business"
        self.password2 = "1234"
        self.user2 = User.objects.create_user(
            email=self.email2,
            username=self.username2,
            password=self.password2,
        )
        self.user2.save()
        Business.objects.create(user=self.user2, name=self.business_name)

    def test_logout(self):
        """A user can log out using the logout url.

        As an authenticated user, when user visit /accounts/logout/
        then user will be logged out and then redirected to the login page.
        """
        logout_url = reverse("customer:logout")
        # Client.login returns true on success
        self.assertTrue(
            self.client.login(username=self.username1, password=self.password1)
        )
        # visit the logout page
        form_data = {}
        response = self.client.post(logout_url, form_data)
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, reverse("customer:home"))

    def test_login_view_with_business(self):
        """A user can log in using the login view with customer account."""
        login_url = reverse("customer:login")
        # Can get the login page
        response = self.client.get(login_url)
        self.assertEqual(200, response.status_code)
        # Can login using a POST request
        form_data = {"username": self.username1, "password": self.password1}
        response = self.client.post(login_url, form_data)
        # after successful login, should redirect browser somewhere
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, reverse("customer:home"))

    def test_login_view_with_customer(self):
        """A user can not log in using the login view with business account."""
        login_url = reverse("customer:login")
        response = self.client.get(login_url)
        self.assertEqual(200, response.status_code)
        form_data = {"username": self.username2, "password": self.password2}
        response = self.client.post(login_url, form_data)
        # after failed login, should redirect to login page
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, reverse("customer:login"))
