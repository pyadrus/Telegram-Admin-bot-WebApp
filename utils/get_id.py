# -*- coding: utf-8 -*-
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

from system.dispatcher import api_id, api_hash

client = TelegramClient('setting/session_name', api_id, api_hash)


async def get_participants_count(channel_username_or_id):
    entity = await client.get_entity(channel_username_or_id)
    print(entity.id)  # ID канала
    print(entity.title)  # Название канала
    # Получаем первых 0 участников — достаточно для подсчёта
    participants = await client(
        GetParticipantsRequest(channel=entity, filter=ChannelParticipantsSearch(''), offset=0, limit=0, hash=0))
    return participants.count


async def getting_data(channel_username):
    total = await get_participants_count(channel_username)
    print(f"Количество участников в '{channel_username}': {total}")
