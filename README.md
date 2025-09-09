# Smart Study Planner

Smart Study Planner is a full-stack web application designed to help students efficiently manage their study tasks, track progress, and stay motivated. Built using Flask for the backend and vanilla HTML/CSS/JavaScript for the frontend, this app offers a clean, responsive interface with powerful features tailored for productivity and learning.

## Project Overview

- **User Authentication:** Secure registration and login with personalized profiles including user interests.
- **Task & Calendar Management:** A dynamic calendar interface to add, view, edit, and delete study tasks with real-time status updates.
- **Gamification:** Engage users with a motivational XP system, streak tracking, levels, badges, and progress indicators.
- **Motivational Guidance:** Daily personalized motivational messages to inspire consistent study habits.
- **Tech Stack:** Flask, SQLAlchemy, Flask-Login, PostgreSQL/SQLite, Vanilla HTML/CSS/JS, Jinja2 templates.

## Purpose

The project aims to empower students by organizing study schedules, gamifying progress to boost motivation, and integrating personalized encouragement for continuous learning.

---

Following sections break down the project folder and files, explaining their purpose and the logical flow of development to aid understanding and customization.

# Explanation of `config.py`

`
import os
from dotenv import load_dotenv
load_dotenv()

class Config:
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///study_planner.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False
`


---

This configuration file contains the essential settings for your Flask application.

- `import os`  
  Imports the built-in Python module for interacting with the operating system, allowing access to environment variables.

- `from dotenv import load_dotenv`  
  Imports `load_dotenv` from the `python-dotenv` package, which loads environment variables from a `.env` file into your Python environment.

- `load_dotenv()`  
  Executes the loading of environment variables from a `.env` file, enabling you to configure settings like secret keys and database URLs without hardcoding them.

- `class Config:`  
  Defines the configuration class where all setup variables for the Flask app live.

- `SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")`  
  Sets the secret key used by Flask for securely signing session cookies and other security-related needs. It attempts to retrieve `SECRET_KEY` from environment variables and falls back to `"dev-secret"` for development if not found. It is critical that in production a strong, unpredictable secret key is set via environment variables.

- `SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///study_planner.db")`  
  Configures the database connection string. It first tries to get a production database URL (e.g., PostgreSQL) from environment variables named `DATABASE_URL`. If unavailable, it defaults to a local SQLite database file named `study_planner.db`. This makes the app flexible for development and production environments without code changes.

- `SQLALCHEMY_TRACK_MODIFICATIONS = False`  
  Disables SQLAlchemy’s event system that tracks modifications to objects and emits signals, which is unnecessary here and saves memory. Also suppresses runtime warnings about this feature.

---

**Summary:**  
This `config.py` file helps your Flask app keep sensitive credentials and environment-specific settings outside version control and your source code while providing default values for easy development. The class-based structure makes it easy to extend and manage configuration settings in large projects.

# Explanation of `__init__.py`

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
```

- Imports Flask core and key extensions.
- Creates instances of database (`db`), migration tool (`migrate`), and authentication manager (`login_manager`).
- These instances are unbound initially for flexible application creation.

```python
def create_app():
app = Flask(name, template_folder='templates', static_folder='static')
app.config.from_object('config.Config')
```

- Defines the application factory `create_app`.
- Creates new Flask app object specifying templates and static folder locations.
- Loads configuration from the `Config` class in `config.py`.


```python
db.init_app(app)
migrate.init_app(app, db)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
```


- Binds extensions to the app instance.
- Sets default login route to redirect unauthorized users.

```python
from .auth import auth_bp
from .main import main_bp
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
```
`return app`

- Returns the fully configured Flask app instance ready to run.

---

This setup uses Flask's application factory pattern to modularize and initialize the app cleanly, allowing flexible app creation and easy extension integration.
