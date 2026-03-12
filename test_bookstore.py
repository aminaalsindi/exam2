"""
Exam 2 - Bookstore API Integration Tests
==========================================
Write your tests below. Each section (Part B and Part D) is marked.
Follow the instructions in each part carefully.

Run your tests with:
    pytest test_bookstore.py -v

Run with coverage:
    pytest test_bookstore.py --cov=bookstore_db --cov=bookstore_app --cov-report=term-missing -v
"""

import pytest
from bookstore_app import app


# ============================================================
# FIXTURE: Test client with isolated database (provided)
# ============================================================

@pytest.fixture
def client(tmp_path, monkeypatch):
    """Create a test client with a temporary database."""
    db_path = str(tmp_path / "test_bookstore.db")
    monkeypatch.setattr("bookstore_db.DB_NAME", db_path)

    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ============================================================
# HELPER: Create a book (provided for convenience)
# ============================================================

def create_sample_book(client, title="The Great Gatsby", author="F. Scott Fitzgerald", price=12.99):
    """Helper to create a book and return the res JSON."""
    res = client.post("/books", json={
        "title": title,
        "author": author,
        "price": price,
    })
    return res


# ============================================================
# PART B - Integration Tests (20 marks)
# Write at least 14 tests covering ALL of the following:
#
# POST /books:
#   - Create a valid book (check 201 and res body)
#   - Create with missing title (check 400)
#   - Create with empty author (check 400)
#   - Create with invalid price (check 400)
#
# GET /books:
#   - List books when empty (check 200, empty list)
#   - List books after adding 2+ books (check count)
#
# GET /books/<id>:
#   - Get an existing book (check 200)
#   - Get a non-existing book (check 404)
#
# PUT /books/<id>:
#   - Update a book's title (check 200 and new value)
#   - Update with invalid price (check 400)
#   - Update a non-existing book (check 404)
#
# DELETE /books/<id>:
#   - Delete an existing book (check 200, then confirm 404)
#   - Delete a non-existing book (check 404)
#
# Full workflow:
#   - Create -> Read -> Update -> Read again -> Delete -> Confirm gone
# ============================================================

# TODO: Write your Part B tests here
def test_create_valid_book(client):
    res = client.post("/books", json={
        "title": "Cook Book",
        "author": "Manal Alalem",
        "price": 15
    })

    assert res.status_code == 201
    data = res.get_json()
    assert data["book"]["title"] == "Cook Book"
    assert data["book"]["author"] == "Manal Alalem"
    assert data["book"]["price"] == 15


def test_create_book_missing_title(client):
    res = client.post("/books", json={
        "author": "Manal Alalem",
        "price": 15
    })

    assert res.status_code == 400
    assert "error" in res.get_json()


def test_create_book_empty_author(client):
    res = client.post("/books", json={
        "title": "Cook Book",
        "author": "",
        "price": 15
    })
    assert res.status_code == 400
    assert "Author cannot be empty" in res.get_json()["error"]


def test_create_book_invalid_price(client):
    res = client.post("/books", json={
        "title": "Cook Book",
        "author": "Manal Alalem",
        "price": -5
    })
    assert res.status_code == 400
    assert "Price must be positive" in res.get_json()["error"]


def test_list_books_empty(client):
    res = client.get("/books")

    assert res.status_code == 200
    assert res.get_json()["books"] == []

def test_list_books_after_adding_books(client):
    create_sample_book(client, title="Cook Book", author="Manal Alalem", price=10)
    create_sample_book(client, title="Book Two", author="Author Two", price=20)
    res = client.get("/books")
    assert res.status_code == 200
    assert len(res.get_json()["books"]) == 2


def test_get_existing_book(client):
    create_res = create_sample_book(client, title="Cook Book", author="Manal Alalem", price=10)
    book_id = create_res.get_json()["book"]["id"]
    res = client.get(f"/books/{book_id}")
    assert res.status_code == 200
    data = res.get_json()
    assert data["book"]["id"] == book_id
    assert data["book"]["title"] == "Cook Book"


def test_get_non_existing_book(client):
    res = client.get("/books/999")
    assert res.status_code == 404
    assert res.get_json()["error"] == "Book not found"


def test_update_book_title(client):
    create_res = create_sample_book(client, title="Old Title", author="Manal Alalem", price=10)
    book_id = create_res.get_json()["book"]["id"]
    res = client.put(f"/books/{book_id}", json={
        "title": "New Title"
    })
    assert res.status_code == 200
    assert res.get_json()["book"]["title"] == "New Title"

def test_update_book_invalid_price(client):
    create_res = create_sample_book(client, title="Cook Book", author="Manal Alalem", price=10)
    book_id = create_res.get_json()["book"]["id"]
    res = client.put(f"/books/{book_id}", json={
        "price": -5
    })
    assert res.status_code == 400
    assert "Price must be positive" in res.get_json()["error"]

def test_update_non_existing_book(client):
    res = client.put("/books/999", json={
        "title": "New Title"
    })
    assert res.status_code == 404
    assert "not found" in res.get_json()["error"]

def test_delete_existing_book(client):
    create_res = create_sample_book(client, title="Cook Book", author="Manal Alalem", price=10)
    book_id = create_res.get_json()["book"]["id"]
    delete_res = client.delete(f"/books/{book_id}")
    get_res = client.get(f"/books/{book_id}")
    assert delete_res.status_code == 200
    assert delete_res.get_json()["message"] == "Book deleted"
    assert get_res.status_code == 404


def test_delete_non_existing_book(client):
    res = client.delete("/books/999")
    assert res.status_code == 404
    assert "not found" in res.get_json()["error"]

def test_full_workflow(client):
    create_res = client.post("/books", json={
        "title": "Workflow Book",
        "author": "Workflow Author",
        "price": 15
    })
    assert create_res.status_code == 201
    book_id = create_res.get_json()["book"]["id"]

    read_res = client.get(f"/books/{book_id}")
    assert read_res.status_code == 200
    assert read_res.get_json()["book"]["title"] == "Workflow Book"

    update_res = client.put(f"/books/{book_id}", json={
        "title": "Updated Workflow Book"
    })
    assert update_res.status_code == 200
    assert update_res.get_json()["book"]["title"] == "Updated Workflow Book"
    read_again_res = client.get(f"/books/{book_id}")
    assert read_again_res.status_code == 200
    assert read_again_res.get_json()["book"]["title"] == "Updated Workflow Book"

    delete_res = client.delete(f"/books/{book_id}")
    assert delete_res.status_code == 200

    confirm_res = client.get(f"/books/{book_id}")
    assert confirm_res.status_code == 404
# ============================================================
# PART D - Coverage (5 marks)
# Run: pytest test_bookstore.py --cov=bookstore_db --cov=bookstore_app --cov-report=term-missing -v
# You must achieve 85%+ coverage across both files.
# If lines are missed, add more tests above to cover them.
# ============================================================


# ============================================================
# BONUS (5 extra marks)
# 1. Add a search endpoint to bookstore_app.py:
#    GET /books/search?q=<query>
#    - Uses search_books() from bookstore_db.py
#    - Returns {"books": [...]} with status 200
#    - Returns {"error": "Search query is required"} with 400 if q is missing
#
# 2. Write 3 integration tests for the search endpoint:
#    - Search by title (partial match)
#    - Search by author (partial match)
#    - Search with no results (empty list)
# ============================================================

# TODO: Write your bonus tests here (optional)
