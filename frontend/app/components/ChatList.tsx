"use client";

import React, { useState, useEffect } from "react";
import { formatDistanceToNow } from "date-fns";
import { useAuth } from "../../contexts/AuthContext";
import { MessageSquare, Plus, Edit3, Trash2, Clock } from "lucide-react";
import { formatRelativeTime } from "../../lib/utils";

interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

interface ChatListProps {
  currentConversationId?: string;
  onSelectConversation: (id: string) => void;
  onNewChat: () => void;
  refreshTrigger?: number; // Add trigger to refresh list
}

export default function ChatList({
  currentConversationId,
  onSelectConversation,
  onNewChat,
  refreshTrigger,
}: ChatListProps) {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const { token, user } = useAuth();

  useEffect(() => {
    fetchConversations();
  }, []);

  useEffect(() => {
    if (refreshTrigger) {
      fetchConversations();
    }
  }, [refreshTrigger]);

  const fetchConversations = async () => {
    try {
      console.log("Fetching conversations...");
      
      const headers: any = {};
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      }
      
      const response = await fetch("http://localhost:8000/api/conversations", {
        headers,
      });
      console.log("Response status:", response.status);
      const data = await response.json();
      console.log("Conversations data:", data);
      setConversations(data);
    } catch (error) {
      console.error("Failed to fetch conversations:", error);
    }
  };

  const deleteConversation = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("Delete this conversation?")) return;

    try {
      await fetch(`http://localhost:8000/api/conversations/${id}`, {
        method: "DELETE",
      });
      fetchConversations();
    } catch (error) {
      console.error("Failed to delete conversation:", error);
    }
  };

  const startEditing = (conv: Conversation, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingId(conv.id);
    setEditTitle(conv.title);
  };

  const saveTitle = async (id: string) => {
    try {
      await fetch(
        `http://localhost:8000/api/conversations/${id}/title?title=${encodeURIComponent(
          editTitle
        )}`,
        {
          method: "PUT",
        }
      );
      setEditingId(null);
      fetchConversations();
    } catch (error) {
      console.error("Failed to update title:", error);
    }
  };

  return (
    <div className="w-80 bg-gradient-to-b from-white via-slate-50 to-gray-50 border-r border-gray-200/50 h-screen overflow-y-auto backdrop-blur-sm">
      <div className="p-4 border-b border-gray-200/50 bg-white/80 backdrop-blur-sm">
        <button
          onClick={onNewChat}
          className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white py-3 px-4 rounded-xl font-medium shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center space-x-2"
        >
          <Plus className="w-5 h-5" />
          <span>New Chat</span>
        </button>
      </div>

      <div className="p-4">
        <div className="flex items-center space-x-2 mb-6">
          <MessageSquare className="w-5 h-5 text-blue-600" />
          <h2 className="text-lg font-bold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent">
            {user ? `${user.full_name}'s Chats` : 'Recent Conversations'}
          </h2>
        </div>

        <div className="space-y-3">
          {conversations.map((conv, index) => (
            <div
              key={conv.id}
              className={`relative p-4 rounded-xl cursor-pointer transition-all duration-200 group ${
                currentConversationId === conv.id
                  ? "bg-gradient-to-r from-blue-500/10 to-purple-500/10 border-2 border-blue-200 shadow-md transform scale-[1.02]"
                  : "bg-white/70 hover:bg-white/90 border border-gray-200/50 hover:border-gray-300/50 shadow-sm hover:shadow-md"
              }`}
              onClick={() => onSelectConversation(conv.id)}
              style={{
                animationDelay: `${index * 50}ms`,
              }}
            >
              {/* Gradient accent */}
              <div className={`absolute top-0 left-0 w-1 h-full rounded-l-xl ${
                currentConversationId === conv.id 
                  ? "bg-gradient-to-b from-blue-500 to-purple-500" 
                  : "bg-gradient-to-b from-gray-300 to-gray-400 opacity-0 group-hover:opacity-100"
              } transition-opacity duration-200`} />
              
              <div className="flex justify-between items-start pl-3">
                <div className="flex-1 min-w-0">
                  {editingId === conv.id ? (
                    <input
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      onBlur={() => saveTitle(conv.id)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") saveTitle(conv.id);
                        if (e.key === "Escape") setEditingId(null);
                      }}
                      className="w-full px-3 py-2 border border-blue-300 rounded-lg text-sm font-medium bg-white/80 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      autoFocus
                      onClick={(e) => e.stopPropagation()}
                    />
                  ) : (
                    <h3 className="font-semibold text-gray-900 truncate leading-tight">
                      {conv.title}
                    </h3>
                  )}

                  <div className="flex justify-between items-center mt-2">
                    <div className="flex items-center space-x-1 text-xs text-gray-500">
                      <Clock className="w-3 h-3" />
                      <span>{formatRelativeTime(conv.updated_at)}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <div className="w-2 h-2 rounded-full bg-gradient-to-r from-blue-400 to-purple-400"></div>
                      <span className="text-xs font-medium text-gray-600">
                        {conv.message_count} messages
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex space-x-1 opacity-0 group-hover:opacity-100 transition-all duration-200 ml-2">
                  <button
                    onClick={(e) => startEditing(conv, e)}
                    className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all duration-150"
                    title="Rename"
                  >
                    <Edit3 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={(e) => deleteConversation(conv.id, e)}
                    className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all duration-150"
                    title="Delete"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {conversations.length === 0 && (
          <div className="text-center mt-12 py-8">
            <div className="w-16 h-16 bg-gradient-to-r from-blue-100 to-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <MessageSquare className="w-8 h-8 text-blue-600" />
            </div>
            <p className="text-gray-600 font-medium mb-1">No conversations yet</p>
            <p className="text-sm text-gray-500">Start your first chat to begin!</p>
          </div>
        )}
      </div>
    </div>
  );
}
