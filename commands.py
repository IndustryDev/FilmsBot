from aiogram.filters import Command
from aiogram.types.bot_command import BotCommand

FILMS_COMMAND = Command('films')
START_COMMAND = Command('start')
FILM_CREATE_COMMAND = Command("create_film")
SEARCH_FILMS_COMMAND = Command('search_film')
FILTER_FILMS_COMMAND = Command('filter_films')
EDIT_FILMS_COMMAND = Command('edit_film')
DELETE_FILMS_COMMAND = Command('delete_film')

BOT_COMMANDS = [
   BotCommand(command="films", description="View a list of movies"),
   BotCommand(command="start", description="Start a conversation"),
   BotCommand(command="create_film", description="Add new movie"),
   BotCommand(command="search_film", description="Movie search"),
   BotCommand(command="filter_films", description="Movie filtering"),
   BotCommand(command="edit_film", description="Edit film"),
   BotCommand(command="delete_film", description="Delete film")
]
