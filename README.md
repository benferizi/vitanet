# Vitanet 🌱

**Your comprehensive nutrition tracking dashboard**

Vitanet is a Flask-based web application that provides a comprehensive platform for tracking nutrition data, with a rich food database, interactive web interface, and RESTful API.

## Features

### 🍎 Food Database
- Comprehensive nutrition database with 10 different foods
- Detailed nutrition information (calories, protein, carbs, fat, fiber)
- Categorized by food types (fruit, vegetable, protein, grain, nut, dairy)
- Search and filter functionality

### 🧮 Nutrition Calculator
- Calculate total nutrition for multiple foods and quantities
- Real-time calculation with detailed breakdown
- Support for custom serving sizes

### 🌐 RESTful API
- Complete API for accessing nutrition data
- Category filtering and food-specific endpoints
- Nutrition calculation endpoints
- VitalsSync module integration

### 💻 Interactive Web Interface
- Modern, responsive design
- Tabbed interface for easy navigation
- Real-time API testing capabilities
- Beautiful gradient design with statistics dashboard

## Quick Start

### Prerequisites
- Python 3.8+
- Virtual environment (vnet-env included)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/benferizi/vitanet.git
   cd vitanet
   ```

2. **Activate virtual environment**
   ```bash
   source vnet-env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

5. **Open your browser**
   Navigate to `http://127.0.0.1:5000`

## API Endpoints

### Foods API
- `GET /api/foods` - Get all foods (optional ?category= filter)
- `GET /api/foods/{name}` - Get specific food by name
- `GET /api/categories` - Get all available categories

### Nutrition Calculator API
- `GET /api/calculate` - Calculate nutrition totals
  - Parameters: `?foods=apple,banana&quantities=1,2`

### VitalsSync Module
- `GET /vitalsync` - Access VitalsSync module

## Example API Usage

```bash
# Get all fruits
curl "http://127.0.0.1:5000/api/foods?category=fruit"

# Get nutrition for apple
curl "http://127.0.0.1:5000/api/foods/apple"

# Calculate nutrition for 1 apple and 2 bananas
curl "http://127.0.0.1:5000/api/calculate?foods=apple,banana&quantities=1,2"
```

## Testing

Run the comprehensive test suite:

```bash
python -m pytest tests/ -v
```

## Code Quality

Check code style with flake8:

```bash
flake8 app/ vitalsync.py run.py --max-line-length=120
```

## Project Structure

```
vitanet/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── routes.py           # API routes and nutrition database
│   └── templates/
│       └── index.html      # Main web interface
├── tests/
│   └── test_basic.py      # Comprehensive test suite
├── vitalsync.py           # VitalsSync module
├── run.py                 # Application entry point
├── requirements.txt       # Python dependencies
└── vnet-env/             # Virtual environment
```

## Technologies Used

- **Backend**: Flask, Flask-SQLAlchemy, Flask-CORS, Flask-Babel
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Data**: Pandas for data processing
- **Testing**: pytest
- **Code Quality**: flake8

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Made with ❤️ by Ben-A