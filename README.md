# vitanet

A Flask web application for health and vital signs management.

## Development Setup

### Using GitHub Codespaces (Recommended)

This repository is configured with a GitHub Codespace that provides a pre-configured development environment with Python 3.12 and all required dependencies.

1. Click the "Code" button on GitHub
2. Select "Codespaces" tab
3. Click "Create codespace on main"

The codespace will automatically:
- Set up Python 3.12 environment
- Install all dependencies from `requirements.txt`
- Configure VS Code with Python development extensions
- Forward port 5000 for the Flask application

### Local Development

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Run the application: `python app.py`

The application will be available at `http://localhost:5000`

## Running Tests

```bash
pytest tests/
```

## Linting

```bash
flake8 app.py vitalsync.py run.py
```