
import asyncio

from external import async_log_message
from logger import logger

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery, URLInputFile, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from config import BOT_TOKEN as TOKEN
from commands import *
from data import get_films, add_film, FILM_DATA_PATH
from keyboards import films_keyboard_markup, FilmCallback
from models import Film
from states import *
import json


dp = Dispatcher()


@dp.message(SEARCH_FILMS_COMMAND)
async def search_film(message: Message, state: FSMContext) -> None:
    await state.set_state(FilmSort.search_query)
    await message.answer(
        'Enter film name to search.',
        reply_markup=ReplyKeyboardRemove()
    )


@dp.message(FilmSort.search_query)
async def search_query(message: Message, state: FSMContext) -> None:
    query = message.text.lower()
    movies = get_films()
    results = [film for film in movies if query in film['name'].lower()]
    if results:
        await message.reply('Search complete!', reply_markup=films_keyboard_markup(results))
    else:
        await message.reply('Search lose:(')
    await state.clear()


@dp.message(FILTER_FILMS_COMMAND)
async def filter_films(message: Message, state: FSMContext) -> None:
    await state.set_state(FilmFilter.filter_criteria)
    await message.answer(
        "What criteria would you like to filter by?\n"
        "Choose one of the following: genre, rating, or year.",
        reply_markup=ReplyKeyboardRemove()
    )


@dp.message(FilmFilter.filter_criteria)
async def filter_criteria(message: Message, state: FSMContext) -> None:
    criteria = message.text.lower()

    if criteria in ['genre', 'rating', 'year']:
        await state.update_data(criteria=criteria)
        if criteria == 'genre':
            await state.set_state(FilmFilter.genre)
            await message.answer("Enter the genre you'd like to filter by.")
        elif criteria == 'rating':
            await state.set_state(FilmFilter.rating)
            await message.answer("Enter the minimum rating (0-10).")
        elif criteria == 'year':
            await state.set_state(FilmFilter.year)
            await message.answer("Enter the year to filter by.")
    else:
        await message.answer("Invalid criteria. Please choose from: genre, rating, or year.")


@dp.message(FilmFilter.genre)
async def filter_by_genre(message: Message, state: FSMContext) -> None:
    genre = message.text.lower()
    await state.update_data(genre=genre)
    await state.set_state(FilmFilter.filter_criteria)
    movies = get_films()
    filtered_films = [film for film in movies if genre in film['genre'].lower()]
    if filtered_films:
        markup = films_keyboard_markup(films_list=filtered_films)
        await message.answer("Filtered films by genre:", reply_markup=markup)
    else:
        await message.answer("No films found for this genre.")
    await state.clear()


@dp.message(FilmFilter.rating)
async def filter_by_rating(message: Message, state: FSMContext) -> None:
    try:
        rating = float(message.text)
        if 0 <= rating <= 10:
            await state.update_data(rating=rating)
            await state.set_state(FilmFilter.filter_criteria)
            movies = get_films()
            filtered_films = [film for film in movies if film['rating'] >= rating]
            if filtered_films:
                markup = films_keyboard_markup(films_list=filtered_films)
                await message.answer("Filtered films by rating:", reply_markup=markup)
            else:
                await message.answer("No films found with this rating.")
        else:
            await message.answer("Invalid rating. Please enter a number between 0 and 10.")
    except ValueError:
        await message.answer("Invalid rating. Please enter a valid number between 0 and 10.")
    await state.clear()


@dp.message(FilmFilter.year)
async def filter_by_year(message: Message, state: FSMContext) -> None:
    try:
        year = int(message.text)
        await state.update_data(year=year)
        await state.set_state(FilmFilter.filter_criteria)
        movies = get_films()
        filtered_films = [film for film in movies if film['year'] == year]
        if filtered_films:
            markup = films_keyboard_markup(films_list=filtered_films)
            await message.answer(f"Filtered films by year {year}:", reply_markup=markup)
        else:
            await message.answer(f"No films found from the year {year}.")
    except ValueError:
        await message.answer("Invalid year. Please enter a valid number.")
    await state.clear()


def update_films(movies):
    with open(FILM_DATA_PATH, 'w', encoding='utf-8') as file:
        json.dump(movies, file, indent=4, ensure_ascii=False)


@dp.message(EDIT_FILMS_COMMAND)
async def edit_film(message: Message, state: FSMContext) -> None:
    await state.set_state(FilmEdit.edit_query)
    await message.answer(
        "Enter the name of the movie you want to edit:",
        reply_markup=ReplyKeyboardRemove()
    )

