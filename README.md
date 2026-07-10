# USER-AUTHENTICATION-using-FastAPI

# FastAPI Authentication Project

A simple Register / Login / Logout API built with FastAPI, SQLite, and JWT tokens.

## Files
- `main.py` — the app and the 3 endpoints
- `database.py` — SQLite connection setup
- `models.py` — database tables (User, BlacklistedToken)
- `schemas.py` — request/response data shapes
- `auth.py` — password hashing + JWT creation/verification
- `requirements.txt` — dependencies to install

## 1. Set up in VS Code

1. Install the **Python extension** in VS Code if you don't have it.
2. Open this folder in VS Code (`File > Open Folder`).
3. Open a terminal in VS Code (`Terminal > New Terminal`) and create a virtual environment:
   ```
   python -m venv venv
   ```
4. Activate it:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
5. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
6. Run the server:
   ```
   uvicorn main:app --reload
   ```
7. You should see it running at `http://127.0.0.1:8000`. A file called `auth.db` will be created automatically — that's your database, nothing else to set up.

You can also visit `http://127.0.0.1:8000/docs` — FastAPI auto-generates an interactive test page (Swagger UI), which is a great sanity check before you even open Postman.

## 2. Test in Postman

Make sure the server is running (step 6 above) before sending requests.

### a) Register a new user
- Method: `POST`
- URL: `http://127.0.0.1:8000/register`
- Body → raw → JSON:
  ```json
  {
    "username": "john",
    "email": "john@example.com",
    "password": "mypassword123"
  }
  ```
- Expected response: `201 Created` with the new user's id, username, email (no password shown back — good practice).

### b) Log in
- Method: `POST`
- URL: `http://127.0.0.1:8000/login`
- Body → **x-www-form-urlencoded** (not JSON — this is the OAuth2 standard FastAPI expects):
  | Key | Value |
  |---|---|
  | username | john |
  | password | mypassword123 |
- Expected response:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
  ```
- **Copy the `access_token` value** — you'll need it next.

### c) Access a protected route (proves login worked)
- Method: `GET`
- URL: `http://127.0.0.1:8000/me`
- Go to the **Authorization** tab in Postman → Type: **Bearer Token** → paste the `access_token`.
- Expected response: your user's id, username, email.
- If you skip the token or use a wrong one, you'll get `401 Unauthorized`.

### d) Log out
- Method: `POST`
- URL: `http://127.0.0.1:8000/logout`
- Authorization tab → Bearer Token → same `access_token` as before.
- Expected response:
  ```json
  { "message": "User 'john' logged out successfully" }
  ```
- Now try step (c) again with that same token — it will fail with `401 Unauthorized: Token has been revoked`. That's the logout actually taking effect, not just a fake success message.

## How it works (for your understanding, since your teacher will likely ask)

- **Passwords** are never stored as-is. `auth.py` hashes them with **bcrypt** before saving, and verifies by comparing hashes on login.
- **Login** issues a **JWT (JSON Web Token)** — a signed string that encodes the username and an expiry time (30 minutes by default). The client must send this token in the `Authorization: Bearer <token>` header on every request that needs to know who's logged in.
- **Logout** is tricky with JWTs because they're normally stateless (the server doesn't "remember" who's logged in). This project solves that by keeping a small **blacklist table** in the database — when you log out, the token gets added there, and `get_current_user` in `auth.py` checks that table on every request.

## Notes before submitting
- `SECRET_KEY` in `auth.py` is a placeholder. For real use, generate a proper one with `openssl rand -hex 32` and keep it out of source control (use an environment variable) — but for a class assignment, the placeholder is fine to mention you're aware of this.
- If Postman shows "Could not send request" — double check the server is still running in your VS Code terminal.
