/**
 * Curia AI — Google Meet Bot
 *
 * Joins a Google Meet as a guest, enables captions,
 * scrapes caption text, and sends the transcript to the backend.
 *
 * Usage:
 *   node index.js <meet-url> [meeting-id]
 */

require('dotenv').config();
const puppeteer = require('puppeteer');
const axios = require('axios');

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:5001';
const BOT_NAME = process.env.BOT_NAME || 'Curia AI Note-taker';
const MAX_DURATION = parseInt(process.env.MAX_DURATION || '3600000');

async function delay(ms) {
    return new Promise(r => setTimeout(r, ms));
}

async function clickByText(page, selector, text) {
    const els = await page.$$(selector);
    for (const el of els) {
        const t = await el.evaluate(e => e.textContent);
        if (t && t.trim().includes(text)) {
            await el.click();
            return true;
        }
    }
    return false;
}

async function joinMeeting(meetUrl) {
    console.log('🤖 Curia AI Bot starting...');
    console.log(`📍 Meet URL: ${meetUrl}`);
    console.log(`👤 Bot name: ${BOT_NAME}`);

    const browser = await puppeteer.launch({
        headless: false,
        args: [
            '--use-fake-ui-for-media-stream',
            '--use-fake-device-for-media-stream',
            '--disable-web-security',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--window-size=1280,720',
        ]
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 720 });

    const context = browser.defaultBrowserContext();
    await context.overridePermissions('https://meet.google.com', [
        'microphone', 'camera', 'notifications'
    ]);

    try {
        // 1. Navigate
        console.log('📡 Navigating to meeting...');
        await page.goto(meetUrl, { waitUntil: 'networkidle2', timeout: 30000 });
        await delay(3000);

        // 2. Handle "Continue without microphone and camera" modal
        console.log('🔍 Checking for media permission modal...');
        const dismissed = await clickByText(page, 'button', 'Continue without microphone and camera');
        if (dismissed) {
            console.log('✅ Dismissed media permission modal');
            await delay(2000);
        }

        // 3. Enter bot name
        console.log('⏳ Looking for name input...');
        const nameInput = await page.waitForSelector(
            'input[aria-label="Your name"], input[placeholder="Your name"]',
            { timeout: 15000 }
        );
        await nameInput.click({ clickCount: 3 });
        await nameInput.type(BOT_NAME, { delay: 50 });
        console.log(`✏️  Entered name: ${BOT_NAME}`);
        await delay(1000);

        // 4. Click "Ask to join"
        console.log('🚪 Clicking "Ask to join"...');
        const clicked = await clickByText(page, 'button', 'Ask to join');
        if (!clicked) {
            // Fallback: try "Join now"
            const clicked2 = await clickByText(page, 'button', 'Join now');
            if (!clicked2) {
                throw new Error('Could not find join button');
            }
        }
        console.log('⏳ Waiting to be admitted...');

        // 5. Wait to be admitted (host admits the bot)
        await page.waitForFunction(() => {
            const btns = Array.from(document.querySelectorAll('button'));
            return btns.some(b => {
                const label = b.getAttribute('aria-label') || '';
                return label.toLowerCase().includes('caption');
            });
        }, { timeout: 300000 }); // Wait up to 5 minutes

        console.log('✅ Joined the meeting!');
        await delay(2000);

        // 6. Enable captions
        console.log('📝 Enabling captions...');
        const captionBtn = await page.$('button[aria-label*="caption" i]');
        if (captionBtn) {
            await captionBtn.click();
            console.log('✅ Captions enabled');
        } else {
            console.log('⚠️ Could not find caption button — will try scraping anyway');
        }

        // 7. Scrape captions
        console.log('🎙️  Scraping captions... (press Ctrl+C to stop)');
        const transcript = await scrapeCaptions(page);

        return transcript;

    } catch (error) {
        console.error('❌ Error:', error.message);
        throw error;
    } finally {
        await browser.close();
    }
}

async function scrapeCaptions(page) {
    const captionData = await page.evaluate((maxDuration) => {
        return new Promise((resolve) => {
            const lines = [];
            let lastText = '';

            const durationTimeout = setTimeout(() => {
                resolve(lines.join('\n'));
            }, maxDuration);

            const observer = new MutationObserver(() => {
                // Google Meet caption containers
                const captionEls = document.querySelectorAll(
                    '[class*="Caption"], [class*="caption"], [data-message-text], [jsname="YSg1Fc"]'
                );
                captionEls.forEach(el => {
                    const text = el.textContent?.trim();
                    if (text && text !== lastText && text.length > 2) {
                        lastText = text;
                        const timestamp = new Date().toLocaleTimeString();
                        lines.push(`[${timestamp}] ${text}`);
                        console.log(`Caption: ${text}`);
                    }
                });
            });

            observer.observe(document.body, {
                childList: true,
                subtree: true,
                characterData: true
            });

            // Detect meeting end
            const checkEnd = setInterval(() => {
                const ended = document.querySelector('[data-call-ended]') ||
                    document.querySelector('[jsname="r4nke"]');
                if (ended) {
                    clearInterval(checkEnd);
                    clearTimeout(durationTimeout);
                    observer.disconnect();
                    resolve(lines.join('\n'));
                }
            }, 3000);
        });
    }, MAX_DURATION);

    return captionData;
}

async function sendTranscript(meetingId, transcript) {
    if (!meetingId || !transcript) {
        console.log('\n📋 Transcript:');
        console.log(transcript || '(empty)');
        // Save locally
        const fs = require('fs');
        const filename = `transcript_${Date.now()}.txt`;
        fs.writeFileSync(filename, transcript || '');
        console.log(`💾 Saved locally as ${filename}`);
        return;
    }

    try {
        console.log(`📤 Sending transcript to backend (meeting ${meetingId})...`);
        await axios.post(`${BACKEND_URL}/api/meetings/${meetingId}/transcript`, { transcript });
        console.log('✅ Transcript saved to backend');
    } catch (error) {
        console.error('❌ Failed to send:', error.message);
        const fs = require('fs');
        const filename = `transcript_${Date.now()}.txt`;
        fs.writeFileSync(filename, transcript);
        console.log(`💾 Saved locally as ${filename}`);
    }
}

// Main
(async () => {
    const meetUrl = process.argv[2];
    const meetingId = process.argv[3];

    if (!meetUrl || !meetUrl.includes('meet.google.com')) {
        console.log('Usage: node index.js <meet-url> [meeting-id]');
        console.log('Example: node index.js https://meet.google.com/abc-defg-hij');
        process.exit(1);
    }

    try {
        const transcript = await joinMeeting(meetUrl);
        console.log(`\n📄 Captured ${(transcript || '').split('\n').filter(Boolean).length} lines`);
        await sendTranscript(meetingId, transcript);
    } catch (error) {
        console.error('Bot failed:', error.message);
        process.exit(1);
    }
})();
