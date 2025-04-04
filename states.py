from aiogram.fsm.state import StatesGroup, State

class FilmSort(StatesGroup):
    search_query = State()

class FilmForm(StatesGroup):
    name = State()
    description = State()
    rating = State()
    year = State()
    genre = State()
    actors = State()
    poster = State()

class FilmFilter(StatesGroup):
    filter_criteria = State()
    rating = State()
    year = State()
    genre = State()

class FilmEdit(StatesGroup):
    select_field = State()
    edit_query = State()
    name = State()
    description = State()
    rating = State()
    year = State()
    genre = State()
    actors = State()
    poster = State()

    @classmethod
    async def next(cls):
        pass


class FilmDelete(StatesGroup):
    delete_query = State()
