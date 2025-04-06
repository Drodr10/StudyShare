# StudyShare

StudyShare is a collaborative platform for students and learners to share and collaborate on study notes. Users can create, share, and interact with Markdown-based notes, including support for mathematical expressions using LaTeX.

## Features

- **User Accounts**: Create accounts with unique usernames and emails.
- **Markdown Notes**: Share notes written in Markdown format for easy readability and formatting.
- **LaTeX Support**: Include mathematical expressions in notes using LaTeX.
- **Categories and Tags**: Organize notes by categories and tags for easy navigation.
- **Comments and Likes**: Interact with notes by commenting and liking posts.

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

4. Configure the database:
   - Create a `.ini` file in the root directory with the following structure:

    ```ini
    [PROD]
    DB_URI = mongodb://localhost:27017
    DB_NAME = studyshare
    ```

5. Initialize the database:

    ```bash
    flask --app flaskr init-db
    ```

6. Run the application:

    ```bash
    flask --app flaskr run
    ```

### Usage

- Access the application at <http://127.0.0.1:5000/>.
- Create an account, share notes, and collaborate with others.

### Technologies Used

- **Backend**: Flask
- **Database**: MongoDB
