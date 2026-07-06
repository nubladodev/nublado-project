from django_nublado_telegram.models import TelegramGroupMember
from django_nublado_telegram.utils.async_utils import async_call


async def transfer_points(tg_chat, tg_member_sender, tg_member_receiver, num_points):
    """
    Persist points transfer in the database.
    Returns sender_member, receiver_member 
    TelegramGroupMember objects from the ORM.
    """

    sender_member, created = await async_call(
        TelegramGroupMember.objects.get_or_create_from_chat_member,
        tg_member_sender,
        tg_chat
    )
    

    receiver_member, created = await async_call(
        TelegramGroupMember.objects.get_or_create_from_chat_member,
        tg_member_receiver,
        tg_chat
    )

    # Increment points
    receiver_member.points += num_points
    await receiver_member.asave()

    return sender_member, receiver_member
