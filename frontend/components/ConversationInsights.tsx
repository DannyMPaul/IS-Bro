"use client";

import React, { useState, useEffect } from "react";
import {
  Brain,
  TrendingUp,
  MessageCircle,
  Clock,
  ArrowRight,
  Lightbulb,
  Target,
  BarChart3,
  X,
  RefreshCw,
} from "lucide-react";

interface ConversationInsights {
  conversation_id: string;
  title: string;
  stage: string;
  total_messages: number;
  engagement_score: number;
  key_themes: string[];
  sentiment_trend: "positive" | "neutral" | "negative";
  complexity_level: "low" | "medium" | "high";
  suggested_next_steps: string[];
  follow_up_questions: string[];
  estimated_completion: string;
  insights_summary: string;
  generated_at: string;
}

interface ConversationInsightsProps {
  conversationId: string | null;
  isOpen: boolean;
  onClose: () => void;
  onQuestionSelect: (question: string) => void;
}

export const ConversationInsights: React.FC<ConversationInsightsProps> = ({
  conversationId,
  isOpen,
  onClose,
  onQuestionSelect,
}) => {
  const [insights, setInsights] = useState<ConversationInsights | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && conversationId) {
      fetchInsights();
    }
  }, [isOpen, conversationId]);

  const fetchInsights = async () => {
    if (!conversationId) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `http://localhost:8000/api/conversations/${conversationId}/insights`
      );

      if (!response.ok) {
        throw new Error("Failed to fetch insights");
      }

      const data = await response.json();
      setInsights(data);
    } catch (error) {
      console.error("Failed to fetch insights:", error);
      setError("Failed to load conversation insights");
    } finally {
      setIsLoading(false);
    }
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case "positive":
        return "text-green-600 dark:text-green-400";
      case "negative":
        return "text-red-600 dark:text-red-400";
      default:
        return "text-blue-600 dark:text-blue-400";
    }
  };

  const getComplexityColor = (complexity: string) => {
    switch (complexity) {
      case "low":
        return "bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-300";
      case "high":
        return "bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-300";
      default:
        return "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-300";
    }
  };

  const getEngagementLevel = (score: number) => {
    if (score >= 8)
      return { label: "High", color: "text-green-600 dark:text-green-400" };
    if (score >= 6)
      return { label: "Medium", color: "text-yellow-600 dark:text-yellow-400" };
    return { label: "Low", color: "text-red-600 dark:text-red-400" };
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-100 dark:bg-slate-950 border border-gray-300 dark:border-slate-700 rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden">
        <div className="p-6 border-b border-gray-300 dark:border-slate-700">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-blue-900 dark:text-yellow-400 flex items-center">
              <Brain className="w-6 h-6 mr-2" />
              Conversation Insights
            </h2>
            <div className="flex items-center space-x-2">
              <button
                onClick={fetchInsights}
                disabled={isLoading}
                className="p-2 text-blue-700 dark:text-yellow-300 hover:text-blue-900 dark:hover:text-yellow-100 disabled:opacity-50"
              >
                <RefreshCw
                  className={`w-5 h-5 ${isLoading ? "animate-spin" : ""}`}
                />
              </button>
              <button
                onClick={onClose}
                className="text-blue-700 dark:text-yellow-300 hover:text-blue-900 dark:hover:text-yellow-100 p-2"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>

        <div className="p-6 overflow-y-auto max-h-[75vh]">
          {isLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full mx-auto mb-4"></div>
              <p className="text-blue-800 dark:text-yellow-300">
                Analyzing conversation...
              </p>
            </div>
          ) : error ? (
            <div className="text-center py-8">
              <Brain className="w-12 h-12 text-red-600 dark:text-red-400 mx-auto mb-4 opacity-50" />
              <p className="text-red-800 dark:text-red-300">{error}</p>
              <button
                onClick={fetchInsights}
                className="mt-4 px-4 py-2 bg-blue-600 dark:bg-blue-700 text-white rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 transition-colors"
              >
                Try Again
              </button>
            </div>
          ) : !insights ? (
            <div className="text-center py-8">
              <Brain className="w-12 h-12 text-blue-600 dark:text-yellow-400 mx-auto mb-4 opacity-50" />
              <p className="text-blue-800 dark:text-yellow-300">
                Select a conversation to view insights
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Overview Section */}
              <div className="bg-gray-200 dark:bg-slate-900 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-blue-900 dark:text-yellow-100 mb-3 flex items-center">
                  <BarChart3 className="w-5 h-5 mr-2" />
                  Overview
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-700 dark:text-yellow-300">
                      {insights.total_messages}
                    </div>
                    <div className="text-sm text-blue-600 dark:text-yellow-400">
                      Messages
                    </div>
                  </div>
                  <div className="text-center">
                    <div
                      className={`text-2xl font-bold ${
                        getEngagementLevel(insights.engagement_score).color
                      }`}
                    >
                      {getEngagementLevel(insights.engagement_score).label}
                    </div>
                    <div className="text-sm text-blue-600 dark:text-yellow-400">
                      Engagement
                    </div>
                  </div>
                  <div className="text-center">
                    <div
                      className={`text-2xl font-bold ${getSentimentColor(
                        insights.sentiment_trend
                      )}`}
                    >
                      {insights.sentiment_trend.charAt(0).toUpperCase() +
                        insights.sentiment_trend.slice(1)}
                    </div>
                    <div className="text-sm text-blue-600 dark:text-yellow-400">
                      Sentiment
                    </div>
                  </div>
                  <div className="text-center">
                    <div
                      className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getComplexityColor(
                        insights.complexity_level
                      )}`}
                    >
                      {insights.complexity_level.charAt(0).toUpperCase() +
                        insights.complexity_level.slice(1)}
                    </div>
                    <div className="text-sm text-blue-600 dark:text-yellow-400 mt-1">
                      Complexity
                    </div>
                  </div>
                </div>
              </div>

              {/* Key Themes */}
              {insights.key_themes.length > 0 && (
                <div className="bg-gray-200 dark:bg-slate-900 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-blue-900 dark:text-yellow-100 mb-3 flex items-center">
                    <Target className="w-5 h-5 mr-2" />
                    Key Themes
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {insights.key_themes.map((theme, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 rounded-full text-sm"
                      >
                        {theme}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Insights Summary */}
              <div className="bg-gray-200 dark:bg-slate-900 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-blue-900 dark:text-yellow-100 mb-3 flex items-center">
                  <TrendingUp className="w-5 h-5 mr-2" />
                  Summary
                </h3>
                <p className="text-blue-800 dark:text-yellow-200 leading-relaxed">
                  {insights.insights_summary}
                </p>
                {insights.estimated_completion && (
                  <div className="mt-3 flex items-center text-sm text-blue-700 dark:text-yellow-300">
                    <Clock className="w-4 h-4 mr-1" />
                    <span>
                      Estimated completion: {insights.estimated_completion}
                    </span>
                  </div>
                )}
              </div>

              {/* Suggested Next Steps */}
              {insights.suggested_next_steps.length > 0 && (
                <div className="bg-gray-200 dark:bg-slate-900 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-blue-900 dark:text-yellow-100 mb-3 flex items-center">
                    <ArrowRight className="w-5 h-5 mr-2" />
                    Suggested Next Steps
                  </h3>
                  <ul className="space-y-2">
                    {insights.suggested_next_steps.map((step, index) => (
                      <li key={index} className="flex items-start">
                        <div className="w-6 h-6 bg-blue-600 dark:bg-blue-700 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3 mt-0.5 flex-shrink-0">
                          {index + 1}
                        </div>
                        <span className="text-blue-800 dark:text-yellow-200">
                          {step}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Follow-up Questions */}
              {insights.follow_up_questions.length > 0 && (
                <div className="bg-gray-200 dark:bg-slate-900 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-blue-900 dark:text-yellow-100 mb-3 flex items-center">
                    <Lightbulb className="w-5 h-5 mr-2" />
                    Suggested Follow-up Questions
                  </h3>
                  <div className="space-y-2">
                    {insights.follow_up_questions.map((question, index) => (
                      <button
                        key={index}
                        onClick={() => {
                          onQuestionSelect(question);
                          onClose();
                        }}
                        className="w-full text-left p-3 bg-gray-300 dark:bg-slate-800 hover:bg-gray-400 dark:hover:bg-slate-700 rounded-lg transition-colors group"
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-blue-800 dark:text-yellow-200 flex-1 mr-2">
                            {question}
                          </span>
                          <MessageCircle className="w-4 h-4 text-blue-600 dark:text-yellow-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Generated timestamp */}
              <div className="text-center text-sm text-blue-600 dark:text-yellow-400">
                Insights generated{" "}
                {new Date(insights.generated_at).toLocaleString()}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
