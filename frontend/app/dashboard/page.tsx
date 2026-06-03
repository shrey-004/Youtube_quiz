"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { authAPI, quizAPI } from "@/lib/api";

export default function DashboardPage() {
  const router = useRouter();
  const [url, setUrl] = useState("");
  const [numEasy, setNumEasy] = useState(3);
  const [numMedium, setNumMedium] = useState(3);
  const [numHard, setNumHard] = useState(2);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [username, setUsername] = useState("");
  const [recentAttempts, setRecentAttempts] = useState<any[]>([]);

  useEffect(() => {
    // Redirect if not logged in
    if (!authAPI.isLoggedIn()) {
      router.push("/login");
      return;
    }
    setUsername(authAPI.getUsername());
    loadRecentAttempts();
  }, []);

  const loadRecentAttempts = async () => {
    try {
      const data = await quizAPI.getMyAttempts();
      setRecentAttempts(data.attempts?.slice(0, 3) || []);
    } catch {
      // Silently fail — not critical
    }
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    setError("");
    setLoading(true);

    try {
      const data = await quizAPI.generateQuiz(url, numEasy, numMedium, numHard);
      // Store quiz data in sessionStorage for the quiz page
      sessionStorage.setItem("current_quiz", JSON.stringify(data));
      router.push(`/quiz/${data.quiz_id}`);
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          "Failed to generate quiz. Please try another video."
      );
    } finally {
      setLoading(false);
    }
  };

  const gradeColor = (grade: string) => {
    const colors: Record<string, string> = {
      A: "text-green-400",
      B: "text-blue-400",
      C: "text-yellow-400",
      D: "text-orange-400",
      F: "text-red-400",
    };
    return colors[grade] || "text-gray-400";
  };

  return (
    <div className="min-h-screen bg-gray-950">
      {/* Navbar */}
      <nav className="border-b border-gray-800 px-6 py-4">
        <div className="max-w-4xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🎯</span>
            <span className="text-xl font-bold text-white">QuizTube</span>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.push("/history")}
              className="text-gray-400 hover:text-white transition text-sm"
            >
              History
            </button>
            <span className="text-gray-500">|</span>
            <span className="text-gray-300 text-sm">👋 {username}</span>
            <button
              onClick={authAPI.logout}
              className="text-gray-400 hover:text-red-400 transition text-sm"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="mb-10">
          <h1 className="text-3xl font-bold text-white mb-2">
            Generate a Quiz
          </h1>
          <p className="text-gray-400">
            Paste a YouTube URL and our AI will create a quiz from the video.
          </p>
        </div>

        {/* Quiz Generator Form */}
        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-8 mb-8">
          <form onSubmit={handleGenerate} className="space-y-6">
            {error && (
              <div className="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-3 rounded-lg text-sm">
                ❌ {error}
              </div>
            )}

            {/* URL Input */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                YouTube URL
              </label>
              <input
                type="url"
                required
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 text-white rounded-lg px-4 py-3 focus:outline-none focus:border-red-500 transition text-sm"
                placeholder="https://www.youtube.com/watch?v=..."
              />
            </div>

            {/* Question count sliders */}
            <div className="grid grid-cols-3 gap-6">
              {[
                {
                  label: "Easy",
                  value: numEasy,
                  set: setNumEasy,
                  color: "text-green-400",
                },
                {
                  label: "Medium",
                  value: numMedium,
                  set: setNumMedium,
                  color: "text-yellow-400",
                },
                {
                  label: "Hard",
                  value: numHard,
                  set: setNumHard,
                  color: "text-red-400",
                },
              ].map((item) => (
                <div key={item.label} className="text-center">
                  <label
                    className={`block text-sm font-medium mb-2 ${item.color}`}
                  >
                    {item.label}: {item.value}
                  </label>
                  <input
                    type="range"
                    min={1}
                    max={5}
                    value={item.value}
                    onChange={(e) => item.set(Number(e.target.value))}
                    className="w-full accent-red-500"
                  />
                  <div className="flex justify-between text-xs text-gray-600 mt-1">
                    <span>1</span>
                    <span>5</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-500">
                Total:{" "}
                <span className="text-white font-medium">
                  {numEasy + numMedium + numHard} questions
                </span>
                {" · "}Estimated time:{" "}
                <span className="text-white font-medium">
                  ~{Math.ceil((numEasy + numMedium + numHard) * 1.5)} min
                </span>
              </p>

              <button
                type="submit"
                disabled={loading}
                className="bg-red-600 hover:bg-red-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-semibold px-8 py-3 rounded-lg transition flex items-center gap-2"
              >
                {loading ? (
                  <>
                    <span className="animate-spin">⏳</span>
                    Generating... (~20s)
                  </>
                ) : (
                  <>🚀 Generate Quiz</>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Recent Attempts */}
        {recentAttempts.length > 0 && (
          <div>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-white">
                Recent Attempts
              </h2>
              <button
                onClick={() => router.push("/history")}
                className="text-red-400 hover:text-red-300 text-sm transition"
              >
                View all →
              </button>
            </div>
            <div className="space-y-3">
              {recentAttempts.map((attempt) => (
                <div
                  key={attempt.attempt_id}
                  className="bg-gray-900 border border-gray-800 rounded-xl p-4 flex items-center justify-between"
                >
                  <div>
                    <p className="text-white text-sm font-medium">
                      Quiz · {attempt.total_questions} questions
                    </p>
                    <p className="text-gray-500 text-xs mt-1">
                      {new Date(attempt.attempted_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="text-right">
                    <p
                      className={`text-2xl font-bold ${gradeColor(attempt.grade)}`}
                    >
                      {attempt.grade}
                    </p>
                    <p className="text-gray-400 text-xs">
                      {attempt.accuracy}% · {attempt.score}/
                      {attempt.total_questions}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}