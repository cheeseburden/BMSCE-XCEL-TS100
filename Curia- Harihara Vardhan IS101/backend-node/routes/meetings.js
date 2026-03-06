const express = require('express');
const {
    createMeeting,
    getMeetings,
    getMeetingById,
    updateMeeting,
    deleteMeeting,
    addTranscript,
    analyzeMeeting
} = require('../controller/meetingController');

const router = express.Router();

// No auth middleware — using fake auth (simplified for hackathon)

// CRUD routes
router.post('/', createMeeting);
router.get('/', getMeetings);
router.get('/:id', getMeetingById);
router.put('/:id', updateMeeting);
router.delete('/:id', deleteMeeting);

// Transcript & analysis
router.post('/:id/transcript', addTranscript);
router.post('/:id/analyze', analyzeMeeting);

module.exports = router;
