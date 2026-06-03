"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";

export default function ResultsPage() {
  const router = useRouter();
  const params = useParams();
  const [results, setResults] = useState<any>(null);
  const [expandedQuestion, setExpandedQuestion] = useState<string | null>(null);

  useEffect(() => {
    const stored = sessionStorage.getItem("quiz_results");
    if (stored) {
      setResults(JSON.parse(stored));
    } else {
      router.push("/dashboard");
    }
  }, []);

  if (!results) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="text-white animate-pulse">Loading results...</div>
      </div>
    );
  }

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

  const gradeBg = (grade: string) => {
    const colors: Record<string, string> = {
      A: "bg-green-500/10 border-green-500/20",
      B: "bg-blue-500/10 border-blue-500/20",
      C: "bg-yellow-500/10 border-yellow-500/20",
      D: "bg-orange-500/10 border-orange-500/20",
      F: "bg-red-500/10 border-red-500/20",
    };
    return colors[grade] || "bg-gray-500/10 border-gray-500/20";
  };

  return (
    <div className="min-h-screen bg-gray-950 px-4 py-8">
      <div className="max-w-2xl mx-auto">
        {/* Score Card */}
        <div
          className={`border rounded-2xl p-8 text-center mb-8 ${gradeBg(
            results.grade
          )}`}
        >
          <p className="text-gray-400 text-sm mb-2">Your Grade</p>
          <p className={`text-8xl font-bold mb-4 ${gradeColor(results.grade)}`}>
            {results.grade}
          </p>
          <p className="text-white text-xl font-semibold mb-1">
            {results.correct_count} / {results.total_questions} correct
          </p>
          <p className="text-gray-400 text-lg">{results.accuracy}% accuracy</p>
          <p className="text-gray-300 mt-4 text-sm italic">
            {results.performance_message}
          </p>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          {[
            {
              label: "Correct",
              value: results.correct_count,
              color: "text-green-400",
            },
            {
              label: "Wrong",
              value: results.wrong_count,
              color: "text-red-400",
            },
            {
              label: "Skipped",
              value: results.skipped_count,
              color: "text-gray-400",
            },
          ].map((stat) => (
            <div
              key={stat.label}
              className="bg-gray-900 border border-gray-800 rounded-xl p-4 text-center"
            >
              <p className={`text-3xl font-bold ${stat.color}`}>{stat.value}</p>
              <p className="text-gray-500 text-sm mt-1">{stat.label}</p>
            </div>
          ))}
        </div>

        {/* Difficulty Breakdown */}
        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 mb-8">
          <h3 className="text-white font-semibold mb-4">
            Performance by Difficulty
          </h3>
          <div className="space-y-3">
            {Object.entries(results.difficulty_breakdown).map(
              ([diff, stats]: [string, any]) => {
                if (stats.total === 0) return null;
                const colors: Record<string, string> = {
                  easy: "bg-green-500",
                  medium: "bg-yellow-500",
                  hard: "bg-red-500",
                };
                return (
                  <div key={diff}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-300 capitalize">{diff}</span>
                      <span className="text-gray-400">
                        {stats.correct}/{stats.total} · {stats.accuracy}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-800 rounded-full h-2">
                      <div
                        className={`${colors[diff]} h-2 rounded-full transition-all`}
                        style={{ width: `${stats.accuracy}%` }}
                      />
                    </div>
                  </div>
                );
              }
            )}
          </div>
        </div>

        {/* Per Question Results */}
        <div className="mb-8">
          <h3 className="text-white font-semibold mb-4">Question Review</h3>
          <div className="space-y-3">
            {results.question_results.map((qr: any, i: number) => (
              <div
                key={qr.question_id}
                className={`border rounded-xl overflow-hidden ${
                  qr.is_correct
                    ? "border-green-500/20"
                    : "border-red-500/20"
                }`}
              >
                {/* Question header */}
                <button
                  onClick={() =>
                    setExpandedQuestion(
                      expandedQuestion === qr.question_id
                        ? null
                        : qr.question_id
                    )
                  }
                  className="w-full text-left p-4 bg-gray-900 hover:bg-gray-800 transition flex items-start gap-3"
                >
                  <span
                    className={`mt-0.5 flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                      qr.is_correct
                        ? "bg-green-500/20 text-green-400"
                        : "bg-red-500/20 text-red-400"
                    }`}
                  >
                    {qr.is_correct ? "✓" : "✗"}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="text-white text-sm font-medium leading-relaxed">
                      Q{i + 1}. {qr.question_text}
                    </p>
                    <p className="text-gray-500 text-xs mt-1 capitalize">
                      {qr.difficulty}
                    </p>
                  </div>
                  <span className="text-gray-600 text-xs flex-shrink-0">
                    {expandedQuestion === qr.question_id ? "▲" : "▼"}
                  </span>
                </button>

                {/* Expanded detail */}
                {expandedQuestion === qr.question_id && (
                  <div className="p-4 bg-gray-900/50 border-t border-gray-800 space-y-3">
                    {!qr.is_correct && qr.user_answer && (
                      <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3">
                        <p className="text-red-400 text-xs font-medium mb-1">
                          Your answer:
                        </p>
                        <p className="text-red-300 text-sm">{qr.user_answer}</p>
                      </div>
                    )}
                    <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-3">
                      <p className="text-green-400 text-xs font-medium mb-1">
                        Correct answer:
                      </p>
                      <p className="text-green-300 text-sm">
                        {qr.correct_answer}
                      </p>
                    </div>
                    <div className="bg-gray-800 rounded-lg p-3">
                      <p className="text-blue-400 text-xs font-medium mb-1">
                        💡 Explanation:
                      </p>
                      <p className="text-gray-300 text-sm leading-relaxed">
                        {qr.explanation}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex gap-4">
          <button
            onClick={() => router.push("/dashboard")}
            className="flex-1 bg-red-600 hover:bg-red-700 text-white font-semibold py-3 rounded-xl transition"
          >
            Generate New Quiz
          </button>
          <button
            onClick={() => router.push("/history")}
            className="flex-1 bg-gray-800 hover:bg-gray-700 text-white font-semibold py-3 rounded-xl transition"
          >
            View History
          </button>
        </div>
      </div>
    </div>
  );
}