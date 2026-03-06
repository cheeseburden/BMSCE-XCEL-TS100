/**
 * Simple JSON file-based meeting store.
 * Replaces MongoDB — stores meetings in data/meetings.json
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const DATA_DIR = path.join(__dirname, '..', 'data');
const DATA_FILE = path.join(DATA_DIR, 'meetings.json');

// Ensure data directory exists
if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
}

// Load meetings from file
function loadMeetings() {
    try {
        if (fs.existsSync(DATA_FILE)) {
            return JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
        }
    } catch (e) {
        console.error('Error loading meetings:', e.message);
    }
    return [];
}

// Save meetings to file
function saveMeetings(meetings) {
    fs.writeFileSync(DATA_FILE, JSON.stringify(meetings, null, 2), 'utf8');
}

// Generate a simple ID
function generateId() {
    return crypto.randomBytes(12).toString('hex');
}

module.exports = {
    create(data) {
        const meetings = loadMeetings();
        const meeting = {
            _id: generateId(),
            title: data.title || 'Untitled Meeting',
            meetUrl: data.meetUrl || '',
            transcript: data.transcript || '',
            summary: { decisions: [], action_items: [] },
            status: data.transcript ? 'completed' : 'scheduled',
            jiraIssuesCreated: false,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
        };
        meetings.push(meeting);
        saveMeetings(meetings);
        return meeting;
    },

    findAll() {
        return loadMeetings().sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
    },

    findById(id) {
        return loadMeetings().find(m => m._id === id) || null;
    },

    update(id, updates) {
        const meetings = loadMeetings();
        const idx = meetings.findIndex(m => m._id === id);
        if (idx === -1) return null;
        meetings[idx] = { ...meetings[idx], ...updates, updatedAt: new Date().toISOString() };
        saveMeetings(meetings);
        return meetings[idx];
    },

    deleteById(id) {
        const meetings = loadMeetings();
        const idx = meetings.findIndex(m => m._id === id);
        if (idx === -1) return null;
        const deleted = meetings.splice(idx, 1)[0];
        saveMeetings(meetings);
        return deleted;
    }
};
