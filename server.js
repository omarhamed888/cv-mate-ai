const express = require('express');
const cors = require('cors');
const fileUpload = require('express-fileupload');
const pdfParse = require('pdf-parse');
const { GoogleGenerativeAI } = require('@google/generative-ai');
const dotenv = require('dotenv');
const path = require('path');
const fs = require('fs');

dotenv.config();
const app = express();
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

// Middleware
app.use(cors());
app.use(fileUpload());
app.use(express.json());
app.use(express.static('public'));

// Logging middleware
app.use((req, res, next) => {
    const timestamp = new Date().toISOString();
    const user = req.headers['x-user'] || 'anonymous';
    console.log(`[${timestamp}] ${user} - ${req.method} ${req.url}`);
    next();
});

// Session storage
const sessions = new Map();

// Routes
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'landing.html'));
});

app.get('/cv-services', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'cv-services.html'));
});

app.get('/interview-chat', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'interview-chat.html'));
});

app.get('/ats-scanner', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'ats-scanner.html'));
});

app.get('/cv-rewriter', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'cv-rewriter.html'));
});

// API Routes
app.post('/api/interview-chat', async (req, res) => {
    try {
        const timestamp = new Date().toISOString();
        const user = req.headers['x-user'] || 'anonymous';
        const sessionId = req.headers['x-session-id'];

        let conversation = sessions.get(sessionId) || [];
        const { message } = req.body;
        let cvText = '';

        if (req.files?.cv) {
            const pdf = await pdfParse(req.files.cv.data);
            cvText = pdf.text;
            // Store CV text in session
            conversation.push({ role: 'system', content: `CV Content: ${cvText}` });
        }

        if (message) {
            conversation.push({ role: 'user', content: message });
        }

        const prompt = `
            Based on the following conversation and CV, provide a relevant response:
            Previous conversation: ${JSON.stringify(conversation)}
            Current time: ${timestamp}
            User: ${user}
            ${message ? `Current message: ${message}` : 'Start interview'}
        `;

        const response = await getGeminiResponse(prompt);
        conversation.push({ role: 'assistant', content: response });
        
        // Update session
        sessions.set(sessionId, conversation);

        // Log interaction
        logInteraction(user, 'interview-chat', { timestamp, message, response });

        res.json({ reply: response });
    } catch (error) {
        console.error('Error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

app.post('/api/ats-scan', async (req, res) => {
    try {
        const timestamp = new Date().toISOString();
        const user = req.headers['x-user'] || 'anonymous';

        if (!req.files?.cv) {
            return res.status(400).json({ error: 'No CV file provided' });
        }

        const pdf = await pdfParse(req.files.cv.data);
        const cvText = pdf.text;

        const scanPrompt = `
            Analyze this CV for ATS compatibility. Consider:
            1. Keyword optimization
            2. Format compatibility
            3. Overall ATS score
            
            CV Text: ${cvText}
            Current time: ${timestamp}
            User: ${user}
        `;

        const analysis = await getGeminiResponse(scanPrompt);
        
        // Log interaction
        logInteraction(user, 'ats-scan', { timestamp, analysis });

        res.json({ analysis });
    } catch (error) {
        console.error('Error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

app.post('/api/cv-rewrite', async (req, res) => {
    try {
        const timestamp = new Date().toISOString();
        const user = req.headers['x-user'] || 'anonymous';

        if (!req.files?.cv) {
            return res.status(400).json({ error: 'No CV file provided' });
        }

        const pdf = await pdfParse(req.files.cv.data);
        const cvText = pdf.text;

        const rewritePrompt = `
            Improve this CV by:
            1. Enhancing grammar and wording
            2. Optimizing format
            3. Making content more professional
            
            CV Text: ${cvText}
            Current time: ${timestamp}
            User: ${user}
        `;

        const improvedCV = await getGeminiResponse(rewritePrompt);
        
        // Log interaction
        logInteraction(user, 'cv-rewrite', { timestamp, originalLength: cvText.length, improvedLength: improvedCV.length });

        res.json({ improvedCV });
    } catch (error) {
        console.error('Error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Helper functions
async function getGeminiResponse(prompt) {
    const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });
    const result = await model.generateContent(prompt);
    return result.response.text();
}

function logInteraction(user, service, data) {
    const logEntry = {
        timestamp: data.timestamp,
        user,
        service,
        data
    };

    // Append to log file
    fs.appendFile(
        'interaction_logs.json',
        JSON.stringify(logEntry) + '\n',
        (err) => {
            if (err) console.error('Error writing to log:', err);
        }
    );
}

// Error handling middleware
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ 
        error: 'Internal Server Error',
        timestamp: new Date().toISOString()
    });
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
    console.log(`Started at: ${new Date().toISOString()}`);
    console.log(`Current user: ${process.env.USER || 'unknown'}`);
});