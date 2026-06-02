from pathlib import Path

files = [
    # Backend
    "youtube-quiz-generator/backend/app/__init__.py",
    "youtube-quiz-generator/backend/app/main.py",
    "youtube-quiz-generator/backend/app/config.py",

    # API
    "youtube-quiz-generator/backend/app/api/__init__.py",
    "youtube-quiz-generator/backend/app/api/auth.py",
    "youtube-quiz-generator/backend/app/api/videos.py",
    "youtube-quiz-generator/backend/app/api/quizzes.py",
    "youtube-quiz-generator/backend/app/api/attempts.py",
    "youtube-quiz-generator/backend/app/api/users.py",

    # Core
    "youtube-quiz-generator/backend/app/core/__init__.py",
    "youtube-quiz-generator/backend/app/core/transcript.py",
    "youtube-quiz-generator/backend/app/core/quiz_generator.py",
    "youtube-quiz-generator/backend/app/core/scorer.py",
    "youtube-quiz-generator/backend/app/core/security.py",

    # AI
    "youtube-quiz-generator/backend/app/ai/__init__.py",
    "youtube-quiz-generator/backend/app/ai/base.py",
    "youtube-quiz-generator/backend/app/ai/claude_provider.py",
    "youtube-quiz-generator/backend/app/ai/openai_provider.py",
    "youtube-quiz-generator/backend/app/ai/prompts.py",

    # Database
    "youtube-quiz-generator/backend/app/db/__init__.py",
    "youtube-quiz-generator/backend/app/db/session.py",
    "youtube-quiz-generator/backend/app/db/models.py",

    # CRUD
    "youtube-quiz-generator/backend/app/db/crud/users.py",
    "youtube-quiz-generator/backend/app/db/crud/quizzes.py",
    "youtube-quiz-generator/backend/app/db/crud/attempts.py",

    # Schemas
    "youtube-quiz-generator/backend/app/schemas/__init__.py",
    "youtube-quiz-generator/backend/app/schemas/auth.py",
    "youtube-quiz-generator/backend/app/schemas/quiz.py",
    "youtube-quiz-generator/backend/app/schemas/attempt.py",

    # Backend Root Files
    "youtube-quiz-generator/backend/.env",
    "youtube-quiz-generator/backend/.env.example",
    "youtube-quiz-generator/backend/requirements.txt",
    "youtube-quiz-generator/backend/Dockerfile",

    # Alembic
    "youtube-quiz-generator/backend/alembic/.gitkeep",

    # Tests
    "youtube-quiz-generator/backend/tests/.gitkeep",

    # Frontend Pages
    "youtube-quiz-generator/frontend/src/app/page.tsx",
    "youtube-quiz-generator/frontend/src/app/login/page.tsx",
    "youtube-quiz-generator/frontend/src/app/dashboard/page.tsx",
    "youtube-quiz-generator/frontend/src/app/quiz/[id]/page.tsx",
    "youtube-quiz-generator/frontend/src/app/results/[id]/page.tsx",
    "youtube-quiz-generator/frontend/src/app/history/page.tsx",

    # Components
    "youtube-quiz-generator/frontend/src/components/QuizCard.tsx",
    "youtube-quiz-generator/frontend/src/components/QuestionDisplay.tsx",
    "youtube-quiz-generator/frontend/src/components/ResultsSummary.tsx",
    "youtube-quiz-generator/frontend/src/components/HistoryList.tsx",

    # Lib
    "youtube-quiz-generator/frontend/src/lib/api.ts",
    "youtube-quiz-generator/frontend/src/lib/auth.ts",

    # Types
    "youtube-quiz-generator/frontend/src/types/index.ts",

    # Frontend Root Files
    "youtube-quiz-generator/frontend/.env.local",
    "youtube-quiz-generator/frontend/package.json",
    "youtube-quiz-generator/frontend/Dockerfile",

    # Project Root
    "youtube-quiz-generator/docker-compose.yml",
    "youtube-quiz-generator/.gitignore",
    "youtube-quiz-generator/README.md",
]

for file in files:
    path = Path(file)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)

print("✅ YouTube Quiz Generator project structure created successfully!")
print("📁 Root folder: youtube-quiz-generator")