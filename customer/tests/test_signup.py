"""Provide test for signup."""
import django.test
from django.urls import reverse
from django.contrib.auth import get_user_model
from customer.models import Customer

User = get_user_model()


class SignUpViewTests(django.test.TestCase):
    """Test Signup View."""

    def setUp(self):
        """Set up the signup URL for tests."""
        self.signup_url = reverse('customer:signup')

    def test_signup_valid(self):
        """Test signup with valid form."""
        form_data = {'username': 'testuser',
                     'email': 'testuser@example.com',
                     'password1': 'thispass123',
                     'password2': 'thispass123'}
        response = self.client.post(self.signup_url, form_data)

        # Check that the user was created
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get(pk=1)
        self.assertEqual(user.username, 'testuser')
        # Check that the business was created
        self.assertEqual(Customer.objects.count(), 1)
        customer = Customer.objects.get(pk=1)
        self.assertEqual(customer.user, user)
        # Check redirection after successful signup
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('customer:home'))
        # Check successfully login with this user
        login_response = self.client.post(reverse('customer:login'), {
            'username': 'testuser',
            'password': 'thispass123',
        })
        self.assertRedirects(login_response, reverse('customer:home'))

    def test_signup_invalid(self):
        """Test signup with invalid form, missing some fields."""
        response = self.client.post(self.signup_url, {
            'username': '',
            'email': 'testuser@example.com',
            'password1': 'securepassword123',
            'password2': '',
        })

        # Check that the user and business was not created
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(Customer.objects.count(), 0)

        # Check redirection back to signup page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('customer:signup'))
