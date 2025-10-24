"use client";

import React from "react";
import {
  HelpCircle,
  Sparkles,
  Keyboard,
  FileText,
  Search,
  BarChart3,
  Download,
  Users,
} from "lucide-react";

interface GettingStartedModalProps {
  isOpen: boolean;
  onClose: () => void;
  onDontShowAgain?: () => void;
}

export const GettingStartedModal: React.FC<GettingStartedModalProps> = ({
  isOpen,
  onClose,
  onDontShowAgain,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="w-full max-w-2xl bg-gray-100 dark:bg-slate-950 border border-gray-300 dark:border-slate-700 rounded-2xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 dark:border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <HelpCircle className="w-5 h-5 text-blue-600 dark:text-yellow-400" />
            <h3 className="text-lg font-bold text-blue-900 dark:text-yellow-400">
              Getting Started
            </h3>
          </div>
          <button
            onClick={onClose}
            className="text-blue-700 dark:text-yellow-300 hover:text-blue-900 dark:hover:text-yellow-100"
            aria-label="Close"
          >
            ✕
          </button>
        </div>

        {/* Body */}
        <div className="px-6 py-5 space-y-6 max-h-[70vh] overflow-y-auto">
          {/* Intro */}
          <div className="flex items-start space-x-3">
            <Sparkles className="w-5 h-5 mt-0.5 text-blue-600 dark:text-yellow-400" />
            <div>
              <p className="text-blue-900 dark:text-yellow-100">
                Welcome to Idea Shaper — your AI partner for turning rough ideas
                into clear, actionable plans.
              </p>
              <p className="text-blue-800 dark:text-yellow-300 mt-2">
                Start by sharing any thought or concept. I’ll ask thoughtful
                questions, suggest directions, and help you shape a concrete
                proposal.
              </p>
            </div>
          </div>

          {/* Quick steps */}
          <div>
            <h4 className="text-sm font-semibold text-blue-700 dark:text-yellow-300 uppercase tracking-wide mb-3">
              Quick Start (3 steps)
            </h4>
            <ol className="list-decimal list-inside space-y-2 text-blue-900 dark:text-yellow-100">
              <li>
                Tell me your idea in a sentence or two — even if it’s vague.
              </li>
              <li>
                Answer my follow-up questions to refine goals, users, and
                constraints.
              </li>
              <li>
                Ask for a proposal or next actions when you’re ready to move
                forward.
              </li>
            </ol>
          </div>

          {/* Features */}
          <div>
            <h4 className="text-sm font-semibold text-blue-700 dark:text-yellow-300 uppercase tracking-wide mb-3">
              Key tools you can use
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div className="flex items-start space-x-3 p-3 rounded-xl bg-gray-200 dark:bg-slate-900 border border-gray-300 dark:border-slate-700">
                <FileText className="w-5 h-5 text-blue-600 dark:text-yellow-400 mt-0.5" />
                <div>
                  <div className="font-medium text-blue-900 dark:text-yellow-100">
                    Conversation Templates
                  </div>
                  <div className="text-sm text-blue-800 dark:text-yellow-300">
                    Jumpstart with curated prompts for product, research, or
                    planning.
                  </div>
                </div>
              </div>
              <div className="flex items-start space-x-3 p-3 rounded-xl bg-gray-200 dark:bg-slate-900 border border-gray-300 dark:border-slate-700">
                <Search className="w-5 h-5 text-blue-600 dark:text-yellow-400 mt-0.5" />
                <div>
                  <div className="font-medium text-blue-900 dark:text-yellow-100">
                    Search Conversations
                  </div>
                  <div className="text-sm text-blue-800 dark:text-yellow-300">
                    Find past ideas and threads instantly by keyword.
                  </div>
                </div>
              </div>
              <div className="flex items-start space-x-3 p-3 rounded-xl bg-gray-200 dark:bg-slate-900 border border-gray-300 dark:border-slate-700">
                <BarChart3 className="w-5 h-5 text-blue-600 dark:text-yellow-400 mt-0.5" />
                <div>
                  <div className="font-medium text-blue-900 dark:text-yellow-100">
                    Conversation Insights
                  </div>
                  <div className="text-sm text-blue-800 dark:text-yellow-300">
                    Get guided questions and next steps tailored to your
                    session.
                  </div>
                </div>
              </div>
              <div className="flex items-start space-x-3 p-3 rounded-xl bg-gray-200 dark:bg-slate-900 border border-gray-300 dark:border-slate-700">
                <Download className="w-5 h-5 text-blue-600 dark:text-yellow-400 mt-0.5" />
                <div>
                  <div className="font-medium text-blue-900 dark:text-yellow-100">
                    Export
                  </div>
                  <div className="text-sm text-blue-800 dark:text-yellow-300">
                    Save your conversation as JSON or Markdown for sharing.
                  </div>
                </div>
              </div>
              <div className="flex items-start space-x-3 p-3 rounded-xl bg-gray-200 dark:bg-slate-900 border border-gray-300 dark:border-slate-700">
                <Users className="w-5 h-5 text-blue-600 dark:text-yellow-400 mt-0.5" />
                <div>
                  <div className="font-medium text-blue-900 dark:text-yellow-100">
                    Multi‑AI Mode
                  </div>
                  <div className="text-sm text-blue-800 dark:text-yellow-300">
                    Compare perspectives from multiple AI providers when needed.
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Keyboard shortcuts */}
          <div>
            <h4 className="text-sm font-semibold text-blue-700 dark:text-yellow-300 uppercase tracking-wide mb-3 flex items-center">
              <Keyboard className="w-4 h-4 mr-2" /> Keyboard Shortcuts
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
              <div className="flex items-center justify-between px-3 py-2 rounded-lg bg-gray-200 dark:bg-slate-900 border border-gray-300 dark:border-slate-700 text-blue-900 dark:text-yellow-100">
                <span>Send message</span>
                <kbd className="px-2 py-1 bg-gray-300 dark:bg-slate-800 rounded">
                  Enter
                </kbd>
              </div>
              <div className="flex items-center justify-between px-3 py-2 rounded-lg bg-gray-200 dark:bg-slate-900 border border-gray-300 dark:border-slate-700 text-blue-900 dark:text-yellow-100">
                <span>New conversation</span>
                <kbd className="px-2 py-1 bg-gray-300 dark:bg-slate-800 rounded">
                  Alt + N
                </kbd>
              </div>
              <div className="flex items-center justify-between px-3 py-2 rounded-lg bg-gray-200 dark:bg-slate-900 border border-gray-300 dark:border-slate-700 text-blue-900 dark:text-yellow-100">
                <span>Focus input</span>
                <kbd className="px-2 py-1 bg-gray-300 dark:bg-slate-800 rounded">
                  Alt + K
                </kbd>
              </div>
              <div className="flex items-center justify-between px-3 py-2 rounded-lg bg-gray-200 dark:bg-slate-900 border border-gray-300 dark:border-slate-700 text-blue-900 dark:text-yellow-100">
                <span>Templates</span>
                <kbd className="px-2 py-1 bg-gray-300 dark:bg-slate-800 rounded">
                  Alt + T
                </kbd>
              </div>
              <div className="flex items-center justify-between px-3 py-2 rounded-lg bg-gray-200 dark:bg-slate-900 border border-gray-300 dark:border-slate-700 text-blue-900 dark:text-yellow-100">
                <span>Search</span>
                <kbd className="px-2 py-1 bg-gray-300 dark:bg-slate-800 rounded">
                  Alt + F
                </kbd>
              </div>
              <div className="flex items-center justify-between px-3 py-2 rounded-lg bg-gray-200 dark:bg-slate-900 border border-gray-300 dark:border-slate-700 text-blue-900 dark:text-yellow-100">
                <span>Insights</span>
                <kbd className="px-2 py-1 bg-gray-300 dark:bg-slate-800 rounded">
                  Alt + I
                </kbd>
              </div>
              <div className="flex items-center justify-between px-3 py-2 rounded-lg bg-gray-200 dark:bg-slate-900 border border-gray-300 dark:border-slate-700 text-blue-900 dark:text-yellow-100">
                <span>Show shortcuts</span>
                <kbd className="px-2 py-1 bg-gray-300 dark:bg-slate-800 rounded">
                  Alt + /
                </kbd>
              </div>
              <div className="flex items-center justify-between px-3 py-2 rounded-lg bg-gray-200 dark:bg-slate-900 border border-gray-300 dark:border-slate-700 text-blue-900 dark:text-yellow-100">
                <span>Close modal</span>
                <kbd className="px-2 py-1 bg-gray-300 dark:bg-slate-800 rounded">
                  Esc
                </kbd>
              </div>
            </div>
          </div>

          {/* Sample prompts */}
          <div>
            <h4 className="text-sm font-semibold text-blue-700 dark:text-yellow-300 uppercase tracking-wide mb-3">
              Try these prompts
            </h4>
            <ul className="list-disc list-inside space-y-1 text-blue-900 dark:text-yellow-100">
              <li>
                "I have a vague idea for an app that helps students manage time
                — where should I start?"
              </li>
              <li>
                "Help me compare two directions: a Chrome extension vs a mobile
                app for note-taking."
              </li>
              <li>
                "Turn our chat so far into a one-page proposal with next steps."
              </li>
            </ul>
          </div>

          {/* Privacy note */}
          <div className="text-xs text-blue-700 dark:text-yellow-300">
            Tip: You can access this guide anytime from the Menu under Help.
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 dark:border-slate-800 flex items-center justify-between">
          <button
            onClick={onDontShowAgain}
            className="text-sm text-blue-700 dark:text-yellow-300 hover:underline"
          >
            Don’t show again
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium shadow"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
