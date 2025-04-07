# StudyShare

StudyShare is a collaborative platform for students and learners to share and collaborate on study notes. Users can create, share, and interact with Markdown-based notes, including support for mathematical expressions using LaTeX.

## Features

- **User Accounts**: Create accounts with unique usernames and emails.
- **Session-Based Authentication**: Secure login and logout functionality using sessions.
- **JWT Integration**: JWT tokens are used internally for session management.
- **Markdown Notes**: Share notes written in Markdown format for easy readability and formatting.
- **LaTeX Support**: Include mathematical expressions in notes using LaTeX.
- **Categories and Tags**: Organize notes by categories and tags for easy navigation.
- **Comments and Likes**: Interact with notes by commenting and liking posts.
- **Database Initialization**: Automatically create collections and indexes for users, posts, comments, likes, and categories.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/Drodr10/StudyShare.git
    cd StudyShare
    ```

2. Create a virtual environment and activate it:

    ```bash
    python -m venv .venv
    .venv\Scripts\activate  # On Windows
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Install MongoDB:
   - Download and install MongoDB Community Edition from the [official MongoDB website](https://www.mongodb.com/try/download/community).
   - Follow the installation instructions for your operating system.
   - Start the MongoDB server:
     - **Windows**: Run `mongod` in your terminal.
     - **macOS/Linux**: Use your package manager or run `mongod` directly.
   - Ensure MongoDB is running on `localhost:27017` (default configuration).

5. Configure the application:
   - Create a `.ini` file in the root directory with the following structure:

    ```ini
    [PROD]
    DB_URI = mongodb://localhost:27017
    DB_NAME = studyshare
    JWT_SECRET_KEY = your_jwt_secret_key
    SECRET_KEY = your_flask_secret_key
    ```

    Replace `your_jwt_secret_key` and `your_flask_secret_key` with strong, randomly generated keys. You can generate them using Python:

    ```python
    import secrets
    print(secrets.token_hex(32))
    ```

6. Initialize the database:

    ```bash
    flask --app flaskr init-db
    ```

    For testing purposes, you can initialize the test database:

    ```bash
    flask --app flaskr init-db --test
    ```

7. Run the application:

    ```bash
    flask --app flaskr run # --debug optional
    ```

8. Access the application:
   - Open your browser and navigate to <http://127.0.0.1:5000/>.
     - Note: will show an error for now as there are no templates

## Usage

- **Register**: Create an account with a unique username and email.
- **Login**: Log in to access your dashboard and interact with notes.
- **Dashboard**: View and manage your notes, categorized by tags and categories.
- **Create Notes**: Write and share notes in Markdown format.
- **Interact**: Comment on and like notes shared by others.

## Testing

Run the test suite to ensure everything is working as expected:

```bash
pytest --cov=flaskr --cov-report=term-missing
```

## Technologies Used

- **Backend**: Flask
- **Database**: MongoDB
- **Authentication**: JWT and Flask sessions
- **Testing**: Pytest

## Future Enhancements

- **Search Functionality**: Add a search bar to find notes by keywords.
- **Real-Time Collaboration**: Enable multiple users to edit notes simultaneously.
- **Notifications**: Notify users of new comments or likes on their notes.
