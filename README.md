# Don't Die

A social network that allows users to share meaningful messages with friends and family - words they'd want others to know if they were gone. The purpose is to create a space of authentic connection and remind people how much they matter.

## Features

- User registration and authentication
- Profile pages for each user
- Write and share tributes for friends and family
- View tributes written about you
- No anonymous posts - all content is tied to verified users

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up environment variables in a `.env` file
5. Initialize the database:
   ```
   flask db init
   flask db migrate
   flask db upgrade
   ```
6. Run the application:
   ```
   flask run
   ```

## Technology

Built with Flask, a lightweight Python web framework. # don-t-die
