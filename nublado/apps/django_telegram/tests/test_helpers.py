from types import SimpleNamespace

from telegram.constants import ChatType, ChatMemberStatus

from django_telegram.utils.helpers import (
    _is_group,
    _is_private,
    _is_admin,
    _is_group_owner,
    message_link,
)


class TestHelpers:
    def test_is_group_and_is_private(self):
        group_chat = SimpleNamespace(type=ChatType.GROUP)
        supergroup_chat = SimpleNamespace(type=ChatType.SUPERGROUP)
        private_chat = SimpleNamespace(type=ChatType.PRIVATE)

        assert _is_group(group_chat)
        assert _is_group(supergroup_chat)
        assert not _is_group(private_chat)

        assert _is_private(private_chat)
        assert not _is_private(group_chat)
        assert not _is_private(supergroup_chat)

    def test_is_admin_and_is_group_owner(self):
        owner = SimpleNamespace(status=ChatMemberStatus.OWNER)
        admin = SimpleNamespace(status=ChatMemberStatus.ADMINISTRATOR)
        member = SimpleNamespace(status=ChatMemberStatus.MEMBER)

        assert _is_admin(owner)
        assert _is_admin(admin)
        assert not _is_admin(member)

        assert _is_group_owner(owner)
        assert not _is_group_owner(admin)
        assert not _is_group_owner(member)

    def test_message_link(self):
        tg_chat_id = "12345"
        tg_message_id = "6789"
        assert (
            message_link(tg_chat_id, tg_message_id)
            == f"https://t.me/c/{tg_chat_id}/{tg_message_id}"
        )
        tg_chat_id = "-100123456789"
        tg_message_id = "6789"
        # Cut off the -100 in chat id.
        assert (
            message_link("-100123456789", "6789")
            == f"https://t.me/c/{tg_chat_id[4:]}/{tg_message_id}"
        )
