from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import requests

app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Define Book model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable = False)
    author = db.Column(db.String(100), nullable = False)
    status = db.Column(db.String(20), nullable = False)  # "Finished", "In Progress", "Want to Read"
    image_url = db.Column(db.String(300))  # URL for the book cover image

# Route to display books
@app.route('/')
def home():
    books = Book.query.all()
    return render_template("index.html", books = books)

# Route to add a new book
@app.route('/add', methods = ['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        status = request.form['status']

        # Fetch book cover image using Google Books API
        query = f"{title} {author}"
        response = requests.get(f"https://www.googleapis.com/books/v1/volumes?q={query}")
        data = response.json()

        # Default image URL if no cover found
        image_url = "https://via.placeholder.com/128x192?text=No+Cover"

        if 'items' in data:
            try:
                image_url = data['items'][0]['volumeInfo']['imageLinks']['thumbnail']
            except KeyError:
                pass

        # Add book to the database
        new_book = Book(title = title, author = author, status = status, image_url = image_url)
        db.session.add(new_book)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('add.html')

# Route to delete a book
@app.route('/delete/<int:book_id>')
def delete_book(book_id):
    book_to_delete = Book.query.get_or_404(book_id)
    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug = True)