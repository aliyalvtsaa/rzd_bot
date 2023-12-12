from aiogram.types import reply_keyboard_markup, keyboard_button, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from rzd_parse_first_time import handle_request

async def trains(first_message_from_user):
    trains_kb = InlineKeyboardBuilder()
    trains = await handle_request(first_message_from_user)

    for key, value in trains.items():
        button_text = f"{key}⏰ {value}"
        trains_kb.add(InlineKeyboardButton(text=button_text, callback_data=key))
    final_button = InlineKeyboardButton(text="Все поезда выбраны", callback_data="final_choice")
    trains_kb.add(final_button)
    return trains_kb.adjust(1).as_markup(resize_keyboard = True)


