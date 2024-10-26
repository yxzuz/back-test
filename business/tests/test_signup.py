"""Provide test for signup."""

import django.test
from django.urls import reverse
from django.contrib.auth import get_user_model
from business.models import Business

User = get_user_model()


class SignUpViewTests(django.test.TestCase):
    """Test Signup View."""

    def setUp(self):
        """Set up the signup URL for tests."""
        self.signup_url = reverse('business:signup')

    def test_signup_valid(self):
        """Test signup with valid form."""
        form_data = {'username': 'testuser',
                     'email': 'testuser@example.com',
                     'business_name': 'Test Business',
                     'password1': 'thispass123',
                     'password2': 'thispass123'}
        response = self.client.post(self.signup_url, form_data)

        # Check that the user was created
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get(pk=1)
        self.assertEqual(user.username, 'testuser')
        # Check that the business was created
        self.assertEqual(Business.objects.count(), 1)
        business = Business.objects.get(pk=1)
        self.assertEqual(business.name, 'Test Business')
        # Check redirection after successful signup
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('business:home'))
        # Check successfully login with this user
        login_response = self.client.post(reverse('business:login'), {
            'username': 'testuser',
            'password': 'thispass123',
        })
        self.assertRedirects(login_response, reverse('business:home'))

    def test_signup_invalid(self):
        """Test signup with invalid form, missing some fields."""
        response = self.client.post(self.signup_url, {
            'username': '',
            'email': 'testuser@example.com',
            'business_name': 'Test Business',
            'password1': 'securepassword123',
            'password2': '',
        })

        # Check that the user and business was not created
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(Business.objects.count(), 0)

        # Check redirection back to signup page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('business:signup'))
