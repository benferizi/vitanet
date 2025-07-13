import pytest
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


def test_basic():
    """Basic test to ensure pytest works."""
    assert 1 + 1 == 2


def test_home_page(client):
    """Test the home page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Vitanet' in response.data
    assert b'nutrition tracking dashboard' in response.data


def test_api_foods_endpoint(client):
    """Test the /api/foods endpoint."""
    response = client.get('/api/foods')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 10  # We have 10 foods in our database
    
    # Check that each food has required fields
    for food in data:
        assert 'item' in food
        assert 'calories' in food
        assert 'carbs_g' in food
        assert 'protein_g' in food
        assert 'fat_g' in food
        assert 'fiber_g' in food
        assert 'category' in food


def test_api_foods_category_filter(client):
    """Test the /api/foods endpoint with category filter."""
    response = client.get('/api/foods?category=fruit')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 2  # Apple and Banana
    
    for food in data:
        assert food['category'] == 'fruit'


def test_api_specific_food(client):
    """Test getting a specific food by name."""
    response = client.get('/api/foods/apple')
    assert response.status_code == 200
    data = response.get_json()
    assert data['item'] == 'Apple'
    assert data['calories'] == 95
    assert data['category'] == 'fruit'


def test_api_specific_food_not_found(client):
    """Test getting a non-existent food."""
    response = client.get('/api/foods/nonexistent')
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data


def test_api_categories(client):
    """Test the /api/categories endpoint."""
    response = client.get('/api/categories')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    expected_categories = ['dairy', 'fruit', 'grain', 'nut', 'protein', 'vegetable']
    assert sorted(data) == expected_categories


def test_api_calculate_nutrition(client):
    """Test the nutrition calculation endpoint."""
    response = client.get('/api/calculate?foods=apple,banana&quantities=1,2')
    assert response.status_code == 200
    data = response.get_json()
    
    assert 'total_calories' in data
    assert 'total_carbs_g' in data
    assert 'total_protein_g' in data
    assert 'total_fat_g' in data
    assert 'total_fiber_g' in data
    assert 'foods' in data
    
    # Check calculation: 1 apple (95 cal) + 2 bananas (105*2 = 210 cal) = 305 cal
    assert data['total_calories'] == 305.0
    assert len(data['foods']) == 2


def test_api_calculate_invalid_food(client):
    """Test calculation with invalid food name."""
    response = client.get('/api/calculate?foods=invalidfood&quantities=1')
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data


def test_api_calculate_mismatched_quantities(client):
    """Test calculation with mismatched foods and quantities."""
    response = client.get('/api/calculate?foods=apple,banana&quantities=1')
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data


def test_vitalsync_endpoint(client):
    """Test the VitalsSync module endpoint."""
    response = client.get('/vitalsync')
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Welcome to VitalsSync Module!'


def test_app_factory():
    """Test that the app factory creates a working app."""
    app = create_app()
    assert app is not None
    assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///vitanet.db'
    assert app.config['BABEL_DEFAULT_LOCALE'] == 'en'


