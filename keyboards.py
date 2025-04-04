from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

class FilmCallback(CallbackData, prefix="film", sep=";"):
    id: int
    name: str


def films_keyboard_markup(films_list: list[dict], offset: int | None = None, skip: int | None = None):
    builder = InlineKeyboardBuilder()
    for film_data in films_list:
        callback_data = FilmCallback(**film_data)
        builder.button(
            text=f"{callback_data.name}",
            callback_data=callback_data.pack()
        )
    builder.adjust(1, repeat=True)
    return builder.as_markup()
