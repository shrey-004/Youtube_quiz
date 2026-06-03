"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { quizAPI } from "@/lib/api";

interface Question {
  id: string;
  question_number: number;
  question_text: string;
  options: string[];
  difficulty: string;
}

export default function QuizPage() {
  const router = useRouter();
  const params = useParams();
  const quizId = params.id as string;

  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    // Load quiz data from sessionStorage (set by dashboard)
    const stored = sessionStorage.getItem("current_quiz");
    if (stored) {
      const quizData = JSON.parse(stored);
      setQuestions(quizData.questions || []);
    } else {
      router.push("/dashboard");
    }
  }, []);

  const currentQuestion = questions[currentIndex];
  const totalQuestions = questions.length;
  const answeredCount = Object.keys(answers).length;
  const progress = totalQuestions > 0 ? (answeredCount / totalQuestions) * 100 : 0;

  const selectAnswer = (questionId: string, answer: string) => {
    setAnswers((prev) => ({ ...prev, [questionId]: answer }));
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    setError("");

    try {
      const formattedAnswers = Object.entries(answers).map(
        ([question_id, selected_answer]) => ({
          question_id,
          selected_answer,
        })
      );

      const result = await quizAPI.submitQuiz(quizId, formattedAnswers);
      // Store results for the results page
      sessionStorage.setItem("quiz_results", JSON.stringify(result));
      sessionStorage.setItem("quiz_questions", JSON.stringify(questions));
      router.push(`/results/${quizId}`);
    } catch (err: any) {
      setError("Failed to submit quiz. Please try again.");
      setSubmitting(false);
    }
  };

  const difficultyColor = (difficulty: string) => {
    const colors: Record<string, string> = {
      easy: "bg-green-500/10 text-green-400 border-green-500/20",
      medium: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20",
      hard: "bg-red-500/10 text-red-400 border-red-500/20",
    };
    return colors[difficulty] || "bg-gray-500/10 text-gray-400";
  };

  if (questions.length === 0) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="text-white text-xl animate-pulse">Loading quiz...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 px-4 py-8">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <button
            onClick={() => router.push("/dashboard")}
            className="text-gray-400 hover:text-white transition text-sm"
          >
            ← Exit Quiz
          </button>
          <span className="text-gray-400 text-sm">
            {answeredCount}/{totalQuestions} answered
          </span>
        </div>

        {/* Progress bar */}
        <div className="w-full bg-gray-800 rounded-full h-2 mb-8">
          <div
            className="bg-red-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>

        {/* Question navigation dots */}
        <div className="flex gap-2 flex-wrap mb-8">
          {questions.map((q, i) => (
            <button
              key={q.id}
              onClick={() => setCurrentIndex(i)}
              className={`w-8 h-8 rounded-full text-xs font-medium transition ${
                i === currentIndex
                  ? "bg-red-600 text-white"
                  : answers[q.id]
                  ? "bg-green-600/30 text-green-400 border border-green-600/50"
                  : "bg-gray-800 text-gray-400 hover:bg-gray-700"
              }`}
            >
              {i + 1}
            </button>
          ))}
        </div>

        {/* Current Question */}
        {currentQuestion && (
          <div className="bg-gray-900 border border-gray-800 rounded-2xl p-8">
            {/* Difficulty badge */}
            <span
              className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border mb-4 ${difficultyColor(
                currentQuestion.difficulty
              )}`}
            >
              {currentQuestion.difficulty.charAt(0).toUpperCase() +
                currentQuestion.difficulty.slice(1)}
            </span>

            {/* Question text */}
            <h2 className="text-white text-xl font-medium mb-8 leading-relaxed">
              <span className="text-gray-500 mr-2">
                Q{currentQuestion.question_number}.
              </span>
              {currentQuestion.question_text}
            </h2>

            {/* Options */}
            <div className="space-y-3">
              {currentQuestion.options.map((option, i) => {
                const isSelected = answers[currentQuestion.id] === option;
                const letters = ["A", "B", "C", "D"];

                return (
                  <button
                    key={i}
                    onClick={() => selectAnswer(currentQuestion.id, option)}
                    className={`w-full text-left px-5 py-4 rounded-xl border transition flex items-center gap-4 ${
                      isSelected
                        ? "bg-red-600/20 border-red-500 text-white"
                        : "bg-gray-800/50 border-gray-700 text-gray-300 hover:border-gray-500 hover:bg-gray-800"
                    }`}
                  >
                    <span
                      className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0 ${
                        isSelected
                          ? "bg-red-600 text-white"
                          : "bg-gray-700 text-gray-400"
                      }`}
                    >
                      {letters[i]}
                    </span>
                    <span className="text-sm leading-relaxed">{option}</span>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Navigation */}
        <div className="flex justify-between items-center mt-6">
          <button
            onClick={() => setCurrentIndex(Math.max(0, currentIndex - 1))}
            disabled={currentIndex === 0}
            className="px-5 py-2 bg-gray-800 hover:bg-gray-700 disabled:opacity-30 disabled:cursor-not-allowed text-white rounded-lg transition text-sm"
          >
            ← Previous
          </button>

          {currentIndex < totalQuestions - 1 ? (
            <button
              onClick={() =>
                setCurrentIndex(Math.min(totalQuestions - 1, currentIndex + 1))
              }
              className="px-5 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition text-sm"
            >
              Next →
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={submitting || answeredCount === 0}
              className="px-8 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition text-sm"
            >
              {submitting ? "Submitting..." : `Submit Quiz (${answeredCount}/${totalQuestions})`}
            </button>
          )}
        </div>

        {error && (
          <p className="text-red-400 text-sm text-center mt-4">{error}</p>
        )}
      </div>
    </div>
  );
}