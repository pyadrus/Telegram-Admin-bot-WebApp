# -*- coding: utf-8 -*-
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

from system.dispatcher import api_id, api_hash


async def get_participants_count(chat_link):
    async with TelegramClient('setting/session_name', api_id, api_hash) as client:
        try:
            entity = await client.get_entity(chat_link)
            participants = await client(
                GetParticipantsRequest(
                    channel=entity,
                    filter=ChannelParticipantsSearch(''),
                    offset=0,
                    limit=0,
                    hash=0
                )
            )
            return entity.id, entity.title, participants.count, chat_link
        except Exception as e:
            raise ValueError(f"Ошибка при получении данных для {chat_link}: {e}")
