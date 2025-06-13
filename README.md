# Book Management System API

A RESTful API for managing a library's book collection, built with Flask, SQLAlchemy, and Marshmallow. This API provides endpoints for managing books and handling library operations like checking books in and out.

## Features

- **Book Management**: Full CRUD operations for books
- **Library Operations**: Check books in and out
- **User Management**: Track which user has which books checked out
- **Search & Filtering**: Search books by title, author, or ISBN
- **Pagination**: Get paginated lists of books
- **Data Validation**: Input validation using Marshmallow schemas
- **Database Migrations**: Using Flask-Migrate for database schema changes

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- SQLite (for development, included in Python)

## Getting Started

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd book-management-system
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory with the following content:
   ```
   FLASK_APP=wsgi.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   ```

5. **Initialize the database**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. **Run the development server**
   ```bash
   flask run
   ```
   The API will be available at `http://localhost:5000`

## API Endpoints

### Books

- `GET /api/books` - Get all books (with pagination)
- `GET /api/books/<int:book_id>` - Get a single book
- `POST /api/books` - Create a new book
- `PUT /api/books/<int:book_id>` - Update a book
- `DELETE /api/books/<int:book_id>` - Delete a book

### Library Operations

- `POST /api/library/checkout` - Check out a book
- `POST /api/library/return/<int:checkout_id>` - Return a book
- `GET /api/library/user/<int:user_id>` - Get user's checkouts
- `GET /api/library/overdue` - Get all overdue books

## Example Usage

### Create a new book
```bash
curl -X POST http://localhost:5000/api/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "isbn": "9780743273565",
    "published_date": "1925-04-10",
    "publisher": "Scribner",
    "description": "A story of decadence and excess...",
    "total_copies": 5
  }'
```

### Check out a book
```bash
curl -X POST http://localhost:5000/api/library/checkout \
  -H "Content-Type: application/json" \
  -d '{
    "book_id": 1,
    "user_id": 1,
    "due_date": "2023-12-31T23:59:59Z"
  }'
```

### Return a book
```bash
curl -X POST http://localhost:5000/api/library/return/1
```

## Running Tests

```bash
pytest
```

## Database Migrations

When you make changes to the models, create a new migration and upgrade the database:

```bash
flask db migrate -m "Description of changes"
flask db upgrade
```

## Project Structure

```
book-management-system/
├── app/
│   ├── __init__.py         # Application factory
│   ├── models.py           # Database models
│   ├── config.py           # Configuration settings
│   ├── books/              # Books blueprint
│   │   ├── __init__.py
│   │   ├── routes.py       # Book-related routes
│   │   └── schemas.py      # Marshmallow schemas
│   └── library/            # Library operations blueprint
│       ├── __init__.py
│       └── routes.py       # Library operation routes
├── migrations/             # Database migrations (created by Flask-Migrate)
├── tests/                  # Test files
├── wsgi.py                 # WSGI entry point
├── requirements.txt        # Project dependencies
└── README.md              # This file
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
