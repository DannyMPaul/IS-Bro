"use client";

import React, { useState, useEffect } from "react";
import {
  Search,
  Filter,
  BookOpen,
  Clock,
  Users,
  Tag,
  Lightbulb,
  X,
} from "lucide-react";

interface Template {
  id: string;
  title: string;
  category: string;
  description: string;
  initial_prompt: string;
  suggested_questions: string[];
  target_audience: string;
  estimated_duration: string;
  difficulty_level: string;
  tags: string[];
}

interface TemplateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectTemplate: (template: Template) => void;
}

export const TemplateModal: React.FC<TemplateModalProps> = ({
  isOpen,
  onClose,
  onSelectTemplate,
}) => {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [filteredTemplates, setFilteredTemplates] = useState<Template[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [categories, setCategories] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchTemplates();
      fetchCategories();
    }
  }, [isOpen]);

  useEffect(() => {
    filterTemplates();
  }, [templates, searchQuery, selectedCategory]);

  const fetchTemplates = async () => {
    setIsLoading(true);
    try {
      const response = await fetch("http://localhost:8000/api/templates");
      const data = await response.json();
      setTemplates(data);
    } catch (error) {
      console.error("Failed to fetch templates:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await fetch(
        "http://localhost:8000/api/templates/categories"
      );
      const data = await response.json();
      setCategories(data.categories);
    } catch (error) {
      console.error("Failed to fetch categories:", error);
    }
  };

  const filterTemplates = () => {
    let filtered = templates;

    if (searchQuery) {
      filtered = filtered.filter(
        (template) =>
          template.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          template.description
            .toLowerCase()
            .includes(searchQuery.toLowerCase()) ||
          template.tags.some((tag) =>
            tag.toLowerCase().includes(searchQuery.toLowerCase())
          )
      );
    }

    if (selectedCategory !== "all") {
      filtered = filtered.filter(
        (template) => template.category === selectedCategory
      );
    }

    setFilteredTemplates(filtered);
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case "low":
        return "text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900/20";
      case "medium":
        return "text-yellow-600 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900/20";
      case "high":
        return "text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/20";
      default:
        return "text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-900/20";
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case "technology":
        return "💻";
      case "business":
        return "💼";
      case "healthcare":
        return "🏥";
      case "education":
        return "📚";
      case "sustainability":
        return "🌱";
      case "entertainment":
        return "🎭";
      case "productivity":
        return "⚡";
      default:
        return "💡";
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-100 dark:bg-slate-950 border border-gray-300 dark:border-slate-700 rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden">
        <div className="p-6 border-b border-gray-300 dark:border-slate-700">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-blue-900 dark:text-yellow-400 flex items-center">
              <BookOpen className="w-6 h-6 mr-2" />
              Choose a Conversation Template
            </h2>
            <button
              onClick={onClose}
              className="text-blue-700 dark:text-yellow-300 hover:text-blue-900 dark:hover:text-yellow-100 p-2"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Search and Filter */}
          <div className="flex space-x-4 mb-4">
            <div className="flex-1 relative">
              <Search className="w-5 h-5 text-blue-600 dark:text-yellow-400 absolute left-3 top-3" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search templates..."
                className="w-full pl-10 pr-4 py-3 border border-gray-400 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-50 dark:bg-slate-900 text-blue-900 dark:text-yellow-100"
              />
            </div>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-4 py-3 border border-gray-400 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-50 dark:bg-slate-900 text-blue-900 dark:text-yellow-100"
            >
              <option value="all">All Categories</option>
              {categories.map((category) => (
                <option key={category} value={category}>
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Templates Grid */}
        <div className="p-6 overflow-y-auto max-h-[60vh]">
          {isLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full mx-auto mb-4"></div>
              <p className="text-blue-800 dark:text-yellow-300">
                Loading templates...
              </p>
            </div>
          ) : filteredTemplates.length === 0 ? (
            <div className="text-center py-8">
              <Lightbulb className="w-12 h-12 text-blue-600 dark:text-yellow-400 mx-auto mb-4" />
              <p className="text-blue-800 dark:text-yellow-300">
                No templates found matching your criteria.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredTemplates.map((template) => (
                <div
                  key={template.id}
                  className="bg-gray-200 dark:bg-slate-900 border border-gray-300 dark:border-slate-700 rounded-lg p-4 hover:bg-gray-300 dark:hover:bg-slate-800 cursor-pointer transition-all duration-200 hover:shadow-md"
                  onClick={() => onSelectTemplate(template)}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      <span className="text-2xl">
                        {getCategoryIcon(template.category)}
                      </span>
                      <h3 className="font-semibold text-blue-900 dark:text-yellow-100">
                        {template.title}
                      </h3>
                    </div>
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(
                        template.difficulty_level
                      )}`}
                    >
                      {template.difficulty_level}
                    </span>
                  </div>

                  <p className="text-blue-800 dark:text-yellow-200 text-sm mb-3 line-clamp-2">
                    {template.description}
                  </p>

                  <div className="flex items-center justify-between text-xs text-blue-700 dark:text-yellow-300 mb-3">
                    <div className="flex items-center space-x-1">
                      <Users className="w-3 h-3" />
                      <span>{template.target_audience}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Clock className="w-3 h-3" />
                      <span>{template.estimated_duration}</span>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-1">
                    {template.tags.slice(0, 3).map((tag, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 text-xs rounded-full"
                      >
                        #{tag}
                      </span>
                    ))}
                    {template.tags.length > 3 && (
                      <span className="px-2 py-1 bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 text-xs rounded-full">
                        +{template.tags.length - 3} more
                      </span>
                    )}
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
