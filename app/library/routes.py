from flask import request, jsonify, current_app
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from app.models import Book, Checkout, db
from app.books.schemas import CheckoutSchema
from . import bp  # Import the blueprint from the package

checkout_schema = CheckoutSchema()

def calculate_due_date():
    """Calculate due date (14 days from now)"""
    return datetime.utcnow() + timedelta(days=14)

@bp.route('/checkout', methods=['POST'])
def checkout_book():
    """Check out a book from the library"""
    data = request.get_json()
    
    # Validate input
    try:
        checkout_data = checkout_schema.load(data)
    except Exception as e:
        return jsonify({"error": "Invalid data", "details": str(e)}), 400
    
    book_id = checkout_data['book_id']
    user_id = checkout_data['user_id']
    
    # Check if book exists and is available
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    
    if book.available_copies <= 0:
        return jsonify({"error": "No available copies of this book"}), 400
    
    # Check if user already has this book checked out
    active_checkout = Checkout.query.filter_by(
        book_id=book_id,
        user_id=user_id,
        return_date=None
    ).first()
    
    if active_checkout:
        return jsonify({"error": "You already have this book checked out"}), 400
    
    # Create checkout record
    due_date = checkout_data.get('due_date') or calculate_due_date()
    checkout = Checkout(
        book_id=book_id,
        user_id=user_id,
        due_date=due_date
    )
    
    # Update book available copies
    book.available_copies -= 1
    
    try:
        db.session.add(checkout)
        db.session.commit()
        return jsonify({
            "message": "Book checked out successfully",
            "checkout_id": checkout.id,
            "due_date": checkout.due_date.isoformat()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to check out book", "details": str(e)}), 500

@bp.route('/return/<int:checkout_id>', methods=['POST'])
def return_book(checkout_id):
    """Return a checked out book"""
    checkout = Checkout.query.get(checkout_id)
    
    if not checkout:
        return jsonify({"error": "Checkout record not found"}), 404
    
    if checkout.return_date is not None:
        return jsonify({"error": "This book has already been returned"}), 400
    
    # Update checkout record
    checkout.return_date = datetime.utcnow()
    
    # Update book available copies
    book = Book.query.get(checkout.book_id)
    if book:
        book.available_copies += 1
    
    try:
        db.session.commit()
        return jsonify({
            "message": "Book returned successfully",
            "checkout_id": checkout.id,
            "return_date": checkout.return_date.isoformat()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to return book", "details": str(e)}), 500

@bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_checkouts(user_id):
    """Get all checkouts for a user"""
    active_only = request.args.get('active', 'true').lower() == 'true'
    
    query = Checkout.query.filter_by(user_id=user_id)
    
    if active_only:
        query = query.filter(Checkout.return_date.is_(None))
    
    checkouts = query.order_by(Checkout.checkout_date.desc()).all()
    
    return jsonify([{
        'id': c.id,
        'book_id': c.book_id,
        'book_title': c.book.title if c.book else 'Unknown Book',
        'checkout_date': c.checkout_date.isoformat(),
        'due_date': c.due_date.isoformat(),
        'return_date': c.return_date.isoformat() if c.return_date else None,
        'is_overdue': c.return_date is None and c.due_date < datetime.utcnow()
    } for c in checkouts]), 200

@bp.route('/overdue', methods=['GET'])
def get_overdue_books():
    """Get all overdue books"""
    overdue_checkouts = Checkout.query.filter(
        Checkout.return_date.is_(None),
        Checkout.due_date < datetime.utcnow()
    ).all()
    
    return jsonify([{
        'checkout_id': c.id,
        'book_id': c.book_id,
        'book_title': c.book.title if c.book else 'Unknown Book',
        'user_id': c.user_id,
        'checkout_date': c.checkout_date.isoformat(),
        'due_date': c.due_date.isoformat(),
        'days_overdue': (datetime.utcnow().date() - c.due_date.date()).days
    } for c in overdue_checkouts]), 200
