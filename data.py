import json

from models import Film


FILM_DATA_PATH = 'data.json'

def get_films(file_path: str = "data.json", film_id: int | None = None) -> list[dict] | dict:
   with open(file_path, "r") as fp:
       films = json.load(fp)
       if film_id is not None:
           for film in films:
               if film['id'] == film_id:
                   return film
       return films


def add_film(
   data: dict,
   file_path: str = "data.json",
) -> Film:
    """
    Add film to file
    :param data: fields of film
    :param file_path:
    :return:
    """
    films = get_films(file_path=file_path, film_id=None) or []
    next_id = films[-1].get('id') + 1 if films else 0
    film = Film(id=next_id, **data)
    films.append(film.model_dump())
    with open(file_path, "w") as fp:
        json.dump(
            films,
            fp,
            indent=4,
            ensure_ascii=False
        )
    return film
