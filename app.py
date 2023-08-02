from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os
import requests

app = Flask(__name__)

# Get the absolute path to the 'data' directory
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
db_path = os.path.join(data_dir, 'library.sqlite')

# Update the SQLALCHEMY_DATABASE_URI configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
db = SQLAlchemy(app)

# Data Models (Author and Book classes)
class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    birth_date = db.Column(db.String, nullable=True)
    date_of_death = db.Column(db.String, nullable=True)

    # Add the back-reference for the 'books' relationship
    books = db.relationship('Book', back_populates='author')

    def __repr__(self):
        return "Author(id={}, name='{}', birth_date='{}', date_of_death='{}')".format(
            self.id, self.name, self.birth_date, self.date_of_death)

class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    publication_year = db.Column(db.Integer, nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))

    author = db.relationship('Author', back_populates='books')

    def __repr__(self):
        return "Book(id={}, isbn='{}', title='{}', publication_year={})".format(
            self.id, self.isbn, self.title, self.publication_year)

#Flask routes
@app.route('/', methods=['GET'])
def home():
    # Get the keyword from the query parameters
    keyword = request.args.get('keyword', '')

    if keyword:
        # Perform the search based on the keyword
        books = Book.query.filter(Book.title.ilike(f"%{keyword}%")).all()
    else:
        # If no keyword is provided, show all books
        books = Book.query.all()

    for book in books:
        # Fetch book cover image using the ISBN
        isbn = book.isbn
        url = f'https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&jscmd=data&format=json'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            cover_image_url = data.get(f'ISBN:{isbn}', {}).get('cover', '')
            print(f'ISBN:{isbn} - Cover Image URL: {cover_image_url}')  # Add this line to print the URL
            book.cover_image_url = cover_image_url

    return render_template('home.html', books=books)

@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        name = request.form['name']
        birth_date = request.form.get('birth_date')  # Use get() method with a default value
        date_of_death = request.form.get('date_of_death')  # Use get() method with a default value

        author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)

        db.session.add(author)
        db.session.commit()

        return "Author added successfully!"

    return render_template('add_author.html')

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    authors = Author.query.all()

    if request.method == 'POST':
        isbn = request.form['isbn']
        title = request.form['title']
        publication_year = request.form['publication_year']
        author_id = request.form['author_id']

        book = Book(isbn=isbn, title=title, publication_year=publication_year, author_id=author_id)

        db.session.add(book)
        db.session.commit()

        return "Book added successfully!"

    return render_template('add_book.html', authors=authors)

@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get(book_id)
    if book:
        db.session.delete(book)
        db.session.commit()
        return redirect('/')
    return "Book not found or already deleted."

if __name__ == "__main__":
    # Initialize the database and create tables
    with app.app_context():
        db.create_all()

    # Run the Flask application
    app.run(host='127.0.0.1', port=3000, debug=True)