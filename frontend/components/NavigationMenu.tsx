"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  Menu,
  X,
  FileText,
  Search,
  BarChart3,
  Download,
  Keyboard,
  Moon,
  Sun,
  Users,
  User,
  LogOut,
  LogIn,
  Settings,
  HelpCircle,
  Sparkles,
} from "lucide-react";

interface NavigationMenuProps {
  user: any;
  theme: "light" | "dark";
  multiPerspectiveMode: boolean;
  sessionId: string;
  hasMessages: boolean;
  onToggleTheme: () => void;
  onToggleMultiPerspective: () => void;
  onShowTemplates: () => void;
  onShowSearch: () => void;
  onShowInsights: () => void;
  onShowShortcuts: () => void;
  onExport: (format: "json" | "markdown") => void;
  onShowAuth: () => void;
  onLogout: () => void;
}

export const NavigationMenu: React.FC<NavigationMenuProps> = ({
  user,
  theme,
  multiPerspectiveMode,
  sessionId,
  hasMessages,
  onToggleTheme,
  onToggleMultiPerspective,
  onShowTemplates,
  onShowSearch,
  onShowInsights,
  onShowShortcuts,
  onExport,
  onShowAuth,
  onLogout,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Close menu on escape key
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setIsOpen(false);
      }
    };

    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, []);

  const menuItems = [
    {
      category: "Templates & Tools",
      items: [
        {
          icon: <FileText className="w-4 h-4" />,
          label: "Conversation Templates",
          shortcut: "Ctrl+T",
          onClick: () => {
            onShowTemplates();
            setIsOpen(false);
          },
        },
        {
          icon: <Search className="w-4 h-4" />,
          label: "Search Conversations",
          shortcut: "Ctrl+F",
          onClick: () => {
            onShowSearch();
            setIsOpen(false);
          },
        },
        {
          icon: <BarChart3 className="w-4 h-4" />,
          label: "Conversation Insights",
          shortcut: "Ctrl+I",
          onClick: () => {
            onShowInsights();
            setIsOpen(false);
          },
          disabled: !sessionId,
        },
      ],
    },
    {
      category: "Export & Data",
      items: [
        {
          icon: <Download className="w-4 h-4" />,
          label: "Export as JSON",
          onClick: () => {
            onExport("json");
            setIsOpen(false);
          },
          disabled: !hasMessages,
        },
        {
          icon: <Download className="w-4 h-4" />,
          label: "Export as Markdown",
          onClick: () => {
            onExport("markdown");
            setIsOpen(false);
          },
          disabled: !hasMessages,
        },
      ],
    },
    {
      category: "Settings & Preferences",
      items: [
        {
          icon: multiPerspectiveMode ? (
            <Users className="w-4 h-4" />
          ) : (
            <User className="w-4 h-4" />
          ),
          label: multiPerspectiveMode ? "Multi-AI Mode: ON" : "Single AI Mode",
          onClick: () => {
            onToggleMultiPerspective();
            setIsOpen(false);
          },
          highlight: multiPerspectiveMode,
        },
        {
          icon:
            theme === "light" ? (
              <Moon className="w-4 h-4" />
            ) : (
              <Sun className="w-4 h-4" />
            ),
          label: `${theme === "light" ? "Dark" : "Light"} Mode`,
          onClick: () => {
            onToggleTheme();
            setIsOpen(false);
          },
        },
        {
          icon: <Keyboard className="w-4 h-4" />,
          label: "Keyboard Shortcuts",
          shortcut: "Ctrl+/",
          onClick: () => {
            onShowShortcuts();
            setIsOpen(false);
          },
        },
      ],
    },
  ];

  return (
    <div className="relative" ref={menuRef}>
      {/* Menu Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-3 py-2 bg-gray-300 dark:bg-blue-800 text-blue-900 dark:text-yellow-400 rounded-lg hover:bg-gray-400 dark:hover:bg-blue-700 transition-all"
        title="Menu"
      >
        {isOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        <span className="hidden sm:inline">Menu</span>
      </button>

      {/* Menu Dropdown */}
      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-80 bg-white dark:bg-slate-900 border border-gray-300 dark:border-slate-700 rounded-lg shadow-xl z-50 max-h-96 overflow-y-auto">
          {/* Header */}
          <div className="p-4 border-b border-gray-200 dark:border-slate-700">
            <div className="flex items-center space-x-2">
              <Sparkles className="w-5 h-5 text-blue-600 dark:text-yellow-400" />
              <h3 className="font-semibold text-blue-900 dark:text-yellow-100">
                Idea Shaper Tools
              </h3>
            </div>
          </div>

          {/* Menu Categories */}
          <div className="py-2">
            {menuItems.map((category, categoryIndex) => (
              <div key={categoryIndex}>
                <div className="px-4 py-2">
                  <h4 className="text-xs font-semibold text-blue-700 dark:text-yellow-300 uppercase tracking-wide">
                    {category.category}
                  </h4>
                </div>
                <div className="space-y-1 px-2">
                  {category.items.map((item, itemIndex) => (
                    <button
                      key={itemIndex}
                      onClick={item.onClick}
                      disabled={item.disabled}
                      className={`w-full flex items-center justify-between px-3 py-2 text-sm rounded-lg transition-all ${
                        item.disabled
                          ? "opacity-50 cursor-not-allowed"
                          : "hover:bg-gray-100 dark:hover:bg-slate-800"
                      } ${
                        item.highlight
                          ? "bg-gradient-to-r from-purple-500/10 to-pink-500/10 border border-purple-200 dark:border-purple-700"
                          : ""
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <div
                          className={
                            item.highlight
                              ? "text-purple-600 dark:text-purple-400"
                              : "text-blue-600 dark:text-yellow-400"
                          }
                        >
                          {item.icon}
                        </div>
                        <span
                          className={`text-left ${
                            item.highlight
                              ? "text-purple-900 dark:text-purple-100 font-medium"
                              : "text-blue-900 dark:text-yellow-100"
                          }`}
                        >
                          {item.label}
                        </span>
                      </div>
                      {item.shortcut && (
                        <kbd className="px-2 py-1 bg-gray-200 dark:bg-slate-700 text-xs rounded border text-blue-700 dark:text-yellow-300">
                          {item.shortcut}
                        </kbd>
                      )}
                    </button>
                  ))}
                </div>
                {categoryIndex < menuItems.length - 1 && (
                  <div className="my-2 border-t border-gray-200 dark:border-slate-700"></div>
                )}
              </div>
            ))}
          </div>

          {/* User Section */}
          <div className="border-t border-gray-200 dark:border-slate-700 p-2">
            {user ? (
              <div className="space-y-1">
                <div className="px-3 py-2 text-sm">
                  <div className="flex items-center space-x-2">
                    <User className="w-4 h-4 text-blue-600 dark:text-yellow-400" />
                    <span className="text-blue-900 dark:text-yellow-100 font-medium">
                      {user.full_name}
                    </span>
                  </div>
                  <div className="text-xs text-blue-700 dark:text-yellow-300 mt-1">
                    {user.email}
                  </div>
                </div>
                <button
                  onClick={() => {
                    onLogout();
                    setIsOpen(false);
                  }}
                  className="w-full flex items-center space-x-3 px-3 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-all"
                >
                  <LogOut className="w-4 h-4" />
                  <span>Sign Out</span>
                </button>
              </div>
            ) : (
              <button
                onClick={() => {
                  onShowAuth();
                  setIsOpen(false);
                }}
                className="w-full flex items-center space-x-3 px-3 py-2 text-sm text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-all"
              >
                <LogIn className="w-4 h-4" />
                <span>Sign In</span>
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
