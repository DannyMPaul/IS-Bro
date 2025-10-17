"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  Send,
  Brain,
  Lightbulb,
  MessageSquare,
  User,
  LogOut,
  LogIn,
  Sparkles,
  Bot,
  Settings,
  Users,
  Moon,
  Sun,
  Download,
  Upload,
  Keyboard,
  HelpCircle,
  Search,
  FileText,
  BarChart3,
} from "lucide-react";
import ChatList from "./components/ChatList";
import { useAuth } from "../contexts/AuthContext";
import { AuthModal } from "../components/AuthModal";
import { TemplateModal } from "../components/TemplateModal";
import { ConversationSearch } from "../components/ConversationSearch";
import { ConversationInsights } from "../components/ConversationInsights";
import { NavigationMenu } from "../components/NavigationMenu";
import { formatChatTimestamp, cn } from "../lib/utils";
import { MarkdownRenderer } from "../lib/markdown";

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

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  suggestions?: string[];
  persona?: string;
  provider?: string;
}

interface ChatResponse {
  response: string;
  session_id: string;
  conversation_state: string;
  suggestions?: string[];
  user_message_timestamp: string;
  assistant_message_timestamp: string;
}

interface MultiPerspectiveResponse {
  perspectives: Array<{
    message: string;
    persona: string;
    provider: string;
    suggestions?: string[];
  }>;
  session_id: string;
  conversation_state: string;
  user_message_timestamp: string;
  assistant_message_timestamps: string[];
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>("");
  const [conversationState, setConversationState] = useState("initial");
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showTemplateModal, setShowTemplateModal] = useState(false);
  const [showSearchModal, setShowSearchModal] = useState(false);
  const [showInsightsModal, setShowInsightsModal] = useState(false);
  const [multiPerspectiveMode, setMultiPerspectiveMode] = useState(false);
  const [theme, setTheme] = useState<"light" | "dark">("light");
  const [showShortcuts, setShowShortcuts] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const { user, logout, token } = useAuth();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Theme initialization
  useEffect(() => {
    const savedTheme = localStorage.getItem("theme") as "light" | "dark" | null;
    const prefersDark = window.matchMedia(
      "(prefers-color-scheme: dark)"
    ).matches;
    const initialTheme = savedTheme || (prefersDark ? "dark" : "light");
    setTheme(initialTheme);
    // Theme class is already applied by the script in layout.tsx
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Ctrl+Enter to send message
      if (event.ctrlKey && event.key === "Enter" && !isLoading) {
        event.preventDefault();
        sendMessage();
      }

      // Ctrl+N for new chat
      if (event.ctrlKey && event.key === "n") {
        event.preventDefault();
        startNewChat();
      }

      // Ctrl+/ to show shortcuts help
      if (event.ctrlKey && event.key === "/") {
        event.preventDefault();
        setShowShortcuts(!showShortcuts);
      }

      // Ctrl+T for templates
      if (event.ctrlKey && event.key === "t") {
        event.preventDefault();
        setShowTemplateModal(!showTemplateModal);
      }

      // Ctrl+F for search
      if (event.ctrlKey && event.key === "f") {
        event.preventDefault();
        setShowSearchModal(!showSearchModal);
      }

      // Ctrl+I for insights
      if (event.ctrlKey && event.key === "i") {
        event.preventDefault();
        if (sessionId) {
          setShowInsightsModal(!showInsightsModal);
        }
      }

      // Escape to close shortcuts or focus input
      if (event.key === "Escape") {
        if (showShortcuts) {
          setShowShortcuts(false);
        } else if (showTemplateModal) {
          setShowTemplateModal(false);
        } else if (showSearchModal) {
          setShowSearchModal(false);
        } else if (showInsightsModal) {
          setShowInsightsModal(false);
        } else {
          inputRef.current?.focus();
        }
      }

      // Ctrl+K to focus input
      if (event.ctrlKey && event.key === "k") {
        event.preventDefault();
        inputRef.current?.focus();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [
    isLoading,
    showShortcuts,
    showTemplateModal,
    showSearchModal,
    showInsightsModal,
    sessionId,
  ]);

  const toggleTheme = () => {
    const newTheme = theme === "light" ? "dark" : "light";
    setTheme(newTheme);
    document.documentElement.classList.toggle("dark", newTheme === "dark");
    localStorage.setItem("theme", newTheme);
  };

  const exportConversation = (format: "json" | "markdown") => {
    if (!sessionId || messages.length === 0) return;

    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, "-");
    const filename = `conversation-${sessionId}-${timestamp}`;

    if (format === "json") {
      const exportData = {
        id: sessionId,
        stage: conversationState,
        exported_at: new Date().toISOString(),
        messages: messages.map((msg) => ({
          role: msg.role,
          content: msg.content,
          timestamp: msg.timestamp,
          persona: msg.persona,
          provider: msg.provider,
          suggestions: msg.suggestions,
        })),
      };

      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${filename}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } else if (format === "markdown") {
      let markdown = `# Idea Shaper Conversation\n\n`;
      markdown += `**Session ID:** ${sessionId}\n`;
      markdown += `**Stage:** ${conversationState}\n`;
      markdown += `**Exported:** ${new Date().toLocaleString()}\n`;
      markdown += `**Messages:** ${messages.length}\n\n---\n\n`;

      messages.forEach((msg, index) => {
        const role = msg.role === "user" ? "👤 **You**" : "🤖 **Big Brother**";
        const persona = msg.persona ? ` (${msg.persona})` : "";
        markdown += `## ${role}${persona}\n`;
        markdown += `*${new Date(msg.timestamp).toLocaleString()}*\n\n`;
        markdown += `${msg.content}\n\n`;

        if (msg.suggestions && msg.suggestions.length > 0) {
          markdown += `**Suggestions:**\n`;
          msg.suggestions.forEach((suggestion) => {
            markdown += `- ${suggestion}\n`;
          });
          markdown += `\n`;
        }

        if (index < messages.length - 1) {
          markdown += `---\n\n`;
        }
      });

      const blob = new Blob([markdown], { type: "text/markdown" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${filename}.md`;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  const startNewChat = () => {
    setMessages([]);
    setSessionId("");
    setConversationState("initial");
  };

  const loadConversation = async (conversationId: string) => {
    try {
      const headers: any = {};

      // Add authentication header if user is logged in
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      }

      const response = await fetch(
        `http://localhost:8000/api/conversations/${conversationId}`,
        { headers }
      );
      const data = await response.json();

      const loadedMessages = data.messages.map((msg: any) => ({
        role: msg.role,
        content: msg.content,
        timestamp: msg.timestamp,
        suggestions: msg.suggestions,
      }));

      setMessages(loadedMessages);
      setSessionId(conversationId);
      setConversationState(data.stage);
    } catch (error) {
      console.error("Failed to load conversation:", error);
    }
  };

  const sendMessage = async (messageText?: string) => {
    const messageToSend = messageText || input;
    if (!messageToSend.trim()) return;

    const userMessage: Message = {
      role: "user",
      content: messageToSend,
      timestamp: new Date().toISOString(), // Keep client timestamp for immediate display
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    // Close template modal if open and we're sending from template
    if (showTemplateModal) {
      setShowTemplateModal(false);
    }

    try {
      const headers: any = {
        "Content-Type": "application/json",
      };

      // Add authentication header if user is logged in
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      }

      const endpoint = multiPerspectiveMode
        ? "http://localhost:8000/api/chat/multi-perspective"
        : "http://localhost:8000/api/chat";

      const response = await fetch(endpoint, {
        method: "POST",
        headers,
        body: JSON.stringify({
          message: messageToSend,
          session_id: sessionId || undefined,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to send message");
      }

      const data = await response.json();

      if (!sessionId) {
        setSessionId(data.session_id);
        setRefreshTrigger((prev) => prev + 1); // Trigger chat list refresh
      }

      setConversationState(data.conversation_state);

      if (multiPerspectiveMode && data.perspectives) {
        // Handle multi-perspective response
        const multiData = data as MultiPerspectiveResponse;
        const assistantMessages: Message[] = multiData.perspectives.map(
          (perspective, index) => ({
            role: "assistant" as const,
            content: perspective.message,
            timestamp:
              multiData.assistant_message_timestamps &&
              multiData.assistant_message_timestamps[index]
                ? multiData.assistant_message_timestamps[index]
                : new Date().toISOString(),
            suggestions: perspective.suggestions,
            persona: perspective.persona,
            provider: perspective.provider,
          })
        );

        setMessages((prev) => [...prev, ...assistantMessages]);
      } else {
        // Handle single response
        const singleData = data as ChatResponse;
        const assistantMessage: Message = {
          role: "assistant",
          content: singleData.response,
          timestamp:
            singleData.assistant_message_timestamp || new Date().toISOString(),
          suggestions: singleData.suggestions,
        };

        setMessages((prev) => [...prev, assistantMessage]);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage: Message = {
        role: "assistant",
        content: "Sorry, I encountered an error. Please try again.",
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage();
  };

  const getStageDisplay = (stage: string) => {
    const stages = {
      initial: {
        icon: <MessageSquare className="w-4 h-4" />,
        label: "Getting Started",
      },
      exploring: {
        icon: <Brain className="w-4 h-4" />,
        label: "Exploring Ideas",
      },
      structuring: {
        icon: <Lightbulb className="w-4 h-4" />,
        label: "Structuring",
      },
      alternatives: {
        icon: <Brain className="w-4 h-4" />,
        label: "Alternatives",
      },
      refinement: {
        icon: <Lightbulb className="w-4 h-4" />,
        label: "Refinement",
      },
      proposal: {
        icon: <MessageSquare className="w-4 h-4" />,
        label: "Proposal Ready",
      },
    };
    return stages[stage as keyof typeof stages] || stages.initial;
  };

  return (
    <div className="h-screen flex bg-gray-100 dark:bg-slate-950">
      <ChatList
        currentConversationId={sessionId}
        onSelectConversation={loadConversation}
        onNewChat={startNewChat}
        refreshTrigger={refreshTrigger}
      />

      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
      />

      <TemplateModal
        isOpen={showTemplateModal}
        onClose={() => setShowTemplateModal(false)}
        onSelectTemplate={(template) => {
          setInput(template.initial_prompt);
          inputRef.current?.focus();
        }}
      />

      <ConversationSearch
        isOpen={showSearchModal}
        onClose={() => setShowSearchModal(false)}
        onSelectConversation={loadConversation}
      />

      <ConversationInsights
        conversationId={sessionId}
        isOpen={showInsightsModal}
        onClose={() => setShowInsightsModal(false)}
        onQuestionSelect={(question) => {
          setInput(question);
          inputRef.current?.focus();
        }}
      />

      {/* Keyboard Shortcuts Modal */}
      {showShortcuts && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-100 dark:bg-slate-950 border border-gray-300 dark:border-slate-700 rounded-lg shadow-xl w-full max-w-md">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-blue-900 dark:text-yellow-400 flex items-center">
                  <Keyboard className="w-5 h-5 mr-2" />
                  Keyboard Shortcuts
                </h3>
                <button
                  onClick={() => setShowShortcuts(false)}
                  className="text-blue-700 dark:text-yellow-300 hover:text-blue-900 dark:hover:text-yellow-100"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-blue-800 dark:text-yellow-200">
                    Send message
                  </span>
                  <kbd className="px-2 py-1 bg-gray-300 dark:bg-slate-800 text-xs rounded border">
                    Ctrl + Enter
                  </kbd>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-blue-800 dark:text-yellow-200">
                    New conversation
                  </span>
                  <kbd className="px-2 py-1 bg-gray-300 dark:bg-slate-800 text-xs rounded border">
                    Ctrl + N
                  </kbd>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-blue-800 dark:text-yellow-200">
                    Focus input
                  </span>
                  <kbd className="px-2 py-1 bg-gray-300 dark:bg-slate-800 text-xs rounded border">
                    Ctrl + K
                  </kbd>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-blue-800 dark:text-yellow-200">
                    Templates
                  </span>
                  <kbd className="px-2 py-1 bg-gray-300 dark:bg-slate-800 text-xs rounded border">
                    Ctrl + T
                  </kbd>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-blue-800 dark:text-yellow-200">
                    Search conversations
                  </span>
                  <kbd className="px-2 py-1 bg-gray-300 dark:bg-slate-800 text-xs rounded border">
                    Ctrl + F
                  </kbd>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-blue-800 dark:text-yellow-200">
                    Insights
                  </span>
                  <kbd className="px-2 py-1 bg-gray-300 dark:bg-slate-800 text-xs rounded border">
                    Ctrl + I
                  </kbd>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-blue-800 dark:text-yellow-200">
                    Show shortcuts
                  </span>
                  <kbd className="px-2 py-1 bg-gray-300 dark:bg-slate-800 text-xs rounded border">
                    Ctrl + /
                  </kbd>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-blue-800 dark:text-yellow-200">
                    Close modal
                  </span>
                  <kbd className="px-2 py-1 bg-gray-300 dark:bg-slate-800 text-xs rounded border">
                    Esc
                  </kbd>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="flex-1 flex flex-col min-h-0">
        <header className="flex-shrink-0 bg-gray-200/80 backdrop-blur-md border-b border-gray-300/20 shadow-sm px-6 py-4 dark:bg-slate-900/80 dark:border-slate-700/20">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="relative">
                <Brain className="w-8 h-8 text-blue-600" />
                <Sparkles className="w-4 h-4 text-yellow-500 absolute -top-1 -right-1 animate-pulse" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-blue-900 dark:text-yellow-400">
                  Idea Shaper
                </h1>
                <p className="text-xs text-blue-800 dark:text-yellow-300 font-medium">
                  AI-Powered Innovation Assistant
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {/* Conversation Stage */}
              <div className="flex items-center space-x-2 px-3 py-1.5 bg-gray-300 dark:bg-blue-800 rounded-full text-sm">
                {getStageDisplay(conversationState).icon}
                <span className="font-medium text-blue-900 dark:text-yellow-400">
                  {getStageDisplay(conversationState).label}
                </span>
              </div>

              {/* Multi-Perspective Mode Indicator */}
              {multiPerspectiveMode && (
                <div className="flex items-center space-x-2 px-3 py-1.5 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-full text-sm font-medium shadow-md">
                  <Users className="w-4 h-4" />
                  <span className="hidden sm:inline">Multi-AI Active</span>
                </div>
              )}

              {/* Navigation Menu */}
              <NavigationMenu
                user={user}
                theme={theme}
                multiPerspectiveMode={multiPerspectiveMode}
                sessionId={sessionId}
                hasMessages={messages.length > 0}
                onToggleTheme={toggleTheme}
                onToggleMultiPerspective={() =>
                  setMultiPerspectiveMode(!multiPerspectiveMode)
                }
                onShowTemplates={() => setShowTemplateModal(true)}
                onShowSearch={() => setShowSearchModal(true)}
                onShowInsights={() => setShowInsightsModal(true)}
                onShowShortcuts={() => setShowShortcuts(true)}
                onExport={exportConversation}
                onShowAuth={() => setShowAuthModal(true)}
                onLogout={logout}
              />
            </div>
          </div>
        </header>

        <main className="flex-1 flex flex-col bg-gray-100 dark:bg-slate-950 min-h-0">
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {messages.length === 0 && (
              <div className="text-center py-16">
                <div className="relative mb-8">
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-32 h-32 bg-gradient-to-r from-blue-400/20 to-purple-400/20 rounded-full animate-pulse"></div>
                  </div>
                  <Brain className="w-20 h-20 text-blue-600 mx-auto relative z-10" />
                  <Sparkles className="w-6 h-6 text-yellow-500 absolute top-4 right-1/2 transform translate-x-8 animate-bounce" />
                </div>
                <h2 className="text-3xl font-bold text-blue-900 dark:text-yellow-400 mb-3">
                  Hey there! I'm Big Brother.
                </h2>
                <p className="text-blue-800 dark:text-yellow-300 max-w-lg mx-auto text-lg leading-relaxed">
                  I'm here to help you turn that vague idea in your head into
                  something concrete and actionable. Tell me what's on your mind
                  - no matter how rough or incomplete it is.
                </p>
                <div className="mt-8 flex justify-center space-x-4">
                  <div className="px-4 py-2 bg-gray-300 dark:bg-blue-800 rounded-full text-sm font-medium text-blue-900 dark:text-yellow-400">
                    💡 Share your ideas
                  </div>
                  <div className="px-4 py-2 bg-gray-300 dark:bg-blue-800 rounded-full text-sm font-medium text-blue-900 dark:text-yellow-400">
                    🚀 Get structured feedback
                  </div>
                  <div className="px-4 py-2 bg-gray-300 dark:bg-blue-800 rounded-full text-sm font-medium text-blue-900 dark:text-yellow-400">
                    ✨ Build something amazing
                  </div>
                </div>
              </div>
            )}

            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`flex max-w-4xl ${
                    message.role === "user" ? "flex-row-reverse" : "flex-row"
                  } items-start space-x-3`}
                >
                  <div
                    className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                      message.role === "user"
                        ? "bg-gradient-to-r from-blue-500 to-purple-500 ml-3"
                        : "bg-gray-300 dark:bg-blue-800 mr-3"
                    }`}
                  >
                    {message.role === "user" ? (
                      <User className="w-4 h-4 text-white" />
                    ) : (
                      <Bot className="w-4 h-4 text-blue-800 dark:text-yellow-400" />
                    )}
                  </div>

                  <div className="flex-1">
                    <div
                      className={cn(
                        "rounded-2xl px-4 py-3 shadow-sm",
                        message.role === "user"
                          ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-br-md"
                          : "bg-gray-200 dark:bg-slate-900 border border-gray-300 dark:border-slate-700 text-blue-900 dark:text-yellow-100 rounded-bl-md shadow-md"
                      )}
                    >
                      {/* Show persona info for assistant messages */}
                      {message.role === "assistant" && message.persona && (
                        <div className="mb-2 flex items-center space-x-2">
                          <div className="px-2 py-1 bg-gray-300 dark:bg-blue-800 rounded-full">
                            <span className="text-xs font-semibold text-blue-900 dark:text-yellow-400">
                              {message.persona}
                            </span>
                          </div>
                          {message.provider && (
                            <div className="px-2 py-1 bg-gray-300 dark:bg-blue-800 rounded-full">
                              <span className="text-xs text-blue-800 dark:text-yellow-300">
                                {message.provider}
                              </span>
                            </div>
                          )}
                        </div>
                      )}
                      <MarkdownRenderer
                        content={message.content}
                        className="leading-relaxed"
                      />
                    </div>

                    <div
                      className={`mt-1 text-xs text-blue-700 dark:text-yellow-300 ${
                        message.role === "user" ? "text-right" : "text-left"
                      }`}
                    >
                      {formatChatTimestamp(message.timestamp)}
                    </div>

                    {message.suggestions && message.suggestions.length > 0 && (
                      <div className="mt-3 space-y-2">
                        <p className="text-xs font-medium text-blue-800 dark:text-yellow-300">
                          Suggestions:
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {message.suggestions.map((suggestion, i) => (
                            <button
                              key={i}
                              onClick={() => sendMessage(suggestion)}
                              className="px-3 py-1.5 text-sm bg-gray-300 dark:bg-blue-800 hover:bg-gray-400 dark:hover:bg-blue-700 border border-gray-400 dark:border-blue-700 text-blue-900 dark:text-yellow-400 rounded-full hover:border-blue-500 dark:hover:border-yellow-400 transition-all duration-200 hover:shadow-sm"
                            >
                              {suggestion}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="flex items-start space-x-3 max-w-4xl">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-300 dark:bg-blue-800 flex items-center justify-center">
                    <Bot className="w-4 h-4 text-blue-800 dark:text-yellow-400" />
                  </div>

                  <div className="bg-gray-200 dark:bg-slate-900 border border-gray-300 dark:border-slate-700 rounded-2xl rounded-bl-md px-4 py-3 shadow-md">
                    <div className="flex items-center space-x-3">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                        <div
                          className="w-2 h-2 bg-purple-500 rounded-full animate-pulse"
                          style={{ animationDelay: "0.1s" }}
                        ></div>
                        <div
                          className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"
                          style={{ animationDelay: "0.2s" }}
                        ></div>
                      </div>
                      <span className="text-blue-800 dark:text-yellow-300 font-medium">
                        Big Brother is thinking...
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <div className="flex-shrink-0 border-t border-gray-300/20 dark:border-slate-700/20 bg-gray-200/80 dark:bg-slate-900/80 backdrop-blur-md p-6">
            <form onSubmit={handleSubmit} className="flex space-x-4">
              <div className="flex-1 relative">
                <input
                  ref={inputRef}
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Share your idea, no matter how rough..."
                  className="w-full border border-gray-400 dark:border-slate-600 rounded-2xl px-6 py-4 text-blue-900 dark:text-yellow-100 placeholder-blue-600 dark:placeholder-yellow-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm bg-gray-100 dark:bg-slate-900 backdrop-blur-sm transition-all"
                  disabled={isLoading}
                />
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-xs text-blue-600 dark:text-yellow-400 opacity-60">
                  Ctrl+Enter to send
                </div>
              </div>
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-2xl hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 shadow-lg hover:shadow-xl transition-all font-medium"
              >
                <Send className="w-5 h-5" />
                <span>Send</span>
              </button>
            </form>
          </div>
        </main>
      </div>
    </div>
  );
}
