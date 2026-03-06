const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const meetingRoutes = require('./routes/meetings');

dotenv.config();

const app = express();

app.use(cors({ origin: '*', credentials: true }));
app.use(express.json({ limit: '10mb' }));

// Routes
app.use('/api/meetings', meetingRoutes);

app.get('/', (req, res) => {
    res.json({ message: 'Curia AI API is running' });
});

app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ message: 'Something went wrong!' });
});

const PORT = process.env.PORT || 5001;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));