import pytest
from app import create_app, db
from app.models import Book
from datetime import date, timedelta

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
        # Add test data
        book = Book(
            title='Test Book',
            author='Test Author',
            isbn='1234567890',
            published_date=date(2020, 1, 1),
            publisher='Test Publisher',
            description='A test book',
            total_copies=5,
            available_copies=5
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

def test_get_books(client):
    """Test getting all books."""
    response = client.get('/api/books')
    assert response.status_code == 200
    data = response.get_json()
    assert 'items' in data
    assert len(data['items']) == 1
    assert data['items'][0]['title'] == 'Test Book'

def test_get_single_book(client):
    """Test getting a single book."""
    response = client.get('/api/books/1')
    assert response.status_code == 200
    data = response.get_json()
    assert data['title'] == 'Test Book'
    assert data['author'] == 'Test Author'

def test_create_book(client):
    """Test creating a new book."""
    new_book = {
        'title': 'New Book',
        'author': 'New Author',
        'isbn': '0987654321',
        'published_date': '2021-01-01',
        'publisher': 'New Publisher',
        'description': 'A new test book',
        'total_copies': 3
    }
    response = client.post('/api/books', json=new_book)
    assert response.status_code == 201
    data = response.get_json()
    assert data['title'] == 'New Book'
    assert data['available_copies'] == 3  # Should match total_copies

def test_update_book(client):
    """Test updating a book."""
    updated_data = {
        'title': 'Updated Title',
        'author': 'Updated Author'
    }
    response = client.put('/api/books/1', json=updated_data)
    assert response.status_code == 200
    data = response.get_json()
    assert data['title'] == 'Updated Title'
    assert data['author'] == 'Updated Author'

def test_delete_book(client):
    """Test deleting a book."""
    response = client.delete('/api/books/1')
    assert response.status_code == 200
    
    # Verify the book was deleted
    response = client.get('/api/books/1')
    assert response.status_code == 404
