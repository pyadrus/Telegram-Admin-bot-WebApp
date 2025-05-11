from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboard.keyboard import create_admin_panel_keyboard
from messages.translations_loader import translations
from system.dispatcher import router, bot


@router.message(Command("start"))
async def start_command(message: Message, state: FSMContext) -> None:
    await state.clear()  # Сбрасываем состояние FSM

    user_id = message.from_user.id
    keyboard = create_admin_panel_keyboard(user_id)

    await bot.send_message(
        message.chat.id,
        translations["ru"]["menu"]["user"],
        reply_markup=keyboard,
        parse_mode="HTML"
    )
