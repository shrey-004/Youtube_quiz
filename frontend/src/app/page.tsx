"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { authAPI } from "@/lib/api";
import Link from "next/link";

export default function LandingPage() {
  const router = useRouter();
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    setIsLoggedIn(authAPI.isLoggedIn());
  }, []);

  return (
    <div className="min-h-screen bg-gray-950 flex flex-col">
      {/* Navbar */}
      <nav className="border-b border-gray-800 px-6 py-4">
        <div className="max-w-6xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🎯</span>
            <span className="text-xl font-bold text-white">QuizTube</span>
          </div>
          <div className="flex gap-3">
            {isLoggedIn ? (
              <button
                onClick={() => router.push("/dashboard")}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-medium transition"
              >
                Dashboard
              </button>
            ) : (
              <>
                <Link
                  href="/login"
                  className="text-gray-300 hover:text-white px-4 py-2 rounded-lg font-medium transition"
                >
                  Login
                </Link>
                <Link
                  href="/register"
                  className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-medium transition"
                >
                  Get Started
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="flex-1 flex flex-col items-center justify-center px-6 py-20 text-center">
        <div className="max-w-3xl mx-auto">
          <div className="inline-flex items-center gap-2 bg-red-600/10 border border-red-600/20 text-red-400 px-4 py-2 rounded-full text-sm font-medium mb-8">
            <span>✨</span>
            <span>Powered by Google Gemini AI</span>
          </div>

          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6 leading-tight">
            Turn Any YouTube Video Into
            <span className="text-red-500"> An Instant Quiz</span>
          </h1>

          <p className="text-xl text-gray-400 mb-12 leading-relaxed">
            Paste a YouTube URL. Our AI extracts the transcript and generates
            multiple-choice questions at easy, medium, and hard difficulty.
            Test your knowledge instantly.
          </p>

          {/* Feature cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12 text-left">
            {[
              {
                icon: "📹",
                title: "Any YouTube Video",
                desc: "Lectures, tutorials, documentaries — if it has captions, we can quiz it.",
              },
              {
                icon: "🤖",
                title: "AI-Generated Questions",
                desc: "Gemini AI creates meaningful MCQs at 3 difficulty levels.",
              },
              {
                icon: "📊",
                title: "Instant Results",
                desc: "Score, grade, accuracy breakdown, and explanations for every question.",
              },
            ].map((feature) => (
              <div
                key={feature.title}
                className="bg-gray-900 border border-gray-800 rounded-xl p-6"
              >
                <div className="text-3xl mb-3">{feature.icon}</div>
                <h3 className="text-white font-semibold mb-2">{feature.title}</h3>
                <p className="text-gray-400 text-sm">{feature.desc}</p>
              </div>
            ))}
          </div>

          <Link
            href={isLoggedIn ? "/dashboard" : "/register"}
            className="inline-block bg-red-600 hover:bg-red-700 text-white text-lg font-semibold px-8 py-4 rounded-xl transition transform hover:scale-105"
          >
            {isLoggedIn ? "Go to Dashboard →" : "Start for Free →"}
          </Link>
        </div>
      </main>
    </div>
  );
}