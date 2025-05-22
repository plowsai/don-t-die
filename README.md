# Don't Die

A social network that allows users to share meaningful messages with friends and family - words they'd want others to know if they were gone. The purpose is to create a space of authentic connection and remind people how much they matter.

## Features

- User registration and authentication with encrypted passwords
- Profile pages for each user with customizable information and profile pictures
- Connect with friends through a friend request system
- Write and share tributes for friends and family
- Control visibility of tributes (private or visible to recipient)
- View tributes written about you
- No anonymous posts - all content is tied to verified users
- Mobile-responsive design using Bootstrap 5

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/dont-die.git
   cd dont-die
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables in a `.env` file:
   ```
   # Copy the example file
   cp .env.example .env
   
   # Edit the file with your settings
   # Generate a secure secret key for production
   # You can use: python -c "import secrets; print(secrets.token_hex(16))"
   ```

5. Initialize the database:
   ```
   # This creates the database tables automatically when you first run the app
   # No need to run flask db commands as the app does this for you
   ```

6. Run the application:
   ```
   python app.py
   # or
   flask run
   ```

7. Visit `http://127.0.0.1:5000` in your browser

## Usage

1. Register an account with your real identity
2. Update your profile with your information and photo
3. Connect with friends and family members
4. Write tributes for your friends - share what you appreciate about them
5. Control the visibility of your tributes
6. View tributes others have written about you

## Technology

- **Backend**: Flask (Python web framework)
- **Database**: SQLAlchemy with SQLite (can be configured for PostgreSQL)
- **Authentication**: Flask-Login, Flask-Bcrypt
- **Forms**: Flask-WTF, WTForms
- **Frontend**: Bootstrap 5, Font Awesome
- **Image Processing**: Pillow

## Project Structure

- `app.py` - Application entry point
- `dontdie/` - Main package
  - `__init__.py` - Application factory pattern
  - `models.py` - Database models
  - `main/` - Main routes (home, about)
  - `users/` - User authentication and profile management
  - `tributes/` - Tribute creation and management
  - `errors/` - Error handlers
  - `static/` - Static files (CSS, images)
  - `templates/` - Jinja2 templates

## Security

- Passwords are hashed using Bcrypt
- CSRF protection on all forms
- Flask-Login for secure session management
- Proper permission checks on all routes

## License

MIT

## Running the Application

### Development Mode
```bash
python run.py
```

### Production Mode with Gunicorn
```bash
# Run with default settings
gunicorn wsgi:app

# Run with configuration file
gunicorn -c gunicorn_config.py wsgi:app

# Run in background with logs
gunicorn -c gunicorn_config.py wsgi:app --daemon --log-file gunicorn.log
```