@dp.message(FilmEdit.edit_query)
async def edit_film_query(message: Message, state: FSMContext) -> None:
    query = message.text.strip().lower()
    movies = get_films()
    film = next((f for f in movies if query in f['name'].lower()), None)  # Поиск по названию фильма

    if film:
        await state.update_data(film_name=film['name'])
        await state.set_state(FilmEdit.select_field)
        await message.answer(
            f"Film found: {film['name']}. What would you like to edit? "
            f"Please reply with one of the following options:\n"
            "1. Name\n"
            "2. Description\n"
            "3. Rating\n"
            "4. Year\n"
            "5. Genre\n"
            "6. Actors\n"
            "7. Poster URL"
        )
    else:
        await message.answer("Movie not found. Please try again.")


@dp.message(FilmEdit.select_field)
async def select_edit_field(message: Message, state: FSMContext) -> None:
    field = message.text.strip()
    valid_fields = {
        "1": "name",
        "2": "description",
        "3": "rating",
        "4": "year",
        "5": "genre",
        "6": "actors",
        "7": "poster"
    }

    if field not in valid_fields:
        await message.answer("Invalid option. Please choose one of the following options:\n"
                             "1. Name\n"
                             "2. Description\n"
                             "3. Rating\n"
                             "4. Year\n"
                             "5. Genre\n"
                             "6. Actors\n"
                             "7. Poster URL")
        return


    field_name = valid_fields[field]
    await state.update_data(field=field_name)
    name = (await state.get_data())['film_name']
    movies = get_films()
    film = next(f for f in movies if f['name'] == name)
    if field_name == "name":
        await state.set_state(FilmEdit.name)
        await message.answer(f"Enter the new name for {film['name']}:")
    elif field_name == "description":
        await state.set_state(FilmEdit.description)
        await message.answer(f"Enter the new description for {film['name']}:")
    elif field_name == "rating":
        await state.set_state(FilmEdit.rating)
        await message.answer(f"Enter the new rating for {film['name']}:")
    elif field_name == "year":
        await state.set_state(FilmEdit.year)
        await message.answer(f"Enter the new year for {film['name']}:")
    elif field_name == "genre":
        await state.set_state(FilmEdit.genre)
        await message.answer(f"Enter the new genre for {film['name']}:")
    elif field_name == "actors":
        await state.set_state(FilmEdit.actors)
        await message.answer(f"Enter the new actors for {film['name']} (comma separated):")
    elif field_name == "poster":
        await state.set_state(FilmEdit.poster)
        await message.answer(f"Enter the new poster URL for {film['name']}:")


