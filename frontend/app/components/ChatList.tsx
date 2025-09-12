"use client";

import React, { useState, useEffect } from "react";
import { formatDistanceToNow } from "date-fns";

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
      const response = await fetch("http://localhost:8000/api/conversations");
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
    <div className="w-80 bg-gray-50 border-r border-gray-200 h-screen overflow-y-auto">
      <div className="p-4 border-b border-gray-200">
        <button
          onClick={onNewChat}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors"
        >
          + New Chat
        </button>
      </div>

      <div className="p-4">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">
          Recent Conversations
        </h2>

        <div className="space-y-2">
          {conversations.map((conv) => (
            <div
              key={conv.id}
              className={`p-3 rounded-lg cursor-pointer transition-colors group ${
                currentConversationId === conv.id
                  ? "bg-blue-100 border-blue-300"
                  : "bg-white hover:bg-gray-100 border-gray-200"
              } border`}
              onClick={() => onSelectConversation(conv.id)}
            >
              <div className="flex justify-between items-start">
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
                      className="w-full px-2 py-1 border rounded text-sm"
                      autoFocus
                      onClick={(e) => e.stopPropagation()}
                    />
                  ) : (
                    <h3 className="font-medium text-gray-900 truncate">
                      {conv.title}
                    </h3>
                  )}

                  <div className="flex justify-between items-center mt-1">
                    <span className="text-xs text-gray-500">
                      {formatDistanceToNow(new Date(conv.updated_at), {
                        addSuffix: true,
                      })}
                    </span>
                    <span className="text-xs text-gray-400">
                      {conv.message_count} messages
                    </span>
                  </div>
                </div>

                <div className="flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={(e) => startEditing(conv, e)}
                    className="p-1 text-gray-400 hover:text-gray-600"
                    title="Rename"
                  >
                    ✏️
                  </button>
                  <button
                    onClick={(e) => deleteConversation(conv.id, e)}
                    className="p-1 text-gray-400 hover:text-red-600"
                    title="Delete"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {conversations.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            <p>No conversations yet</p>
            <p className="text-sm mt-2">Start your first chat to begin!</p>
          </div>
        )}
      </div>
    </div>
  );
}
