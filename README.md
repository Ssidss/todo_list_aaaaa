# Todo List Application

This project provides a minimal todo list application with:

- **FastAPI** backend
- **SQLite** database
- **React** frontend

## Features

- User registration and login
- Users can create teams and lists of tasks
- Roles for team memberships (principal, admin, member)
- Basic token-based authentication

## Running Backend

```bash
cd backend
uvicorn app:app --reload
```

The API server stores its SQLite database in `todo.db` inside the backend directory.

## Running Frontend

Open `frontend/index.html` in a browser. It uses CDN links for React and communicates with the backend using fetch requests.

## Testing

With Python installed, run:

```bash
python -m pytest
```

No JavaScript tests are provided. Running `npm test` will therefore fail.
