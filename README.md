# 🐾 Premium Pet Care Platform

Welcome to the **Premium Pet Care Platform** — your one-stop solution for all pet needs. This platform integrates instant quick-commerce for pet supplies, a local veterinarian locator, and an AI-powered 24/7 veterinary assistant.

## 🌟 Key Features

1. **AI Veterinary Assistant (Powered by Gemini 2.0 Flash)**: A 24/7 chatbot to help triage pet symptoms, answer health questions, and recommend when an in-person visit is crucial. Includes a freemium limit (5 messages/day on free tier).
2. **Vet Finder & Appointment Booking**: Search for local veterinarians by proximity, specialty, or rating, and seamlessly book appointments.
3. **Quick Commerce Pet Store**: Browse products, add them to your cart, and place orders with instant inventory updates.

## 🏗️ Architecture

- **Backend**: Built with **FastAPI** and **Python 3.11+**, providing lightning-fast API responses and automatic OpenAPI documentation.
- **Database**: **PostgreSQL** using raw SQL queries for optimized, direct database interactions.
- **Frontend**: A sleek, responsive dashboard built with HTML, CSS, and JS (No heavy frameworks required). Features interactive tabs and premium styling.
- **AI Integration**: **Google Gemini 2.0 Flash** via the Google GenAI SDK.

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL Server
- Google Gemini API Key

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd "pet care"
   ```

2. **Set up the Database:**
   Ensure PostgreSQL is running. Create a new database for the pet care platform. Run the SQL schemas (derived from `srs_document.md` ER Diagram) to initialize your tables.

3. **Backend Setup:**
   See the [Backend README](backend/README.md) for detailed instructions on virtual environments, dependencies, and environment variables.

4. **Running the Application:**
   Start the FastAPI server:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

5. **Access the Frontend:**
   Simply open `frontend/index.html` or `frontend/dashboard.html` in your web browser. No frontend build step is required!

## 📚 API Documentation

Once the backend server is running, FastAPI automatically generates interactive API documentation.
Visit `http://localhost:8000/docs` to view the Swagger UI and test endpoints directly from your browser.

## 📄 License
See the `LICENSE` file for details.
