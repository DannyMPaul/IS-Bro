"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  Search,
  Filter,
  Calendar,
  MessageSquare,
  Clock,
  X,
  ArrowRight,
} from "lucide-react";
import { formatRelativeTime } from "../lib/utils";

interface SearchResult {
  id: string;
  title: string;
  stage: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  relevance_score: number;
  matching_snippet: string;
}

interface SearchResponse {
  results: SearchResult[];
  total_count: number;
  query: string;
  filters_applied: Record<string, any>;
}

interface SearchFilters {
  stage?: string;
  date_from?: string;
  date_to?: string;
}

interface ConversationSearchProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectConversation: (conversationId: string) => void;
}

export const ConversationSearch: React.FC<ConversationSearchProps> = ({
  isOpen,
  onClose,
  onSelectConversation,
}) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<SearchFilters>({});
  const [filterOptions, setFilterOptions] = useState<{
    stages: string[];
    date_ranges: Array<{ label: string; value: string }>;
  }>({ stages: [], date_ranges: [] });
  const [totalCount, setTotalCount] = useState(0);
  const searchInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      fetchFilterOptions();
      searchInputRef.current?.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    if (searchQuery.trim().length >= 2) {
      const timeoutId = setTimeout(() => {
        performSearch();
      }, 300); // Debounce search
      return () => clearTimeout(timeoutId);
    } else {
      setSearchResults([]);
      setTotalCount(0);
    }
  }, [searchQuery, filters]);

  const fetchFilterOptions = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/search/filters");
      const data = await response.json();
      setFilterOptions(data);
    } catch (error) {
      console.error("Failed to fetch filter options:", error);
    }
  };

  const performSearch = async () => {
    if (!searchQuery.trim()) return;

    setIsLoading(true);
    try {
      const searchRequest = {
        query: searchQuery,
        filters: filters,
        limit: 20,
      };

      const response = await fetch(
        "http://localhost:8000/api/search/conversations",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(searchRequest),
        }
      );

      const data: SearchResponse = await response.json();
      setSearchResults(data.results);
      setTotalCount(data.total_count);
    } catch (error) {
      console.error("Search failed:", error);
      setSearchResults([]);
      setTotalCount(0);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFilterChange = (key: string, value: string) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value || undefined,
    }));
  };

  const clearFilters = () => {
    setFilters({});
  };

  const getStageColor = (stage: string) => {
    const colors = {
      initial: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300",
      exploring:
        "bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300",
      structuring:
        "bg-purple-100 text-purple-700 dark:bg-purple-900/20 dark:text-purple-300",
      alternatives:
        "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-300",
      refinement:
        "bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-300",
      proposal:
        "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/20 dark:text-indigo-300",
    };
    return colors[stage as keyof typeof colors] || colors.initial;
  };

  const highlightMatch = (text: string, query: string) => {
    if (!query.trim()) return text;

    const regex = new RegExp(
      `(${query.replace(/[.*+?^${}()|[\\]\\\\]/g, "\\$&")})`,
      "gi"
    );
    return text.replace(
      regex,
      '<mark class="bg-yellow-200 dark:bg-yellow-800 px-1 rounded">$1</mark>'
    );
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-100 dark:bg-slate-950 border border-gray-300 dark:border-slate-700 rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden">
        <div className="p-6 border-b border-gray-300 dark:border-slate-700">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-blue-900 dark:text-yellow-400 flex items-center">
              <Search className="w-6 h-6 mr-2" />
              Search Conversations
            </h2>
            <button
              onClick={onClose}
              className="text-blue-700 dark:text-yellow-300 hover:text-blue-900 dark:hover:text-yellow-100 p-2"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Search Input */}
          <div className="relative mb-4">
            <Search className="w-5 h-5 text-blue-600 dark:text-yellow-400 absolute left-3 top-3" />
            <input
              ref={searchInputRef}
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search your conversations..."
              className="w-full pl-10 pr-4 py-3 border border-gray-400 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-50 dark:bg-slate-900 text-blue-900 dark:text-yellow-100"
            />
          </div>

          {/* Filters */}
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                showFilters
                  ? "bg-blue-200 dark:bg-blue-800 text-blue-900 dark:text-yellow-100"
                  : "bg-gray-200 dark:bg-slate-800 text-blue-800 dark:text-yellow-300 hover:bg-gray-300 dark:hover:bg-slate-700"
              }`}
            >
              <Filter className="w-4 h-4" />
              <span>Filters</span>
            </button>

            {Object.keys(filters).length > 0 && (
              <button
                onClick={clearFilters}
                className="text-sm text-blue-600 dark:text-yellow-400 hover:text-blue-800 dark:hover:text-yellow-200"
              >
                Clear filters
              </button>
            )}

            {totalCount > 0 && (
              <span className="text-sm text-blue-700 dark:text-yellow-300">
                {totalCount} result{totalCount !== 1 ? "s" : ""} found
              </span>
            )}
          </div>

          {/* Filter Controls */}
          {showFilters && (
            <div className="mt-4 p-4 bg-gray-200 dark:bg-slate-900 rounded-lg space-y-3">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-blue-800 dark:text-yellow-300 mb-1">
                    Stage
                  </label>
                  <select
                    value={filters.stage || ""}
                    onChange={(e) =>
                      handleFilterChange("stage", e.target.value)
                    }
                    className="w-full px-3 py-2 border border-gray-400 dark:border-slate-600 rounded-lg bg-gray-50 dark:bg-slate-800 text-blue-900 dark:text-yellow-100 text-sm"
                  >
                    <option value="">All stages</option>
                    {filterOptions.stages.map((stage) => (
                      <option key={stage} value={stage}>
                        {stage.charAt(0).toUpperCase() + stage.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-blue-800 dark:text-yellow-300 mb-1">
                    From Date
                  </label>
                  <input
                    type="date"
                    value={filters.date_from || ""}
                    onChange={(e) =>
                      handleFilterChange("date_from", e.target.value)
                    }
                    className="w-full px-3 py-2 border border-gray-400 dark:border-slate-600 rounded-lg bg-gray-50 dark:bg-slate-800 text-blue-900 dark:text-yellow-100 text-sm"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-blue-800 dark:text-yellow-300 mb-1">
                    To Date
                  </label>
                  <input
                    type="date"
                    value={filters.date_to || ""}
                    onChange={(e) =>
                      handleFilterChange("date_to", e.target.value)
                    }
                    className="w-full px-3 py-2 border border-gray-400 dark:border-slate-600 rounded-lg bg-gray-50 dark:bg-slate-800 text-blue-900 dark:text-yellow-100 text-sm"
                  />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Search Results */}
        <div className="p-6 overflow-y-auto max-h-[60vh]">
          {isLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full mx-auto mb-4"></div>
              <p className="text-blue-800 dark:text-yellow-300">Searching...</p>
            </div>
          ) : searchQuery.trim().length < 2 ? (
            <div className="text-center py-8">
              <Search className="w-12 h-12 text-blue-600 dark:text-yellow-400 mx-auto mb-4 opacity-50" />
              <p className="text-blue-800 dark:text-yellow-300">
                Enter at least 2 characters to search
              </p>
            </div>
          ) : searchResults.length === 0 ? (
            <div className="text-center py-8">
              <MessageSquare className="w-12 h-12 text-blue-600 dark:text-yellow-400 mx-auto mb-4 opacity-50" />
              <p className="text-blue-800 dark:text-yellow-300">
                No conversations found matching your search
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {searchResults.map((result) => (
                <div
                  key={result.id}
                  className="bg-gray-200 dark:bg-slate-900 border border-gray-300 dark:border-slate-700 rounded-lg p-4 hover:bg-gray-300 dark:hover:bg-slate-800 cursor-pointer transition-all duration-200 hover:shadow-md group"
                  onClick={() => {
                    onSelectConversation(result.id);
                    onClose();
                  }}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-semibold text-blue-900 dark:text-yellow-100 flex-1 mr-4">
                      {result.title}
                    </h3>
                    <ArrowRight className="w-4 h-4 text-blue-600 dark:text-yellow-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>

                  <div
                    className="text-blue-800 dark:text-yellow-200 text-sm mb-3 line-clamp-2"
                    dangerouslySetInnerHTML={{
                      __html: highlightMatch(
                        result.matching_snippet,
                        searchQuery
                      ),
                    }}
                  />

                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${getStageColor(
                          result.stage
                        )}`}
                      >
                        {result.stage}
                      </span>
                      <div className="flex items-center space-x-1 text-xs text-blue-700 dark:text-yellow-300">
                        <MessageSquare className="w-3 h-3" />
                        <span>{result.message_count} messages</span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-1 text-xs text-blue-700 dark:text-yellow-300">
                      <Clock className="w-3 h-3" />
                      <span>{formatRelativeTime(result.updated_at)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