@dp.message(FilmEdit.name)
async def edit_film_name(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    name = data['film_name']
    movies = get_films()
    film = next(f for f in movies if f['name'] == name)
    new_name = message.text.strip() if message.text.strip() else film['name']
    film['name'] = new_name
    await state.update_data(name=new_name)
    update_films(movies)
    await state.clear()
    await message.answer(f"Film {film['name']} updated successfully!")


@dp.message(FilmEdit.description)
async def edit_film_description(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    name = data['film_name']
    movies = get_films()
    film = next(f for f in movies if f['name'] == name)
    new_description = message.text.strip() if message.text.strip() else film['description']
    film['description'] = new_description
    await state.update_data(description=new_description)
    update_films(movies)
    await state.clear()
    await message.answer(f"Description for {film['name']} updated successfully!")


@dp.message(FilmEdit.rating)
async def edit_film_rating(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    name = data['film_name']
    movies = get_films()
    film = next(f for f in movies if f['name'] == name)
    try:
        new_rating = float(message.text.strip()) if message.text.strip() else film['rating']
        film['rating'] = new_rating
        await state.update_data(rating=new_rating)
        update_films(movies)
        await state.clear()
        await message.answer(f"Rating for {film['name']} updated successfully!")
    except ValueError:
        await message.answer("Invalid rating. Please enter a valid number.")


@dp.message(FilmEdit.year)
async def edit_film_year(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    name = data['film_name']
    movies = get_films()
    film = next(f for f in movies if f['name'] == name)
    try:
        new_year = int(message.text.strip()) if message.text.strip() else film['year']
        film['year'] = new_year
        await state.update_data(year=new_year)
        update_films(movies)
        await state.clear()
        await message.answer(f"Year for {film['name']} updated successfully!")
    except ValueError:
        await message.answer("Invalid year. Please enter a valid number.")


@dp.message(FilmEdit.genre)
async def edit_film_genre(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    name = data['film_name']
    movies = get_films()
    film = next(f for f in movies if f['name'] == name)
    new_genre = message.text.strip() if message.text.strip() else film['genre']
    film['genre'] = new_genre
    await state.update_data(genre=new_genre)
    update_films(movies)
    await state.clear()
    await message.answer(f"Genre for {film['name']} updated successfully!")


@dp.message(FilmEdit.actors)
async def edit_film_actors(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    name = data['film_name']
    movies = get_films()
    film = next(f for f in movies if f['name'] == name)
    new_actors = [actor.strip() for actor in message.text.split(',')] if message.text.strip() else film['actors']
    film['actors'] = new_actors
    await state.update_data(actors=new_actors)
    update_films(movies)
    await state.clear()
    await message.answer(f"Actors for {film['name']} updated successfully!")


@dp.message(FilmEdit.poster)
async def edit_film_poster(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    name = data['film_name']
    movies = get_films()
    film = next(f for f in movies if f['name'] == name)
    new_poster = message.text.strip() if message.text.strip() else film['poster']
    film['poster'] = new_poster
    await state.update_data(poster=new_poster)
    update_films(movies)
    await state.clear()
    await message.answer(f"Poster URL for {film['name']} updated successfully!")


@dp.message(DELETE_FILMS_COMMAND)
async def delete_film(message: Message, state: FSMContext) -> None:
    await state.set_state(FilmDelete.delete_query)
    await message.answer(
        "Enter the name of the movie you want to delete:",
        reply_markup=ReplyKeyboardRemove()
    )


@dp.message(FilmDelete.delete_query)
async def delete_film_query(message: Message, state: FSMContext) -> None:
    query = message.text.strip().lower()
    movies = get_films()
    film = next((f for f in movies if query in f['name'].lower()), None)  # Поиск по названию фильма
    if film:
        movies = [f for f in movies if f['name'].lower() != query]  # Удаляем фильм по названию
        update_films(movies)
        await state.clear()
        await message.answer(f"Film {film['name']} deleted successfully!")
    else:
        await message.answer("Movie not found. Please try again.")

@dp.message(FILM_CREATE_COMMAND)
async def film_create(message: Message, state: FSMContext) -> None:
    await state.set_state(FilmForm.name)
    await message.answer(
        "Enter the name of the movie.",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(FilmForm.name)
async def film_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(FilmForm.description)
    await message.answer(
        "Enter a description of the movie.",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(FilmForm.description)
async def film_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await state.set_state(FilmForm.rating)
    await message.answer(
        "Please rate the movie from 0 to 10.",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(FilmForm.rating)
async def film_rating(message: Message, state: FSMContext) -> None:
    await state.update_data(rating=message.text)
    await state.set_state(FilmForm.year)
    await message.answer(
        "Enter the year of the movie.",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(FilmForm.year)
async def film_year(message: Message, state: FSMContext) -> None:
    try:
        year = int(message.text)
        await state.update_data(year=year)
        await state.set_state(FilmForm.genre)
        await message.answer(
            "Enter the movie genre.",
            reply_markup=ReplyKeyboardRemove(),
        )
    except ValueError:
        await message.answer("Invalid year format. Please enter a valid number.")


@dp.message(FilmForm.genre)
async def film_genre(message: Message, state: FSMContext) -> None:
    await state.update_data(genre=message.text)
    await state.set_state(FilmForm.actors)
    await message.answer(
        text="Enter the movie actors through a separator, '\n"
             + html.bold("A comma and an indent after it are required."),
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(FilmForm.actors)
async def film_actors(message: Message, state: FSMContext) -> None:
    actors_list = [actor.strip() for actor in message.text.split(", ")]
    await state.update_data(actors=actors_list)
    await state.set_state(FilmForm.poster)
    await message.answer(
        "Enter a link to the movie poster.",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(FilmForm.poster)
async def film_poster(message: Message, state: FSMContext) -> None:
    data = await state.update_data(poster=message.text)
    film = add_film(data)
    await state.clear()
    await message.answer(
        f"Movie {film.name} successfully added!",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(Command('start'))
@async_log_message
async def start(message: Message, *args, **kwargs) -> None:
    logger.debug('Hi:)')
    await message.answer(
        f'Hello {message.from_user.full_name}!\n'
        'I am the first Python bot developer Shynkar Snizhana'
    )


@dp.message(FILMS_COMMAND)
async def films(message: Message) -> None:
    data = get_films()
    markup = films_keyboard_markup(films_list=data)
    await message.answer(
        "List of movies. Click on the movie title for details.",
        reply_markup=markup
    )


@dp.message()
async def echo_handler(message: Message) -> None:
    try:
        await message.answer(f"{html.bold(message.from_user.full_name)}, I dont understand you!")
    except TypeError:
        await message.answer(f"{html.bold(message.from_user.full_name)}, I dont understand you!")

@dp.callback_query(FilmCallback.filter())
async def callback_film(callback: CallbackQuery, callback_data: FilmCallback) -> None:
    film_id = callback_data.id
    film_data = get_films(film_id=film_id)
    film = Film(**film_data)
    text = (
        f"Film: {film.name}\n"
        f"Description: {film.description}\n"
        f"Rating: {film.rating}\n"
        f"Year: {film.year}\n"
        f"Genre: {film.genre}\n"
        f"Actors: {', '.join(film.actors)}\n"
    )
    await callback.message.answer_photo(
        caption=text,
        photo=URLInputFile(
            film.poster,
            filename=f"{film.name}_poster.{film.poster.split('.')[-1]}"
        )
    )


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
