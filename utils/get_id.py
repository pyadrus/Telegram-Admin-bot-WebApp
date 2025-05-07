# -*- coding: utf-8 -*-
import configparser
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

config = configparser.ConfigParser()
config.read("config.ini")

api_id = config.get('telegram_settings', 'id')
api_hash = config.get('telegram_settings', 'hash')

client = TelegramClient('session_name', api_id, api_hash)


async def get_participants_count(channel_username_or_id):
    entity = await client.get_entity(channel_username_or_id)
    print(entity.id) # ID канала
    print(entity.title) # Название канала
    # Получаем первых 0 участников — достаточно для подсчёта
    participants = await client(GetParticipantsRequest(channel=entity, filter=ChannelParticipantsSearch(''), offset=0, limit=0, hash=0))
    return participants.count


with client:
    channel_username = "@rabota_rf_ru"  # можно указать ID или username
    total = client.loop.run_until_complete(get_participants_count(channel_username))
    print(f"Количество участников в '{channel_username}': {total}")