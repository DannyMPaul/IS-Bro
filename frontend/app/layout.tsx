import React from "react";
import "./globals.css";
import type { Metadata } from "next";
import { AuthProvider } from "../contexts/AuthContext";

export const metadata: Metadata = {
  title: "Idea Shaper - AI-Powered Idea Refinement",
  description:
    "Transform vague ideas into structured project blueprints with AI mentorship",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
