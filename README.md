# DriftDater a Dating Application

**INFO3180 Group Project**

DriftDater is a dating application built using Vue 3 for the frontend and Flask for the backend. The aim of this project was to create a simple platform where users can connect, match and communicate witheach other.
---

## Team Members and Roles

- Cheyenne Gowie(620149270) - Project Manager - Planning, coordination, and overall structure 
- Adrienne Jobs(620172127) - Backend Lead - Flask API, database design, and backend logic 
- Akeelia Philbert(620160082) - Frontend Lead - Vue 3 interface, components, and routing 
- Shantauna Sibbey(620137399) - QA and Testing Lead - Testing, validation, and documentation 
- Brittannia Gregory(620156816) - Deployment Lead - Deployment and configuration 

---

## Features

### Core Features


- User Authentication - Register, login, and logout with password hashing 
- Profile Management - Create and edit profiles with pictures, bio, and interests 
- Smart Matching - Matching based on interests, age, location, and preferences 
- Like and Pass System - Mutual likes create confirmed matches 
- Messaging - Matched users can send and receive messages 
- Search and Filter - Filter profiles by name, location, age, and interests 
- Saved Profiles - Bookmark profiles to view later 

### Additional Features

- Profile visibility controls (public/private)
- Basic admin functionality
- Deployment on Render

---

## Technology Stack

- Frontend - Vue 3, Vite, Pinia, Vue Router
- Backend - Flask, SQLAlchemy, Flask-Migrate 
- Database - SQLite (development), PostgreSQL (production) 
- Authentication - Flask-Login, Flask-Bcrypt 
- API - REST with JSON and CORS 
- Deployment - Render 

---

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- npm

---

### Backend Setup

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv

# on Windows
venv\Scripts\activate

# on macOS / Linux
source venv/bin/activate

# Install the dependencies
pip install -r requirements.txt

# Copy the environment file
cp .env.example .env

# Run database migrations
flask --app app db init
flask --app app db migrate -m "Initial migration"
flask --app app db upgrade

# Seed the database with sample data
python seed.py

# Start the development server
flask --app app --debug run
```

> Backend runs at `http://localhost:5000`

---

### Frontend Setup

```bash
cd frontend

npm install
npm run dev
```

> Frontend runs at `http://localhost:5173`

---

## Test Accounts

The following accounts are available after running `python seed.py`:


- alice@example.com - password123 - Alice Wonder 
- bob@example.com - password123 - Bob Builder 
- grace@example.com - password123 - Grace Gamer 
- carol@example.com - password123 - Carol Cook 
- emma@example.com - password123 - Emma Artist 

---

## API Overview

**Base URL:** `http://localhost:5000/api`

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Log in |
| `POST` | `/auth/logout` | Log out |
| `GET` | `/auth/check` | Check authentication status |
| `GET` | `/auth/me` | Get current user info |

### Profiles

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/profiles` | Create a new profile |
| `GET` | `/profiles/me` | Get the current user's profile |
| `PUT` | `/profiles/me` | Update the current user's profile |
| `GET` | `/profiles/{user_id}` | Get a specific user's profile |
| `GET` | `/profiles/browse` | Browse unacted-on profiles |
| `GET` | `/profiles/picture/{filename}` | Serve a profile picture |

### Matches

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/matches/action` | Like or pass on a profile |
| `GET` | `/matches/mutual` | Get all mutual matches |
| `GET` | `/matches/count` | Get mutual match count |
| `GET` | `/matches/status/{user_id}` | Get match status with a user |

### Messages

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/messages/send` | Send a message |
| `GET` | `/messages/conversation/{user_id}` | Get conversation history |
| `GET` | `/messages/conversations` | Get all conversation summaries |

### Search

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/search` | Search profiles with filters |
| `GET` | `/search/interests` | Get all available interests |

### Favourites

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/favourites` | Get saved profiles |
| `POST` | `/favourites` | Save a profile |
| `DELETE` | `/favourites/{profile_id}` | Remove a saved profile |
| `GET` | `/favourites/check/{profile_id}` | Check if a profile is saved |

---

## Database Design

### Tables

| Table | Description |
|-------|-------------|
| `users` | Core authentication table |
| `profiles` | Extended user profile information |
| `interests` | Interest and hobby tags |
| `profile_interests` | Many-to-many join table for profiles and interests |
| `matches` | Like and pass actions between users |
| `messages` | Chat messages between matched users |
| `favourites` | Saved and bookmarked profiles |

### Relationships

- `users` have one `profile`
- `profiles` and `interests` share a many-to-many relationship via `profile_interests`
- `users` can have many `matches` as both the liker and the liked
- `users` can send and receive many `messages`
- `users` can save many `favourites`

---

## Security

- Passwords are hashed using **bcrypt**
- Authentication is handled with **Flask-Login**
- CORS is configured to allow only the frontend origin
- All endpoints include input validation
- SQL injection is prevented through the **SQLAlchemy ORM**
- Sensitive configuration is stored in a `.env` file and excluded from version control

---

## Known Issues

- Messaging uses polling every 3 seconds rather than a real-time WebSocket connection
- No email verification is performed on registration
- Profile images are stored locally and should use cloud storage in production
- SQLite is used in development only but PostgreSQL is required for production

---

## References

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Vue 3 Documentation](https://vuejs.org/)
- [Pinia Documentation](https://pinia.vuejs.org/)
- [Vue Router Documentation](https://router.vuejs.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Flask-Login Documentation](https://flask-login.readthedocs.io/)
