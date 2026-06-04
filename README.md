# 🎯 YouTube Quiz Generator

> Turn any YouTube video into an AI-powered quiz in under 30 seconds.

![Demo](https://img.shields.io/badge/Status-Live-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Next.js](https://img.shields.io/badge/Next.js-14-black)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Live Demo:** [youtube-quiz.vercel.app](https://youtube-quiz.vercel.app)  
**Backend API:** [youtube-quiz-backend.onrender.com/docs](https://youtube-quiz-backend-6bo6.onrender.com/docs)

---

## What it does

1. User pastes a YouTube URL
2. System extracts the video transcript automatically
3. Google Gemini AI analyzes the transcript
4. AI generates multiple-choice questions at Easy / Medium / Hard difficulty
5. User attempts the quiz
6. System scores answers and shows grade, accuracy, and explanations
7. Full quiz history saved per user

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Backend | FastAPI, Python 3.11 |
| Database | PostgreSQL (Supabase) |
| AI | Google Gemini 2.5 Flash Lite |
| Auth | JWT + bcrypt |
| Deployment | Vercel + Render |

---

## Architecture

---

## Features

- ✅ JWT Authentication (register/login)
- ✅ YouTube transcript extraction (no API key needed)
- ✅ AI question generation at 3 difficulty levels
- ✅ Real-time quiz interface with navigation
- ✅ Detailed results with per-question explanations
- ✅ Complete quiz history per user
- ✅ Production deployment on Vercel + Render

---

## Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL database (or Supabase free tier)
- Google Gemini API key (free at aistudio.google.com)

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Fill in DATABASE_URL, SECRET_KEY, GEMINI_API_KEY

uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

npm run dev
```

Open `http://localhost:3000`

---

## API Documentation

Interactive docs available at `/docs` when running locally or at the live backend URL.

Key endpoints:
- `POST /api/auth/register` — Create account
- `POST /api/auth/login` — Login, receive JWT
- `POST /api/quizzes/generate` — Generate quiz from YouTube URL
- `POST /api/quizzes/{id}/submit` — Submit answers, get score
- `GET /api/quizzes/my-attempts` — Quiz history

---

## Project Structure


---

## What I learned

- Full-stack development with Python + TypeScript
- REST API design with FastAPI
- LLM prompt engineering and structured output
- JWT authentication and security best practices
- PostgreSQL schema design and SQLAlchemy ORM
- Production deployment with CI/CD via GitHub

---

## Author

**Shrey** — Master's student in Data Science and Engineering  
[GitHub](https://github.com/shrey-004)