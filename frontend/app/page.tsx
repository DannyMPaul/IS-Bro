"use client";

import React, { useState, useRef, useEffect } from "react";
import { Send, Brain, Lightbulb, MessageSquare } from "lucide-react";
import ChatList from "./components/ChatList";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  suggestions?: string[];
}

interface ChatResponse {
  response: string;
  session_id: string;
  conversation_state: string;
  suggestions?: string[];
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>("");
  const [conversationState, setConversationState] = useState("initial");
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const startNewChat = () => {
    setMessages([]);
    setSessionId("");
    setConversationState("initial");
  };

  const loadConversation = async (conversationId: string) => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/conversations/${conversationId}`
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
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: messageToSend,
          session_id: sessionId || undefined,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to send message");
      }

      const data: ChatResponse = await response.json();

      if (!sessionId) {
        setSessionId(data.session_id);
        setRefreshTrigger((prev) => prev + 1); // Trigger chat list refresh
      }

      setConversationState(data.conversation_state);

      const assistantMessage: Message = {
        role: "assistant",
        content: data.response,
        timestamp: new Date().toISOString(),
        suggestions: data.suggestions,
      };

      setMessages((prev) => [...prev, assistantMessage]);
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
    <div className="h-screen flex bg-gray-50">
      <ChatList
        currentConversationId={sessionId}
        onSelectConversation={loadConversation}
        onNewChat={startNewChat}
        refreshTrigger={refreshTrigger}
      />{" "}
      <div className="flex-1 flex flex-col">
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Brain className="w-8 h-8 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900">Idea Shaper</h1>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              {getStageDisplay(conversationState).icon}
              <span>{getStageDisplay(conversationState).label}</span>
            </div>
          </div>
        </header>

        <main className="flex-1 flex flex-col">
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {messages.length === 0 && (
              <div className="text-center py-12">
                <Brain className="w-16 h-16 text-blue-600 mx-auto mb-4" />
                <h2 className="text-2xl font-semibold text-gray-900 mb-2">
                  Hey there! I'm Big Brother.
                </h2>
                <p className="text-gray-600 max-w-md mx-auto">
                  I'm here to help you turn that vague idea in your head into
                  something concrete and actionable. Tell me what's on your mind
                  - no matter how rough or incomplete it is.
                </p>
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
                  className={`max-w-3xl rounded-lg px-4 py-3 ${
                    message.role === "user"
                      ? "bg-blue-600 text-white"
                      : "bg-white border border-gray-200 text-gray-900"
                  }`}
                >
                  <p className="whitespace-pre-wrap">{message.content}</p>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white border border-gray-200 rounded-lg px-4 py-3">
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                    <span className="text-gray-600">
                      Big Brother is thinking...
                    </span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <div className="border-t border-gray-200 bg-white p-6">
            <form onSubmit={handleSubmit} className="flex space-x-4">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Share your idea, no matter how rough..."
                className="flex-1 border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                <Send className="w-4 h-4" />
                <span>Send</span>
              </button>
            </form>
          </div>
        </main>
      </div>
    </div>
  );
}
