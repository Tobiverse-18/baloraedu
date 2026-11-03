
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import override_settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


User = get_user_model()


class UserRegistrationAPITests(APITestCase):

    def setUp(self):
        self.register_url = reverse("register")

        self.password = "N0tCommon!Password-2026"

        self.registration_data = {
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "phone_number": "08012345678",
            "password": self.password,
            "password_confirmation": self.password,
        }

    def test_user_can_register_successfully(self):
        response = self.client.post(
            self.register_url,
            self.registration_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(
            User.objects.filter(
                email="newuser@example.com"
            ).exists()
        )

        self.assertNotIn("password", response.data)
        self.assertNotIn("password_confirmation", response.data)

    def test_duplicate_email_registration_is_rejected(self):
        User.objects.create_user(
            email="newuser@example.com",
            password=self.password,
            first_name="Existing",
            last_name="User",
        )

        response = self.client.post(
            self.register_url,
            self.registration_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(
            User.objects.filter(
                email="newuser@example.com"
            ).count(),
            1,
        )

    def test_password_confirmation_must_match(self):
        data = self.registration_data.copy()
        data["password_confirmation"] = "DifferentPassword123!"

        response = self.client.post(
            self.register_url,
            data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn("password_confirmation", response.data)

    def test_weak_password_is_rejected(self):
        data = self.registration_data.copy()
        data["password"] = "password"
        data["password_confirmation"] = "password"

        response = self.client.post(
            self.register_url,
            data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn("password", response.data)

    def test_registered_password_is_hashed(self):
        response = self.client.post(
            self.register_url,
            self.registration_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(
            email="newuser@example.com"
        )

        self.assertNotEqual(user.password, self.password)
        self.assertTrue(user.check_password(self.password))


class UserAuthenticationAPITests(APITestCase):

    def setUp(self):
        self.login_url = reverse("login")
        self.refresh_url = reverse("token_refresh")
        self.logout_url = reverse("token_blacklist")
        self.profile_url = reverse("user_profile")

        self.password = "N0tCommon!Password-2026"

        self.user = User.objects.create_user(
            email="member@example.com",
            password=self.password,
            first_name="Test",
            last_name="Member",
            phone_number="08012345678",
        )

    def login(self):
        return self.client.post(
            self.login_url,
            {
                "email": self.user.email,
                "password": self.password,
            },
            format="json",
        )

    def test_user_can_login_with_email(self):
        response = self.login()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)

        self.assertEqual(
            response.data["user"]["email"],
            self.user.email,
        )

    def test_invalid_credentials_are_rejected(self):
        response = self.client.post(
            self.login_url,
            {
                "email": self.user.email,
                "password": "WrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_inactive_user_cannot_login(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        response = self.login()

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_requires_authentication(self):
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_access_profile(self):
        login_response = self.login()

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        access_token = login_response.data["access"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            response.data["email"],
            self.user.email,
        )

        self.assertNotIn("password", response.data)

    def test_refresh_token_rotation_blacklists_old_token(self):
        login_response = self.login()

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        old_refresh_token = login_response.data["refresh"]

        refresh_response = self.client.post(
            self.refresh_url,
            {"refresh": old_refresh_token},
            format="json",
        )

        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)

        new_refresh_token = refresh_response.data["refresh"]

        self.assertNotEqual(
            old_refresh_token,
            new_refresh_token,
        )

        old_token_response = self.client.post(
            self.refresh_url,
            {"refresh": old_refresh_token},
            format="json",
        )

        self.assertEqual(
            old_token_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_logout_blacklists_refresh_token(self):
        login_response = self.login()

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        refresh_token = login_response.data["refresh"]

        logout_response = self.client.post(
            self.logout_url,
            {"refresh": refresh_token},
            format="json",
        )

        self.assertEqual(
            logout_response.status_code,
            status.HTTP_200_OK,
        )

        refresh_response = self.client.post(
            self.refresh_url,
            {"refresh": refresh_token},
            format="json",
        )

        self.assertEqual(
            refresh_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
)
class PasswordResetAPITests(APITestCase):

    def setUp(self):
        self.request_url = reverse("password_reset")
        self.confirm_url = reverse("password_reset_confirm")

        self.old_password = "N0tCommon!Password-2026"
        self.new_password = "N3wStrong!Password-2026"

        self.user = User.objects.create_user(
            email="resetuser@example.com",
            password=self.old_password,
            first_name="Reset",
            last_name="User",
        )

    def get_reset_data(self, token=None):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))

        if token is None:
            token = default_token_generator.make_token(self.user)

        return {
            "uid": uid,
            "token": token,
            "new_password": self.new_password,
            "password_confirmation": self.new_password,
        }

    def test_registered_user_receives_password_reset_email(self):
        response = self.client.post(
            self.request_url,
            {"email": self.user.email},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)

        self.assertEqual(
            mail.outbox[0].to,
            [self.user.email],
        )

        self.assertIn(
            "Reset your BaloraEdu password",
            mail.outbox[0].subject,
        )

    def test_unknown_email_returns_generic_success_response(self):
        response = self.client.post(
            self.request_url,
            {"email": "unknown@example.com"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 0)

        self.assertIn("detail", response.data)

    def test_valid_reset_token_changes_password(self):
        reset_data = self.get_reset_data()

        response = self.client.post(
            self.confirm_url,
            reset_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(self.new_password)
        )

        self.assertFalse(
            self.user.check_password(self.old_password)
        )

    def test_invalid_reset_token_is_rejected(self):
        reset_data = self.get_reset_data(
            token="invalid-token"
        )

        response = self.client.post(
            self.confirm_url,
            reset_data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(self.old_password)
        )

    def test_password_confirmation_must_match(self):
        reset_data = self.get_reset_data()
        reset_data["password_confirmation"] = "DifferentPassword123!"

        response = self.client.post(
            self.confirm_url,
            reset_data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "password_confirmation",
            response.data,
        )

    def test_weak_new_password_is_rejected(self):
        reset_data = self.get_reset_data()
        reset_data["new_password"] = "password"
        reset_data["password_confirmation"] = "password"

        response = self.client.post(
            self.confirm_url,
            reset_data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn("new_password", response.data)

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(self.old_password)
        )

    def test_password_reset_blacklists_existing_refresh_tokens(self):
        from rest_framework_simplejwt.tokens import RefreshToken

        # Create a refresh token before resetting the password.
        refresh_token = str(RefreshToken.for_user(self.user))

        reset_data = self.get_reset_data()

        response = self.client.post(
            self.confirm_url,
            reset_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # The old refresh token must no longer work.
        refresh_response = self.client.post(
            reverse("token_refresh"),
            {"refresh": refresh_token},
            format="json",
        )

        self.assertEqual(
            refresh_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )