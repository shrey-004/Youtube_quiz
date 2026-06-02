# from pathlib import Path

# files = [
#     # Backend
#     "backend/app/__init__.py",
#     "backend/app/main.py",
#     "backend/app/config.py",

#     # API
#     "backend/app/api/__init__.py",
#     "backend/app/api/auth.py",
#     "backend/app/api/videos.py",
#     "backend/app/api/quizzes.py",
#     "backend/app/api/attempts.py",
#     "backend/app/api/users.py",

#     # Core
#     "backend/app/core/__init__.py",
#     "backend/app/core/transcript.py",
#     "backend/app/core/quiz_generator.py",
#     "backend/app/core/scorer.py",
#     "backend/app/core/security.py",

#     # AI
#     "backend/app/ai/__init__.py",
#     "backend/app/ai/base.py",
#     "backend/app/ai/claude_provider.py",
#     "backend/app/ai/openai_provider.py",
#     "backend/app/ai/prompts.py",

#     # Database
#     "backend/app/db/__init__.py",
#     "backend/app/db/session.py",
#     "backend/app/db/models.py",

#     # CRUD
#     "backend/app/db/crud/users.py",
#     "backend/app/db/crud/quizzes.py",
#     "backend/app/db/crud/attempts.py",

#     # Schemas
#     "backend/app/schemas/__init__.py",
#     "backend/app/schemas/auth.py",
#     "backend/app/schemas/quiz.py",
#     "backend/app/schemas/attempt.py",

#     # Backend files
#     "backend/.env",
#     "backend/.env.example",
#     "backend/requirements.txt",
#     "backend/Dockerfile",

#     # Alembic & Tests
#     "backend/alembic/.gitkeep",
#     "backend/tests/.gitkeep",

#     # Frontend pages
#     "frontend/src/app/page.tsx",
#     "frontend/src/app/login/page.tsx",
#     "frontend/src/app/dashboard/page.tsx",
#     "frontend/src/app/quiz/[id]/page.tsx",
#     "frontend/src/app/results/[id]/page.tsx",
#     "frontend/src/app/history/page.tsx",

#     # Components
#     "frontend/src/components/QuizCard.tsx",
#     "frontend/src/components/QuestionDisplay.tsx",
#     "frontend/src/components/ResultsSummary.tsx",
#     "frontend/src/components/HistoryList.tsx",

#     # Lib
#     "frontend/src/lib/api.ts",
#     "frontend/src/lib/auth.ts",

#     # Types
#     "frontend/src/types/index.ts",

#     # Frontend files
#     "frontend/.env.local",
#     "frontend/package.json",
#     "frontend/Dockerfile",

#     # Root files
#     "docker-compose.yml",
#     ".gitignore",
#     "README.md",
# ]

# for file in files:
#     path = Path(file)
#     path.parent.mkdir(parents=True, exist_ok=True)
#     path.touch(exist_ok=True)

# print("✅ Project structure created successfully!")