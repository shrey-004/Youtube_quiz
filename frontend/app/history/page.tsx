"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { authAPI, quizAPI } from "@/lib/api";

export default function HistoryPage() {
  const router = useRouter();
  const [attempts, setAttempts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!authAPI.isLoggedIn()) {
      router.push("/login");
      return;
    }
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const data = await quizAPI.getMyAttempts();
      setAttempts(data.attempts || []);
    } catch {
      setAttempts([]);
    } finally {
      setLoading(false);
    }
  };

  const gradeColor = (grade: string) => {
    const colors: Record<string, string> = {
      A: "text-green-400 bg-green-500/10 border-green-500/20",
      B: "text-blue-400 bg-blue-500/10 border-blue-500/20",
      C: "text-yellow-400 bg-yellow-500/10 border-yellow-500/20",
      D: "text-orange-400 bg-orange-500/10 border-orange-500/20",
      F: "text-red-400 bg-red-500/10 border-red-500/20",
    };
    return colors[grade] || "text-gray-400 bg-gray-500/10 border-gray-500/20";
  };

  return (
    <div className="min-h-screen bg-gray-950">
      <nav className="border-b border-gray-800 px-6 py-4">
        <div className="max-w-4xl mx-auto flex justify-between items-center">
          <button
            onClick={() => router.push("/dashboard")}
            className="flex items-center gap-2 text-gray-400 hover:text-white transition"
          >
            <span className="text-2xl">🎯</span>
            <span className="text-xl font-bold text-white">QuizTube</span>
          </button>
          <button
            onClick={() => router.push("/dashboard")}
            className="text-gray-400 hover:text-white transition text-sm"
          >
            ← Dashboard
          </button>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto px-6 py-12">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Quiz History</h1>
          <p className="text-gray-400">All your past quiz attempts</p>
        </div>

        {loading ? (
          <div className="text-center py-20">
            <div className="text-gray-500 animate-pulse">
              Loading history...
            </div>
          </div>
        ) : attempts.length === 0 ? (
          <div className="text-center py-20">
            <span className="text-6xl block mb-4">📭</span>
            <p className="text-gray-400 mb-6">No quiz attempts yet.</p>
            <button
              onClick={() => router.push("/dashboard")}
              className="bg-red-600 hover:bg-red-700 text-white font-semibold px-6 py-3 rounded-xl transition"
            >
              Generate Your First Quiz
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {attempts.map((attempt, i) => (
              <div
                key={attempt.attempt_id}
                className="bg-gray-900 border border-gray-800 rounded-2xl p-6 flex items-center justify-between hover:border-gray-700 transition"
              >
                <div className="flex items-center gap-5">
                  <div
                    className={`w-14 h-14 rounded-xl border flex items-center justify-center text-2xl font-bold flex-shrink-0 ${gradeColor(
                      attempt.grade
                    )}`}
                  >
                    {attempt.grade}
                  </div>
                  <div>
                    <p className="text-white font-medium">
                      Quiz · {attempt.total_questions} questions
                    </p>
                    <p className="text-gray-400 text-sm mt-0.5">
                      {attempt.score}/{attempt.total_questions} correct ·{" "}
                      {attempt.accuracy}% accuracy
                    </p>
                    <p className="text-gray-600 text-xs mt-1">
                      {new Date(attempt.attempted_at).toLocaleDateString(
                        "en-IN",
                        {
                          day: "numeric",
                          month: "short",
                          year: "numeric",
                          hour: "2-digit",
                          minute: "2-digit",
                        }
                      )}
                    </p>
                  </div>
                </div>

                {/* Accuracy bar */}
                <div className="hidden md:block w-32">
                  <div className="text-right text-xs text-gray-500 mb-1">
                    {attempt.accuracy}%
                  </div>
                  <div className="w-full bg-gray-800 rounded-full h-2">
                    <div
                      className="bg-red-500 h-2 rounded-full"
                      style={{ width: `${attempt.accuracy}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}