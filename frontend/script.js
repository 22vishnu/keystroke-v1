// =========================
// GLOBAL VARIABLES - Our data storage
// =========================
let relaxedData = { events: [], features: {} };
let stressedData = { events: [], features: {} };
let currentData = relaxedData; // This points to which task we are recording
let startTime;
let timerInterval;

// TWO DIFFERENT TEXTS FOR THE TWO TASKS
const relaxedText = "The graceful swans glided across the serene surface of the lake, their movements creating gentle ripples. The surrounding forest was a tapestry of lush green, with sunlight filtering through the leaves. It was a scene of perfect tranquility and natural beauty.";
const stressedText = "The ambitious quarterback scrambled frantically across the field, dodging relentless defenders under the glaring stadium lights. A critical fourth down with mere seconds remaining, the roaring crowd's anticipation reached a fever pitch, creating an atmosphere of intense, electrifying pressure.";

// =========================
// DOM ELEMENTS - Getting parts of our HTML
// =========================
// Get sections
const introScreen = document.getElementById('intro-screen');
const relaxedTask = document.getElementById('relaxed-task');
const stressedTask = document.getElementById('stressed-task');
const downloadScreen = document.getElementById('download-screen');

// Get textareas
const relaxedTextarea = document.getElementById('relaxed-text');
const stressedTextarea = document.getElementById('stressed-text');

// Get buttons
const startButton = document.getElementById('start-button');
const relaxedDoneButton = document.getElementById('relaxed-done');
const stressedDoneButton = document.getElementById('stressed-done');
const downloadButton = document.getElementById('download-button');

// Get other elements
const timerDisplay = document.getElementById('timer');
const stressedPromptElem = document.getElementById('stressed-prompt');
const relaxedPromptElem = document.getElementById('relaxed-prompt'); // Get the relaxed prompt element

// =========================
// SETUP - Runs when the page loads
// =========================
document.addEventListener('DOMContentLoaded', function() {
    // Put the texts into the correct prompts
    relaxedPromptElem.textContent = relaxedText; // Set relaxed text
    stressedPromptElem.textContent = stressedText; // Set stressed text

    // Attach event listeners to buttons
    startButton.addEventListener('click', startRelaxedTask);
    relaxedDoneButton.addEventListener('click', startStressedTask);
    stressedDoneButton.addEventListener('click', finishExperiment);
    downloadButton.addEventListener('click', downloadCSV);

    // Setup listeners for the typing boxes
    setupEventListeners(relaxedTextarea);
    setupEventListeners(stressedTextarea);
});

// ... [THE REST OF YOUR script.js CODE REMAINS EXACTLY THE SAME] ...
// ... [All functions from setupEventListeners() to downloadCSV() are unchanged] ...
// =========================
// FUNCTION: Set up listeners for a textarea
// =========================
function setupEventListeners(textarea) {
    // When user focuses (clicks) on the textbox to start typing
    textarea.addEventListener('focus', () => {
        currentData.events = []; // Clear previous events
        startTime = performance.now(); // Start the timer for this session
    });

    // When a key is PRESSED down
    textarea.addEventListener('keydown', (event) => {
        // Only record character keys, space, and backspace
        if (event.key.length === 1 || event.key === ' ' || event.key === 'Backspace') {
            currentData.events.push({
                type: 'keydown',
                key: event.key,
                code: event.code,
                timestamp: performance.now() // High-precision timestamp
            });
        }
    });

    // When a key is RELEASED
    textarea.addEventListener('keyup', (event) => {
        if (event.key.length === 1 || event.key === ' ' || event.key === 'Backspace') {
            currentData.events.push({
                type: 'keyup',
                key: event.key,
                code: event.code,
                timestamp: performance.now()
            });
        }
    });
}

// =========================
// FUNCTION: Start the Relaxed Task
// =========================
function startRelaxedTask() {
    // 1. Change the UI
    introScreen.classList.add('hidden');
    relaxedTask.classList.remove('hidden');

    // 2. Point the recorder to the relaxed data object
    currentData = relaxedData;

    // 3. Reset and focus on the textarea
    relaxedTextarea.value = '';
    relaxedTextarea.disabled = false;
    relaxedTextarea.focus();
}

// =========================
// FUNCTION: Start the Stressed Task
// =========================
function startStressedTask() {
    // 1. Calculate features for the relaxed task
    relaxedData.features = calculateFeatures(relaxedData.events);
    console.log("Relaxed Task Features:", relaxedData.features);

    // 2. Change the UI
    relaxedTask.classList.add('hidden');
    stressedTask.classList.remove('hidden');

    // 3. Point the recorder to the stressed data object
    currentData = stressedData;

    // 4. Reset and focus on the textarea
    stressedTextarea.value = '';
    stressedTextarea.disabled = false;
    stressedTextarea.focus();

    // 5. Start the stressful timer!
    startTimer(120); // 2 minutes = 120 seconds
}

