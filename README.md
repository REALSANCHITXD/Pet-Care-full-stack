# 🐾 Premium Pet Care Platform

Welcome to the **Premium Pet Care Platform** — your one-stop solution for all pet needs. This platform integrates instant quick-commerce for pet supplies, a local veterinarian locator, and an AI-powered 24/7 veterinary assistant.

## 🌟 Key Features

1. **AI Veterinary Assistant (Powered by Gemini 2.0 Flash)**: A 24/7 chatbot to help triage pet symptoms, answer health questions, and recommend when an in-person visit is crucial. Includes a freemium rate-limiting system (5 messages/day on free tier).
2. **Vet Finder & Appointment Booking**: Search for local veterinarians by proximity, specialty, or rating, and seamlessly book appointments.
3. **Quick Commerce Pet Store**: Browse products, add them to your cart, and checkout with instant inventory updates.
4. **Secure Authentication**: JWT-based authentication with secure password hashing for user accounts (Owner, Vet, and Customer roles).

## 🏗️ Architecture

- **Backend Framework**: Built with **FastAPI** (Python 3.11+), providing lightning-fast API responses and automatic OpenAPI documentation.
- **ORM & Data Validation**: Uses **SQLModel** (SQLAlchemy + Pydantic) for safe, injection-proof database interactions and strict schema validation.
- **Database**: Cloud-hosted **PostgreSQL on Supabase**, utilizing connection pooling for scalability.
- **Dependency Injection**: Utilizes FastAPI's `Depends` for secure, per-request database session management and route protection.
- **AI Integration**: **Google Gemini 2.0 Flash** via the Google GenAI SDK.
- **Frontend**: A sleek, responsive dashboard built with HTML, CSS, and JS (No heavy frameworks required). Features interactive tabs and premium styling.

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL Server (or a Supabase account)
- Google Gemini API Key

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd "pet care"
   ```

2. **Backend Environment Setup:**
   Create a `.venv`, install dependencies, and configure your `secret.env` file with your database and API keys.
   ```bash
   cd backend
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Running the Application:**
   Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

4. **Access the Frontend:**
   Start a simple Python HTTP server in the `frontend/` directory, or just open `frontend/index.html` in your web browser.

## 📚 API Documentation

Once the backend server is running, FastAPI automatically generates interactive API documentation.
Visit `http://localhost:8000/docs` to view the Swagger UI and test endpoints directly from your browser.

## 📄 License
See the `LICENSE` file for details.
