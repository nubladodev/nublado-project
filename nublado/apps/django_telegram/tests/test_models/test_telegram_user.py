import pytest

from django_telegram.models import TelegramUser


class TestTelegramUser:
    """
    Tests for the TelegramUser model.
    """

    pytestmark = pytest.mark.django_db

    def test_pk(self):
        """
        telegram_id is the primary key
        """
        assert TelegramUser._meta.pk.name == "telegram_id"

    def test_create_user_defaults(self):
        """
        Create a TelegramUser object and check its default values.
        """
        user = TelegramUser.objects.create(telegram_id=1)
        assert user.telegram_id == 1
        assert user.is_bot is False
        assert user.date_created is not None
        assert user.date_updated is not None

    def test_display_name(self):
        user = TelegramUser.objects.create(telegram_id=111, first_name="firstname1")
        assert user.display_name == user.first_name

        user = TelegramUser.objects.create(telegram_id=222, username="username2", first_name="firstname2")
        assert user.display_name == f"@{user.username}"

        user = TelegramUser.objects.create(telegram_id=333, first_name="firstname3", last_name="lastname3")
        assert user.display_name == f"{user.first_name} {user.last_name}"


    def test_str_representation(self):
        """
        __str__ returns username, or telegram_id if username doesn't exist.
        """
        user = TelegramUser.objects.create(telegram_id=111, first_name="foo", username="foo")
        assert str(user) == f"{user.display_name} : {user.telegram_id}"