// =========================
// FUNCTION: Start the Countdown Timer
// =========================
function startTimer(duration) {
    let timeLeft = duration;
    timerDisplay.textContent = formatTime(timeLeft);
    timerDisplay.style.color = '#e74c3c'; // Red color

    timerInterval = setInterval(() => {
        timeLeft--;
        timerDisplay.textContent = formatTime(timeLeft);

        // Change color when time is low
        if (timeLeft < 30) {
            timerDisplay.style.color = '#ff0000'; // Bright red
        }

        // When time runs out
        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            stressedTextarea.disabled = true;
            stressedDoneButton.classList.remove('hidden');
            alert("Time's up! Please click 'Finish Study'.");
        }
    }, 1000); // Update every second
}

// Helper function to format seconds into MM:SS
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

// =========================
// FUNCTION: Finish the Experiment
// =========================
function finishExperiment() {
    clearInterval(timerInterval); // Stop the timer
    stressedData.features = calculateFeatures(stressedData.events); // Calculate stressed features
    console.log("Stressed Task Features:", stressedData.features);

    // Change the UI
    stressedTask.classList.add('hidden');
    downloadScreen.classList.remove('hidden');
}

// =========================
// FUNCTION: Calculate Features (The Most Important Function!)
// =========================
function calculateFeatures(events) {
    if (events.length < 4) return { error: "Not enough data" }; // Check if we have data

    let holdTimes = [];
    let latencies = [];
    let totalKeysPressed = 0;
    let totalBackspaces = 0;

    // We'll use a Map to match keydown and keyup events
    let keydownMap = new Map();

    // 1. First, calculate Hold Times
    for (let event of events) {
        if (event.type === 'keydown') {
            keydownMap.set(event.code, event.timestamp); // Store keydown time
            totalKeysPressed++;
            if (event.key === 'Backspace') totalBackspaces++;
        }

        if (event.type === 'keyup' && keydownMap.has(event.code)) {
            const holdTime = event.timestamp - keydownMap.get(event.code);
            if (holdTime > 0) { // Sanity check
                holdTimes.push(holdTime);
            }
            keydownMap.delete(event.code); // Remove matched event
        }
    }

    // 2. Now, calculate Latencies (time between key RELEASES)
    let keyUpEvents = events.filter(e => e.type === 'keyup' && e.key !== 'Backspace');
    for (let i = 1; i < keyUpEvents.length; i++) {
        const latency = keyUpEvents[i].timestamp - keyUpEvents[i-1].timestamp;
        if (latency > 0) { // Sanity check
            latencies.push(latency);
        }
    }

    // 3. Calculate Statistics
    function calcStats(arr) {
        if (arr.length === 0) return { mean: 0, std: 0, median: 0 };
        const mean = arr.reduce((a, b) => a + b, 0) / arr.length;
        const sorted = arr.slice().sort((a, b) => a - b);
        const median = sorted[Math.floor(sorted.length / 2)];
        const variance = arr.reduce((sq, n) => sq + Math.pow(n - mean, 2), 0) / arr.length;
        const std = Math.sqrt(variance);
        return { mean, median, std };
    }

    const holdTimeStats = calcStats(holdTimes);
    const latencyStats = calcStats(latencies);
    const errorRate = totalBackspaces / totalKeysPressed;
    
    // Calculate typing accuracy
    const typing_accuracy = (totalKeysPressed - (2 * totalBackspaces)) / totalKeysPressed;

    const totalChars = totalKeysPressed - totalBackspaces;
    const sessionDuration = events.length > 0 ? events[events.length-1].timestamp - events[0].timestamp : 0;
    const wpm = (totalChars / 5) / (sessionDuration / 60000);

    // 4. Return the final feature set for ML
    return {
        total_keys_pressed: totalKeysPressed,
        total_backspaces: totalBackspaces,
        error_rate: errorRate,
        typing_accuracy: typing_accuracy,
        hold_time_mean: holdTimeStats.mean,
        hold_time_std: holdTimeStats.std,
        hold_time_median: holdTimeStats.median,
        latency_mean: latencyStats.mean,
        latency_std: latencyStats.std,
        latency_median: latencyStats.median,
        typing_speed_wpm: wpm,
        session_duration_ms: sessionDuration
    };
}

// =========================
// FUNCTION: Download the Data as CSV
// =========================
function downloadCSV() {
    // Create the header row for the CSV - with typing_accuracy
    let csvContent = "condition,total_keys_pressed,total_backspaces,error_rate,typing_accuracy,hold_time_mean,hold_time_std,hold_time_median,latency_mean,latency_std,latency_median,typing_speed_wpm,session_duration_ms\n";

    // Add the relaxed data row - with typing_accuracy
    const r = relaxedData.features;
    csvContent += `relaxed,${r.total_keys_pressed},${r.total_backspaces},${r.error_rate},${r.typing_accuracy},${r.hold_time_mean},${r.hold_time_std},${r.hold_time_median},${r.latency_mean},${r.latency_std},${r.latency_median},${r.typing_speed_wpm},${r.session_duration_ms}\n`;

    // Add the stressed data row - with typing_accuracy
    const s = stressedData.features;
    csvContent += `stressed,${s.total_keys_pressed},${s.total_backspaces},${s.error_rate},${s.typing_accuracy},${s.hold_time_mean},${s.hold_time_std},${s.hold_time_median},${s.latency_mean},${s.latency_std},${s.latency_median},${s.typing_speed_wpm},${s.session_duration_ms}\n`;

    // Create a downloadable file
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'keystroke_study_data.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}