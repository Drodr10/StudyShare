# StudyShare

StudyShare is a collaborative web platform designed for students and learners to create, share, discover, and interact with study notes. It leverages Markdown for easy formatting, includes robust support for LaTeX mathematical expressions (via MathJax) and code syntax highlighting (via Pygments), and allows user interaction through likes and comments.

## Features

* **User Accounts:** Secure user registration and session-based login/logout.
* **Markdown Notes:** Create and view notes written in feature-rich Markdown, including tables and fenced code blocks.
* **LaTeX Support:** Seamlessly embed inline (`$..$`) and display (`$$..$$`) mathematical formulas using LaTeX syntax rendered by MathJax.
* **Code Syntax Highlighting:** Automatic syntax highlighting for various languages in code blocks using Pygments.
* **Post Management:** Users can create, view, edit, and delete their own posts.
* **Search & Sort:** Find posts using keyword search (title/content), filtering by category or tags (case-insensitive), and sorting by date, title, relevance, or popularity.
* **Interaction:** Like/unlike posts and add comments to foster discussion.
* **Database Initialization:** Includes a command to easily set up the required database schema and initial categories.

## Technologies Used

* **Backend:** Python 3, Flask Web Framework
* **Database:** MongoDB (accessed via PyMongo library)
* **Templating:** Jinja2 (via Flask)
* **Frontend:** HTML5, CSS3
* **Markdown Processing:** `python-markdown` library with `fenced_code`, `codehilite`, `tables`, `extra` extensions
* **Syntax Highlighting:** `Pygments` library
* **Math Rendering:** MathJax JavaScript library
* **Authentication:** Flask Sessions (potentially using JWT internally, handled by auth logic)
* **Testing:** Pytest (setup included)

## Installation & Setup

Follow these steps to run the project locally:

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/Drodr10/StudyShare.git
    cd StudyShare
    ```

2. **Create and Activate Virtual Environment:**
    * It's crucial to use a virtual environment.
    * **Windows (Command Prompt):**

        ```cmd
        python -m venv .venv
        .\.venv\Scripts\activate.bat
        ```

    * **Windows (PowerShell):**

        ```powershell
        python -m venv .venv
        .\.venv\Scripts\Activate.ps1
        # If blocked, may need: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
        ```

    * **Linux / macOS / WSL (Bash/Zsh):**

        ```bash
        python3 -m venv .venv
        source .venv/bin/activate
        ```

    * **WSL Note:** If you cloned the project on Windows and are running WSL, the `.venv` created by Windows (`Scripts` folder) **will not work correctly**. You must **delete** the existing `.venv` (`rm -rf .venv`) and recreate it *from within WSL* using `python3 -m venv .venv` before activating with `source .venv/bin/activate`.

3. **Install Dependencies:**
    * Ensure `pip` is up-to-date: `python -m pip install --upgrade pip`
    * Install required packages:

        ```bash
        pip install -r requirements.txt
        ```

    * **WSL/Ubuntu Note:** If creating the venv (`python3 -m venv .venv`) fails due to `ensurepip` or `venv` module issues, you may need to install it first: `sudo apt update && sudo apt install python3.12-venv` (adjust version if needed). Also ensure `pip` is installed for your system Python if needed: `sudo apt install python3-pip`. Remember to activate the venv *before* running `pip install -r requirements.txt` to avoid "externally-managed-environment" errors.

4. **Install and Run MongoDB:**
    * Download and install MongoDB Community Edition from the [official MongoDB website](https://www.mongodb.com/try/download/community). Follow instructions for your OS.
    * **Crucially, start the MongoDB server.**
        * On Windows, this is usually done by starting the "MongoDB Server" service (`services.msc`).
        * On macOS/Linux/WSL (if installed *inside* WSL), use `sudo systemctl start mongod` or `sudo service mongod start`.
    * Ensure it's running and accessible on `localhost:27017`.
    * **WSL Note:** If running MongoDB on the Windows host and accessing from WSL, you may need to edit the MongoDB config file (`mongod.cfg`) on Windows to change `net.bindIp` from `127.0.0.1` to `0.0.0.0` and restart the Windows MongoDB service to allow connections from WSL.

5. **Configure the Application:**
    * Create a file named `.env` in the project root directory. Add your secret keys:

        ```ini
        # Generate using: python -c "import secrets; print(secrets.token_hex(32))"
        SECRET_KEY=your_flask_secret_key_here
        JWT_SECRET_KEY=your_jwt_secret_key_here
        ```

    * Create a file named `.ini` in the project root directory. Configure your **local** MongoDB connection:

        ```ini
        [PROD]
        DB_URI = mongodb://localhost:27017
        DB_NAME = studyshare
        # DB_NAME = test_studyshare # Optionally use test DB name
        ```

6. **Initialize the Database:**
    * Run the Flask CLI command to create collections, indexes, and initial categories:

        ```bash
        flask --app flaskr init-db
        ```

    * *(Note: The `--test` flag is only used by this command if you specifically want to initialize a database named `test_studyshare` as configured in `db.py`'s command logic).*

7. **Run the Application:**

    ```bash
    # Standard run
    flask --app flaskr run

    # Optional: Run in debug mode (auto-reloads on code changes, shows more errors)
    flask --app flaskr run --debug
    ```

8. **Access the Application:**
    * Open your web browser and navigate to: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

## Usage

* **Register/Login:** Create an account or log in.
* **Browse Posts:** View existing posts on the index page. Use search, filter by category/tags, and sort options.
* **View Post:** Click a post title to see the fully rendered content (Markdown, LaTeX, Code Highlighting), existing comments, and like count.
* **Create/Edit/Delete:** Logged-in users can create new posts using Markdown, or edit/delete posts they own.
* **Interact:** Like/unlike posts and submit comments.
* **Dashboard:** Currently a placeholder; intended for future user profile/settings management.

## Testing

Unit tests are included. Run them using pytest (ensure it's installed from `requirements.txt`):

```bash
pytest --cov=flaskr --cov-report=term-missing
```

(Note: Tests may need updates to reflect latest features).

## Future Enhancements (Ideas)

* Editing/Content Creation:
  * Add "Copy" button to code blocks.
  * Implement live/side-by-side Markdown preview during post creation/editing.
* Post Interaction:
  * Allow editing/deleting of own comments.
  * Implement comment sorting.
  * Add dislike/downvote option.
  * Use icons (e.g., 👍) for Like button.
  * Dynamically update like state without page reload (AJAX/Fetch).
* Display & UI/UX:
  * Enhance overall visual design/styling.
  * Show creator username, like count, comment count, last updated date on index page posts.
* User Account/Dashboard:
  * Implement user profile editing (username, etc.).
  * Implement password change/reset (potentially via email).
* Media:
  * Auto-embed video links (YouTube, etc.) from post content.
* Moderation:
  * Basic admin/moderation tools. (e.g. banning, removing posts/comments)
