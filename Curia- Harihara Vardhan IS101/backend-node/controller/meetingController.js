const store = require('../store/meetingStore');
const axios = require('axios');

const FLASK_API_URL = process.env.FLASK_API_URL || 'http://localhost:5002';

const hasCompleteJiraConfig = (config) => {
    if (!config || typeof config !== 'object') return false;
    const { jiraUrl, jiraProjectKey, jiraEmail, jiraApiToken } = config;
    return Boolean(jiraUrl && jiraProjectKey && jiraEmail && jiraApiToken);
};

// Create a new meeting
const createMeeting = async (req, res) => {
    try {
        const { title, meetUrl, transcript } = req.body;
        const meeting = store.create({ title, meetUrl, transcript });
        res.status(201).json({ success: true, message: 'Meeting created', meeting });
    } catch (error) {
        console.error('Create meeting error:', error);
        res.status(500).json({ message: 'Error creating meeting', error: error.message });
    }
};

// Get all meetings
const getMeetings = async (req, res) => {
    try {
        const meetings = store.findAll().map(m => {
            const { transcript, ...rest } = m; // Don't send full transcript in list
            return rest;
        });
        res.json({ success: true, count: meetings.length, meetings });
    } catch (error) {
        console.error('Get meetings error:', error);
        res.status(500).json({ message: 'Error fetching meetings', error: error.message });
    }
};

// Get single meeting
const getMeetingById = async (req, res) => {
    try {
        const meeting = store.findById(req.params.id);
        if (!meeting) return res.status(404).json({ message: 'Meeting not found' });
        res.json({ success: true, meeting });
    } catch (error) {
        console.error('Get meeting error:', error);
        res.status(500).json({ message: 'Error fetching meeting', error: error.message });
    }
};

// Update a meeting
const updateMeeting = async (req, res) => {
    try {
        const meeting = store.findById(req.params.id);
        if (!meeting) return res.status(404).json({ message: 'Meeting not found' });

        const updates = {};
        if (req.body.title) updates.title = req.body.title;
        if (req.body.meetUrl) updates.meetUrl = req.body.meetUrl;
        if (req.body.status) updates.status = req.body.status;

        const updated = store.update(req.params.id, updates);
        res.json({ success: true, meeting: updated });
    } catch (error) {
        console.error('Update meeting error:', error);
        res.status(500).json({ message: 'Error updating meeting', error: error.message });
    }
};

// Delete a meeting
const deleteMeeting = async (req, res) => {
    try {
        const meeting = store.deleteById(req.params.id);
        if (!meeting) return res.status(404).json({ message: 'Meeting not found' });
        res.json({ success: true, message: 'Meeting deleted' });
    } catch (error) {
        console.error('Delete meeting error:', error);
        res.status(500).json({ message: 'Error deleting meeting', error: error.message });
    }
};

// Add transcript
const addTranscript = async (req, res) => {
    try {
        const meeting = store.findById(req.params.id);
        if (!meeting) return res.status(404).json({ message: 'Meeting not found' });

        const { transcript } = req.body;
        if (!transcript) return res.status(400).json({ message: 'Transcript text is required' });

        const updated = store.update(req.params.id, { transcript, status: 'completed' });
        res.json({ success: true, message: 'Transcript added', meeting: updated });
    } catch (error) {
        console.error('Add transcript error:', error);
        res.status(500).json({ message: 'Error adding transcript', error: error.message });
    }
};

// Analyze meeting with AI + create Jira tickets
const analyzeMeeting = async (req, res) => {
    try {
        const meeting = store.findById(req.params.id);
        if (!meeting) return res.status(404).json({ message: 'Meeting not found' });
        if (!meeting.transcript) return res.status(400).json({ message: 'No transcript to analyze' });

        const { jiraConfig } = req.body;
        const useJira = hasCompleteJiraConfig(jiraConfig);

        if (jiraConfig && !useJira) {
            return res.status(400).json({
                message: 'Incomplete Jira config. Provide jiraUrl, jiraProjectKey, jiraEmail, jiraApiToken.'
            });
        }

        // Call Flask AI summarizer
        const flaskResponse = await axios.post(
            `${FLASK_API_URL}/analyze-transcript`,
            { transcript: meeting.transcript, jiraConfig: useJira ? jiraConfig : null },
            { headers: { 'Content-Type': 'application/json' }, timeout: 180000 }
        );

        const data = flaskResponse.data || {};
        const actionItems = Array.isArray(data.action_items) ? data.action_items : [];
        const jiraErrors = Array.isArray(data.jira_errors) ? data.jira_errors : [];
        const hasJiraKeys = useJira && actionItems.some(item => item && item.jiraIssueKey);

        // Update meeting with results
        const updated = store.update(req.params.id, {
            summary: {
                decisions: data.decisions || [],
                action_items: actionItems
            },
            status: 'analyzed',
            jiraIssuesCreated: hasJiraKeys,
            jiraErrors
        });

        const message = hasJiraKeys
            ? 'Analyzed + Jira tickets created'
            : jiraErrors.length
                ? 'Analyzed (Jira errors found)'
                : useJira
                    ? 'Analyzed (no Jira tickets created)'
                    : 'Analyzed (no Jira config)';

        res.json({
            success: true,
            message,
            meeting: updated
        });
    } catch (error) {
        console.error('Analyze error:', error.message);
        if (error.code === 'ECONNREFUSED') {
            return res.status(503).json({ message: `Flask AI service not reachable at ${FLASK_API_URL}` });
        }
        res.status(500).json({ message: 'Error analyzing meeting', error: error.message });
    }
};

module.exports = { createMeeting, getMeetings, getMeetingById, updateMeeting, deleteMeeting, addTranscript, analyzeMeeting };
