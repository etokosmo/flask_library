import os

from flask import Flask, request, jsonify, render_template
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from loguru import logger
from marshmallow import fields, exceptions
from sqlalchemy import orm

app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
                                        os.path.join(BASE_DIR, 'db.sqlite3')
PATH_TO_LOGS = os.path.join(BASE_DIR, 'logs', 'logs.log')

db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    author_id = db.Column(db.Integer, db.ForeignKey("author.id"))
    author = db.relationship("Author", backref="books", lazy='subquery')


class BookSchema(ma.SQLAlchemySchema):
    id = fields.Int(dump_only=True)
    title = fields.Str()

    author = fields.Nested(lambda: AuthorSchema(only=("name",)))


class AuthorSchema(ma.SQLAlchemyAutoSchema):
    id = fields.Int(dump_only=True)
    name = fields.Str()

    books = fields.List(fields.Nested(BookSchema(exclude=("author",))))


db.create_all()
author_schema = AuthorSchema()
book_schema = BookSchema()
books_schema = BookSchema(many=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/library/', methods=['GET'])
def get_book_list():
    all_books = Book.query.all()
    return jsonify(books_schema.dump(all_books))


@app.route('/library/', methods=['POST'])
def create_book():
    schema = BookSchema()
    try:
        content = schema.load(request.json)
        if not content:
            raise exceptions.ValidationError("Пустой запрос")
    except exceptions.ValidationError:
        logger.debug(f'Ошибка запроса. Неправильные переданные параметры.')
        return book_schema.dump({})
    res_title = content.get('title')
    res_author = content.get('author').get('name')
    if result := db.session.query(Author).filter(Author.name == res_author).first():
        author = result
    else:
        author = Author(name=res_author)
    book = Book(title=res_title, author=author)
    db.session.add(author)
    db.session.add(book)
    db.session.commit()

    return book_schema.dump(book)


@app.route('/library/<int:book_id>/', methods=["GET"])
def get_book_detail(book_id):
    book = Book.query.get(book_id)
    return book_schema.jsonify(book)


@app.route('/library/<string:author>/', methods=["GET"])
def get_books_for_author(author):
    author = db.session.query(Author).filter(Author.name == author).first()
    return author_schema.dump(author)


@app.route('/library/<int:book_id>/', methods=['PATCH'])
def update_book(book_id):
    schema = BookSchema()
    try:
        content = schema.load(request.json)
        if not content:
            raise exceptions.ValidationError("Пустой запрос")
    except exceptions.ValidationError:
        logger.debug(f'Ошибка запроса. Неправильные переданные параметры.')
        return book_schema.dump({})

    res_title = content.get('title')
    res_author = content.get('author').get('name')

    if result := db.session.query(Author).filter(Author.name == res_author).first():
        author = result
    else:
        author = Author(name=res_author)

    book = Book.query.get(book_id)
    if not book:
        logger.debug(f'Ошибка запроса. Книга с id={book_id} не найдена.')
        return book_schema.jsonify(book)
    book.title = res_title
    book.author = author

    db.session.add(author)
    db.session.add(book)
    db.session.commit()

    return book_schema.jsonify(book)


@app.route('/library/<int:book_id>/', methods=["DELETE"])
def delete_book(book_id):
    book = Book.query.get(book_id)
    try:
        db.session.delete(book)
        db.session.commit()
    except orm.exc.UnmappedInstanceError:
        logger.debug(f'Ошибка запроса. Книга с id={book_id} не найдена.')
        pass
    return book_schema.jsonify(book)


if __name__ == '__main__':
    logger.add(PATH_TO_LOGS, level='DEBUG')
    app.run(debug=True)
