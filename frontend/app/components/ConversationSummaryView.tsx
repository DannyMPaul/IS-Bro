"use client";

import React, { useState, useEffect } from "react";
import {
  ConversationSummary,
  KeyPoint,
  SummaryService,
  SummaryRequest,
} from "../services/summaryService";
import { SummaryType } from "../types/summary";

interface ConversationSummaryProps {
  conversationId: string;
  onSummaryGenerated?: (summary: ConversationSummary) => void;
}

const summaryService = new SummaryService();

export const ConversationSummaryView: React.FC<ConversationSummaryProps> = ({
  conversationId,
  onSummaryGenerated,
}) => {
  const [summaries, setSummaries] = useState<ConversationSummary[]>([]);
  const [selectedSummary, setSelectedSummary] =
    useState<ConversationSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSummaries();
  }, [conversationId]);

  const loadSummaries = async () => {
    try {
      const conversationSummaries =
        await summaryService.getConversationSummaries(conversationId);
      setSummaries(conversationSummaries);
      if (conversationSummaries.length > 0) {
        setSelectedSummary(conversationSummaries[0]);
      }
    } catch (error) {
      setError("Failed to load summaries");
    }
  };

  const generateNewSummary = async (type: SummaryType) => {
    setLoading(true);
    setError(null);
    try {
      const request: SummaryRequest = {
        conversation_id: conversationId,
        summary_type: type,
        include_sentiment: true,
        include_key_points: true,
      };
      const newSummary = await summaryService.generateSummary(request);
      setSummaries((prev) => [newSummary, ...prev]);
      setSelectedSummary(newSummary);
      if (onSummaryGenerated) {
        onSummaryGenerated(newSummary);
      }
    } catch (error) {
      setError("Failed to generate summary");
    } finally {
      setLoading(false);
    }
  };

  const renderKeyPoints = (keyPoints: KeyPoint[]) => (
    <div className="mt-4">
      <h4 className="text-lg font-semibold mb-2">Key Points</h4>
      <div className="space-y-2">
        {keyPoints.map((point, index) => (
          <div key={index} className="p-3 bg-gray-50 rounded-lg">
            <h5 className="font-medium text-gray-900">{point.title}</h5>
            <p className="text-gray-600 mt-1">{point.description}</p>
            {point.category && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 mt-2">
                {point.category}
              </span>
            )}
            <div className="mt-2 text-sm text-gray-500">
              Importance: {(point.importance * 100).toFixed(0)}%
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-bold">Conversation Summary</h3>
        <div className="flex space-x-2">
          {Object.values(SummaryType).map((type) => (
            <button
              key={type}
              onClick={() => generateNewSummary(type)}
              disabled={loading}
              className="px-3 py-1 text-sm rounded-md bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {type.replace("_", " ")}
            </button>
          ))}
        </div>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      )}

      {error && (
        <div className="p-3 bg-red-100 text-red-700 rounded-md">{error}</div>
      )}

      {selectedSummary && (
        <div className="bg-white shadow rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <div>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100">
                {selectedSummary.summary_type.replace("_", " ")}
              </span>
              <span className="ml-2 text-sm text-gray-500">
                {new Date(selectedSummary.created_at).toLocaleString()}
              </span>
            </div>
            <div className="text-sm">
              Completion:{" "}
              {(selectedSummary.completion_percentage * 100).toFixed(0)}%
            </div>
          </div>

          <div className="prose max-w-none">{selectedSummary.content}</div>

          {selectedSummary.key_points &&
            renderKeyPoints(selectedSummary.key_points)}

          {selectedSummary.sentiment_score !== undefined && (
            <div className="mt-4 flex items-center">
              <span className="text-sm font-medium text-gray-700">
                Sentiment:
              </span>
              <div className="ml-2 flex items-center">
                {selectedSummary.sentiment_score > 0 ? (
                  <span className="text-green-600">
                    Positive (
                    {(selectedSummary.sentiment_score * 100).toFixed(0)}%)
                  </span>
                ) : selectedSummary.sentiment_score < 0 ? (
                  <span className="text-red-600">
                    Negative (
                    {(Math.abs(selectedSummary.sentiment_score) * 100).toFixed(
                      0
                    )}
                    %)
                  </span>
                ) : (
                  <span className="text-gray-600">Neutral</span>
                )}
              </div>
            </div>
          )}

          {(selectedSummary.categories.length > 0 ||
            selectedSummary.tags.length > 0) && (
            <div className="mt-4 flex flex-wrap gap-2">
              {selectedSummary.categories.map((category) => (
                <span
                  key={category}
                  className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800"
                >
                  {category}
                </span>
              ))}
              {selectedSummary.tags.map((tag) => (
                <span
                  key={tag}
                  className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
                >
                  #{tag}
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      {summaries.length > 1 && (
        <div className="mt-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">
            Previous Summaries
          </h4>
          <div className="space-y-2">
            {summaries.slice(1).map((summary) => (
              <button
                key={summary.summary_id}
                onClick={() => setSelectedSummary(summary)}
                className="w-full text-left p-3 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-900">
                    {summary.summary_type.replace("_", " ")}
                  </span>
                  <span className="text-sm text-gray-500">
                    {new Date(summary.created_at).toLocaleString()}
                  </span>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
