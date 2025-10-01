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
} from "lucide-react";
import ChatList from "./components/ChatList";
import { useAuth } from "../contexts/AuthContext";
import { AuthModal } from "../components/AuthModal";
import { formatChatTimestamp, cn } from "../lib/utils";

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
  const [multiPerspectiveMode, setMultiPerspectiveMode] = useState(false);
  const [theme, setTheme] = useState<"light" | "dark">("light");
  const messagesEndRef = useRef<HTMLDivElement>(null);
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

  const toggleTheme = () => {
    const newTheme = theme === "light" ? "dark" : "light";
    setTheme(newTheme);
    document.documentElement.classList.toggle("dark", newTheme === "dark");
    localStorage.setItem("theme", newTheme);
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
              {/* Theme Toggle */}
              <button
                onClick={toggleTheme}
                className="flex items-center space-x-2 px-3 py-1.5 bg-gray-300 dark:bg-blue-800 text-blue-900 dark:text-yellow-400 rounded-full hover:bg-gray-400 dark:hover:bg-blue-700 transition-all"
                title={`Switch to ${theme === "light" ? "dark" : "light"} mode`}
              >
                {theme === "light" ? (
                  <Moon className="w-4 h-4" />
                ) : (
                  <Sun className="w-4 h-4" />
                )}
              </button>

              {/* Multi-Perspective Toggle */}
              <button
                onClick={() => setMultiPerspectiveMode(!multiPerspectiveMode)}
                className={`flex items-center space-x-2 px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                  multiPerspectiveMode
                    ? "bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-md"
                    : "bg-gray-300 dark:bg-blue-800 text-blue-900 dark:text-yellow-400 hover:bg-gray-400 dark:hover:bg-blue-700"
                }`}
                title={
                  multiPerspectiveMode
                    ? "Multi-AI Mode: ON"
                    : "Multi-AI Mode: OFF"
                }
              >
                {multiPerspectiveMode ? (
                  <Users className="w-4 h-4" />
                ) : (
                  <User className="w-4 h-4" />
                )}
                <span>{multiPerspectiveMode ? "Multi-AI" : "Single AI"}</span>
              </button>

              <div className="flex items-center space-x-2 px-3 py-1.5 bg-gray-300 dark:bg-blue-800 rounded-full text-sm">
                {getStageDisplay(conversationState).icon}
                <span className="font-medium text-blue-900 dark:text-yellow-400">
                  {getStageDisplay(conversationState).label}
                </span>
              </div>

              {user ? (
                <div className="flex items-center space-x-3">
                  <div className="flex items-center space-x-2 px-3 py-1.5 bg-gray-300 dark:bg-blue-800 rounded-full">
                    <User className="w-4 h-4 text-blue-900 dark:text-yellow-400" />
                    <span className="text-sm font-medium text-blue-900 dark:text-yellow-400">
                      {user.full_name}
                    </span>
                  </div>
                  <button
                    onClick={logout}
                    className="flex items-center space-x-1 px-3 py-2 text-sm text-blue-800 dark:text-yellow-300 hover:text-blue-900 dark:hover:text-yellow-200 hover:bg-gray-400 dark:hover:bg-blue-700 rounded-lg transition-all"
                  >
                    <LogOut className="w-4 h-4" />
                    <span>Logout</span>
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setShowAuthModal(true)}
                  className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 shadow-md hover:shadow-lg transition-all"
                >
                  <LogIn className="w-4 h-4" />
                  <span>Sign In</span>
                </button>
              )}
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
                      <p className="whitespace-pre-wrap leading-relaxed">
                        {message.content}
                      </p>
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
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Share your idea, no matter how rough..."
                  className="w-full border border-gray-400 dark:border-slate-600 rounded-2xl px-6 py-4 text-blue-900 dark:text-yellow-100 placeholder-blue-600 dark:placeholder-yellow-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm bg-gray-100 dark:bg-slate-900 backdrop-blur-sm transition-all"
                  disabled={isLoading}
                />
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
