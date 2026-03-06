import { API_BASE_URL } from "@/config/api";
import { getJiraConfig } from "@/lib/session";

const API_URL = `${API_BASE_URL}/api/meetings`;

class MeetingService {
    private getHeaders(): HeadersInit {
        const token = localStorage.getItem('token');
        return {
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        };
    }

    // Get all meetings
    async getMeetings() {
        try {
            const response = await fetch(API_URL, {
                headers: this.getHeaders()
            });
            return await response.json();
        } catch (error) {
            throw new Error('Network error fetching meetings');
        }
    }

    // Get single meeting by ID
    async getMeetingById(id: string) {
        try {
            const response = await fetch(`${API_URL}/${id}`, {
                headers: this.getHeaders()
            });
            return await response.json();
        } catch (error) {
            throw new Error('Network error fetching meeting');
        }
    }

    // Create a new meeting
    async createMeeting(data: { title: string; meetUrl?: string; transcript?: string }) {
        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify(data)
            });
            return await response.json();
        } catch (error) {
            throw new Error('Network error creating meeting');
        }
    }

    // Add transcript to a meeting
    async addTranscript(id: string, transcript: string) {
        try {
            const response = await fetch(`${API_URL}/${id}/transcript`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify({ transcript })
            });
            return await response.json();
        } catch (error) {
            throw new Error('Network error adding transcript');
        }
    }

    // Analyze a meeting (AI summarization + Jira)
    async analyzeMeeting(id: string) {
        try {
            const jiraConfig = getJiraConfig();
            const body = jiraConfig ? { jiraConfig } : {};
            const response = await fetch(`${API_URL}/${id}/analyze`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify(body)
            });
            return await response.json();
        } catch (error) {
            throw new Error('Network error analyzing meeting');
        }
    }

    // Delete a meeting
    async deleteMeeting(id: string) {
        try {
            const response = await fetch(`${API_URL}/${id}`, {
                method: 'DELETE',
                headers: this.getHeaders()
            });
            return await response.json();
        } catch (error) {
            throw new Error('Network error deleting meeting');
        }
    }
}

export default new MeetingService();
