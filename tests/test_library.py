import pytest
from datetime import datetime, timedelta
from app import create_app, db
from app.models import Book, Checkout

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False,
    })

    # Create the database and load test data
    with app.app_context():
        db.create_all()
        # Add test book
        book = Book(
            title='Test Book',
            author='Test Author',
            isbn='1234567890',
            published_date=datetime(2020, 1, 1).date(),
            total_copies=2,
            available_copies=2
        )
        db.session.add(book)
        db.session.commit()

    yield app

    # Clean up
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

def test_checkout_book(client):
    """Test checking out a book."""
    checkout_data = {
        'book_id': 1,
        'user_id': 1,
        'due_date': (datetime.utcnow() + timedelta(days=14)).isoformat() + 'Z'
    }
    
    response = client.post('/api/library/checkout', json=checkout_data)
    assert response.status_code == 200
    data = response.get_json()
    assert 'checkout_id' in data
    
    # Verify book available copies were updated
    book = Book.query.get(1)
    assert book.available_copies == 1

def test_return_book(client):
    """Test returning a checked out book."""
    # First, check out a book
    checkout_data = {
        'book_id': 1,
        'user_id': 1,
        'due_date': (datetime.utcnow() + timedelta(days=14)).isoformat() + 'Z'
    }
    response = client.post('/api/library/checkout', json=checkout_data)
    checkout_id = response.get_json()['checkout_id']
    
    # Now return the book
    response = client.post(f'/api/library/return/{checkout_id}')
    assert response.status_code == 200
    
    # Verify book available copies were updated
    book = Book.query.get(1)
    assert book.available_copies == 2
    
    # Verify the checkout record was updated
    checkout = Checkout.query.get(checkout_id)
    assert checkout.return_date is not None

def test_get_user_checkouts(client):
    """Test getting a user's checkouts."""
    # Check out a book
    checkout_data = {
        'book_id': 1,
        'user_id': 1,
        'due_date': (datetime.utcnow() + timedelta(days=14)).isoformat() + 'Z'
    }
    client.post('/api/library/checkout', json=checkout_data)
    
    # Get user's checkouts
    response = client.get('/api/library/user/1')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['book_id'] == 1
    assert data[0]['user_id'] == 1

def test_get_overdue_books(client):
    """Test getting overdue books."""
    # Create a checkout that's already overdue
    overdue_checkout = Checkout(
        book_id=1,
        user_id=1,
        checkout_date=datetime.utcnow() - timedelta(days=30),
        due_date=datetime.utcnow() - timedelta(days=15),
        return_date=None
    )
    db.session.add(overdue_checkout)
    db.session.commit()
    
    # Update book available copies
    book = Book.query.get(1)
    book.available_copies = 0
    db.session.commit()
    
    # Get overdue books
    response = client.get('/api/library/overdue')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['book_id'] == 1
    assert data[0]['user_id'] == 1
    assert data[0]['days_overdue'] > 0
