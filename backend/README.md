# Pet Care Platform Backend

This is the FastAPI backend for the Premium Pet Care Platform. It handles user authentication, product catalogs, cart management, checkout, vet appointment scheduling, and AI chatbot integration via Google Gemini 2.0 Flash.

## 🛠 Tech Stack
- **Framework:** FastAPI
- **Database:** PostgreSQL (with `psycopg2-binary` for raw SQL execution)
- **Authentication:** JWT with `passlib` (bcrypt hashing)
- **AI Integration:** `google-genai`

## ⚙️ Setup & Installation

1. **Create and Activate a Virtual Environment:**
   ```bash
   python -m venv .venv
   
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r ../requirements.txt
   ```

3. **Configure Environment Variables:**
   Create a file named `secret.env` in the `backend/` directory. You will need to define your PostgreSQL database credentials and Gemini API key.
   
   **`secret.env` template:**
   ```env
   DB_NAME=petcare_db
   DB_USER=postgres
   DB_PASSWORD=your_secure_password
   DB_HOST=localhost
   DB_PORT=5432
   
   SECRET_KEY=your_super_secret_jwt_key
   ALGORITHM=HS256
   
   GEMINI_API_KEY=your_google_gemini_api_key
   ```

## 🚀 Running the Server

Once your database is running and `secret.env` is populated, start the development server using Uvicorn:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

## 📖 API Documentation

FastAPI automatically generates interactive Swagger documentation.
Once the server is running, navigate to:
**[http://localhost:8000/docs](http://localhost:8000/docs)**

This interface allows you to view all available routes, see required JSON schemas, and test the endpoints directly from your browser. Don't forget to use the "Authorize" button to pass your JWT token for protected routes!

## 📂 Structure Overview
- `main.py` - Application entry point and router registration.
- `confg.py` - Configuration loading and environment variable parsing.
- `database.py` - PostgreSQL connection initialization.
- `auth.py` - Login endpoint and JWT dependency checks.
- `gemini_api.py` - System prompts and connection logic for the Gemini AI.
- `Models/` - Raw SQL database interactions for all core entities.
- `routers/` - FastAPI endpoint definitions for Users, Products, Orders, Vets, Bookings, Carts, and the Chatbot.
- `schemas/` - Pydantic models for request validation and response formatting.
