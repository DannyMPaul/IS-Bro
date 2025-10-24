import { SummaryType } from '../types/summary';

export interface SummaryRequest {
    conversation_id: string;
    summary_type: SummaryType;
    include_sentiment: boolean;
    include_key_points: boolean;
}

export interface KeyPoint {
    title: string;
    description: string;
    importance: number;
    category?: string;
}

export interface ConversationSummary {
    summary_id: number;
    conversation_id: string;
    summary_type: SummaryType;
    content: string;
    key_points?: KeyPoint[];
    sentiment_score?: number;
    completion_percentage: number;
    categories: string[];
    tags: string[];
    created_at: string;
    updated_at: string;
}

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class SummaryService {
    async generateSummary(request: SummaryRequest): Promise<ConversationSummary> {
        try {
            const response = await fetch(`${BASE_URL}/api/summaries`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(request),
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error('Failed to generate summary');
            }

            return await response.json();
        } catch (error) {
            throw error;
        }
    }

    async getSummary(summaryId: number): Promise<ConversationSummary> {
        try {
            const response = await fetch(`${BASE_URL}/api/summaries/${summaryId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error('Failed to get summary');
            }

            return await response.json();
        } catch (error) {
            throw error;
        }
    }

    async getConversationSummaries(conversationId: string): Promise<ConversationSummary[]> {
        try {
            const response = await fetch(`${BASE_URL}/api/conversations/${conversationId}/summaries`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error('Failed to get conversation summaries');
            }

            const data = await response.json();
            return data.summaries;
        } catch (error) {
            throw error;
        }
    }
}