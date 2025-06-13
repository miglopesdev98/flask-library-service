from flask import request, jsonify, current_app
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from app.models import Book, db
from app.books.schemas import BookSchema
from . import bp  # Import the blueprint from the package

book_schema = BookSchema()
books_schema = BookSchema(many=True)

@bp.route('', methods=['GET'])
def get_books():
    """Get all books with optional pagination and search"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', current_app.config['BOOKS_PER_PAGE'], type=int)
    search = request.args.get('search', '')
    
    query = Book.query
    
    # Apply search if provided
    if search:
        search = f"%{search}%"
        query = query.filter(
            (Book.title.ilike(search)) |
            (Book.author.ilike(search)) |
            (Book.isbn.ilike(search))
        )
    
    # Order by most recently added
    books = query.order_by(Book.date_added.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'items': [book.to_dict() for book in books.items],
        'total': books.total,
        'pages': books.pages,
        'current_page': books.page
    }), 200

@bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """Get a single book by ID"""
    book = Book.query.get_or_404(book_id)
    return jsonify(book.to_dict()), 200

@bp.route('', methods=['POST'])
def create_book():
    """Create a new book"""
    data = request.get_json()
    
    # Validate and deserialize input
    try:
        book_data = book_schema.load(data)
    except Exception as e:
        return jsonify({"error": "Invalid data", "details": str(e)}), 400
    
    # Create new book
    book = Book(**book_data)
    
    try:
        db.session.add(book)
        db.session.commit()
        return jsonify(book.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Book with this ISBN already exists"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create book", "details": str(e)}), 500

@bp.route('/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """Update an existing book"""
    book = Book.query.get_or_404(book_id)
    data = request.get_json()
    
    # Validate and deserialize input
    try:
        book_data = book_schema.load(data, partial=True)
    except Exception as e:
        return jsonify({"error": "Invalid data", "details": str(e)}), 400
    
    # Update book fields
    for key, value in book_data.items():
        setattr(book, key, value)
    
    try:
        db.session.commit()
        return jsonify(book.to_dict()), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Book with this ISBN already exists"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update book", "details": str(e)}), 500

@bp.route('/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """Delete a book"""
    book = Book.query.get_or_404(book_id)
    
    try:
        db.session.delete(book)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to delete book", "details": str(e)}), 500
