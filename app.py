from flask import Flask, request
from flask_restx import Api, Resource

from Schemas import movie_schema, movies_schema, director_schema, directors_schema, genre_schema, genres_schema
from Models import Movie, Director, Genre
from setup_db import db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JSON_AS_ASCII"] = False

app.app_context().push()

db.init_app(app)

api = Api(app)
movie_ns = api.namespace("movies")
director_ns = api.namespace("directors")
genre_ns = api.namespace("genres")


@movie_ns.route("/")  # Показ всех фильмов
class MovieView(Resource):
    def get(self):
        all_movie_filter = db.session.query(Movie.id, Movie.title, Movie.description, Movie.trailer, Movie.year, Movie.rating,
                                            Genre.name.label("genre"),
                                            Director.name.label("director")).join(Genre).join(Director)


        dir_id = request.args.get("director_id")
        gen_id = request.args.get("genre_id")

        if "director_id" in request.args:
            all_movie_filter = all_movie_filter.filter(Movie.director_id == dir_id)

        if "genre_id" in request.args:
            all_movie_filter = all_movie_filter.filter(Movie.genre_id == gen_id)

        all_movies = all_movie_filter.all()

        movies_schema.dump(all_movies), 200

    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)

        with db.session.begin():
            db.session.add(new_movie)

        return f"Фильм с id = {new_movie.id} успешно создан!", 201


@movie_ns.route("/<int:movie_id>")  # Отображение выбранного фильма по его 'id'
class MovieView(Resource):
    def get(self, movie_id: int):
        one_movie = db.session.query(Movie.id, Movie.title, Movie.description, Movie.trailer, Movie.year, Movie.rating,
                                     Genre.name.label("genre"),
                                     Director.name.label("director")).join(Genre).join(Director).\
                                     filter(Movie.id == movie_id).first()

        if one_movie:
            return movie_schema.dump(one_movie), 200
        return f"Выбранного фильма с id = {movie_id} не найдено!", 404

    def patch(self, movie_id: int):
        edit_part_of_movie = db.session.query(Movie).get(movie_id)

        if not edit_part_of_movie:
            return f"Выбранного фильма с id = {movie_id} не найдено!", 404

        req_json = request.json
        if "title" in req_json:
            edit_part_of_movie.title = req_json["title"]
        elif "description" in req_json:
            edit_part_of_movie.description = req_json["description"]
        elif "trailer" in req_json:
            edit_part_of_movie.trailer = req_json["trailer"]
        elif "year" in req_json:
            edit_part_of_movie.year = req_json["year"]
        elif "rating" in req_json:
            edit_part_of_movie.rating = req_json["rating"]
        elif "genre_id" in req_json:
            edit_part_of_movie.genre_id = req_json["genre_id"]
        elif "director_id" in req_json:
            edit_part_of_movie.director_id = req_json["director_id"]

        db.session.add(edit_part_of_movie)
        db.session.commit()

        return f"Фильм с id = {edit_part_of_movie.id} успешно обновлен!", 204

    def put(self, movie_id: int):
        edit_all_movie = db.session.query(Movie).get(movie_id)

        if not edit_all_movie:
            return f"Выбранного фильма с id = {movie_id} не найдено!", 404

        req_json = request.json

        edit_all_movie.title = req_json["title"]
        edit_all_movie.description = req_json["description"]
        edit_all_movie.trailer = req_json["trailer"]
        edit_all_movie.year = req_json["year"]
        edit_all_movie.rating = req_json["rating"]
        edit_all_movie.genre_id = req_json["genre_id"]
        edit_all_movie.director_id = req_json["director_id"]

        db.session.add(edit_all_movie)
        db.session.commit()

        return f"Фильм с id = {edit_all_movie.id} успешно обновлен!", 204

    def delete(self, movie_id: int):
        del_movie = db.session.query(Movie).get(movie_id)

        if not del_movie:
            return f"Выбранного фильма с id = {movie_id} не найдено!", 404

        db.session.delete(del_movie)
        db.session.commit()

        return f"Фильм с id = {del_movie.id} успешно удален!", 204


@director_ns.route("/")  # Отображение всех режиссеров
class DirectorsView(Resource):
    def get(self):
        all_directors = db.session.query(Director.id, Director.name).all()

        return directors_schema.dump(all_directors), 200

    def post(self):
        req_json = request.json
        new_director = Director(**req_json)

        with db.session.begin():
            db.session.add(new_director)

        return f"Режиссер с id = {new_director.id} успешно создан!", 201


@director_ns.route("/<int:director_id>")
class DirectorView(Resource):
    def get(self, director_id: int):
        one_director = db.session.query(Director.id, Director.name).filter(Director.id == director_id).first()

        if one_director:
            return director_schema.dump(one_director), 200
        return f"Выбранного режиссера с id = {director_id} не найдено!", 404

    def put(self, director_id: int):
        edit_director = db.session.query(Director).get(director_id)

        if not edit_director:
            return f"Выбранного режиссера с id = {director_id} не найдено!", 404

        req_json = request.json
        edit_director.name = req_json["name"]

        db.session.add(edit_director)
        db.session.commit()

        return f"Режиссер с id = {edit_director.id} успешно обновлен!", 204

    def delete(self, director_id: int):
        del_director = db.session.query(Director).get(director_id)

        if not del_director:
            return f"Выбранного режиссера с id = {director_id} не найдено!", 404

        db.session.delete(del_director)
        db.session.commit()

        return f"Режиссер с id = {del_director.id} успешно удален!", 204


@genre_ns.route("/")
class GenreView(Resource):
    def get(self):
        all_genres = db.session.query(Genre.id, Genre.name).all()

        return genres_schema.dump(all_genres), 200

    def post(self):
        req_json = request.json
        new_genre = Genre(**req_json)

        with db.session.begin():
            db.session.add(new_genre)

        return f"Жанр с id = {new_genre.id} успешно создан!", 201


@genre_ns.route("/<int:genre_id>")  # Отображение выбранного жанра по его 'id'
class GenreView(Resource):
    def get(self, genre_id: int):
        one_genre = db.session.query(Genre.id, Genre.name).filter(Genre.id == genre_id).first()

        if one_genre:
            return genre_schema.dump(one_genre), 200
        return f"Выбранного жанра с id = {genre_id} не найдено!", 404

    def put(self, genre_id: int):
        edit_one_genre = db.session.query(Genre).get(genre_id)

        if not edit_one_genre:
            return f"Выбранного жанра с id = {genre_id} не найдено!", 404

        req_json = request.json
        edit_one_genre.name = req_json["name"]

        db.session.add(edit_one_genre)
        db.session.commit()

        return f"Жанр с id = {edit_one_genre.id} успешно обновлен!", 204

    def delete(self, genre_id: int):
        del_genre = db.session.query(Genre).get(genre_id)

        if not del_genre:
            return f"Выбранного жанра с id = {genre_id} не найдено!", 404

        db.session.delete(del_genre)
        db.session.commit()

        return f"Жанр с id = {del_genre.id} успешно удален!", 204


if __name__ == '__main__':
    app.run(debug=True)
