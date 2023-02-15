from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from sqlalchemy import and_

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.String()
    description = fields.String()
    trailer = fields.String()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.String()


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.String()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)
genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)
director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')


@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        if director_id and genre_id:
            movies_by_director_genre = db.session.query(Movie).filter(and_(
                Movie.genre_id == genre_id, Movie.director_id == director_id))
            return movies_schema.dump(movies_by_director_genre), 200
        elif director_id:
            movies_with_director = db.session.query(Movie).filter(Movie.director_id == director_id)
            return movies_schema.dump(movies_with_director), 200
        elif genre_id:
            movies_with_genre = db.session.query(Movie).filter(Movie.genre_id == genre_id)
            return movies_schema.dump(movies_with_genre), 200
        all_movies = Movie.query.all()
        return movies_schema.dump(all_movies), 200


@movie_ns.route('/<int:mid>')
class MovieView(Resource):
    def get(self, mid: int):
        movie = Movie.query.get(mid)
        if not movie:
            return '', 404
        return movie_schema.dump(movie), 200


@director_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        directors = Director.query.all()
        return directors_schema.dump(directors), 200

    def post(self):
        json_data = request.json
        new_director = Director(**json_data)
        db.session.add(new_director)
        db.session.commit()
        return '', 201


@director_ns.route('/<int:did>')
class DirectorView(Resource):
    def get(self, did: int):
        director = Director.query.get(did)
        if not director:
            return '', 404
        return director_schema.dump(director), 200

    def put(self, did: int):
        director = Director.query.get(did)
        if not director:
            return '', 404

        json_data = request.json
        director.id = json_data.get('id')
        director.name = json_data.get('name')
        db.session.add(director)
        db.session.commit()
        return '', 204

    def delete(self, did: int):
        director = Director.query.get(did)
        if not director:
            return '', 404

        db.session.delete(director)
        db.session.commit()
        return '', 204


@genre_ns.route("/")
class GenresView(Resource):
    def get(self):
        genres = Genre.query.all()
        return genres_schema.dump(genres), 200

    def post(self):
        req_json = request.json
        new_genre = Genre(**req_json)
        db.session.add(new_genre)
        db.session.commit()
        return '', 201


@genre_ns.route('/<int:gid>')
class GenreView(Resource):
    def get(self, gid: int):
        genre = Genre.query.get(gid)
        if not genre:
            return '', 404
        return genre_schema.dump(genre), 200

    def put(self, gid: int):
        genre = Genre.query.get(gid)
        if not genre:
            return '', 404

        json_data = request.json
        genre.id = json_data.get('id')
        genre.name = json_data.get('name')
        db.session.add(genre)
        db.session.commit()
        return '', 204

    def delete(self, gid: int):
        genre = Genre.query.get(gid)
        if not genre:
            return '', 404

        db.session.delete(genre)
        db.session.commit()
        return '', 204


app.run
