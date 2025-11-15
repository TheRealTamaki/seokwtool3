// DOM Elements
const apiKeyInput = document.getElementById("apiKey");
const queryInput = document.getElementById("query");
const scrapeBtn = document.getElementById("scrapeBtn");
const resultsSection = document.getElementById("resultsSection");
const emptyState = document.getElementById("emptyState");
const closeResultsBtn = document.getElementById("closeResults");
const togglePasswordBtn = document.getElementById("togglePassword");
const charCountEl = document.getElementById("charCount");
const statusMessageEl = document.getElementById("statusMessage");
const errorMessageEl = document.getElementById("errorMessage");
const questionsContainerEl = document.getElementById("questionsContainer");
const questionsListEl = document.getElementById("questionsList");
const resultQueryEl = document.getElementById("resultQuery");
const exportJsonBtn = document.getElementById("exportJson");
const copyJsonBtn = document.getElementById("copyJson");

// State
let lastScrapedData = null;

// Event Listeners
scrapeBtn.addEventListener("click", handleScrape);
closeResultsBtn.addEventListener("click", closeResults);
togglePasswordBtn.addEventListener("click", togglePasswordVisibility);
queryInput.addEventListener("input", updateCharCount);
exportJsonBtn.addEventListener("click", exportAsJson);
copyJsonBtn.addEventListener("click", copyToClipboard);

// Allow Enter key to scrape
queryInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !scrapeBtn.disabled) {
        handleScrape();
    }
});

apiKeyInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !scrapeBtn.disabled) {
        handleScrape();
    }
});

/**
 * Toggle password visibility
 */
function togglePasswordVisibility() {
    const isPassword = apiKeyInput.type === "password";
    apiKeyInput.type = isPassword ? "text" : "password";
    togglePasswordBtn.textContent = isPassword ? "🙈" : "👁️";
}

/**
 * Update character count for query
 */
function updateCharCount() {
    const length = queryInput.value.length;
    charCountEl.textContent = `${length}/500 characters`;
    charCountEl.style.color = length > 400 ? "var(--warning-color)" : "var(--text-light)";
}

/**
 * Handle scrape button click
 */
async function handleScrape() {
    const apiKey = apiKeyInput.value.trim();
    const query = queryInput.value.trim();

    // Validation
    if (!apiKey) {
        showError("Please enter your Firecrawl API key");
        apiKeyInput.focus();
        return;
    }

    if (!query) {
        showError("Please enter a search query");
        queryInput.focus();
        return;
    }

    // Disable button and show loading state
    scrapeBtn.disabled = true;
    document.querySelector(".btn-text").classList.add("hidden");
    document.querySelector(".btn-loader").classList.add("active");

    try {
        const response = await fetch("/api/scrape", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                query: query,
                api_key: apiKey,
            }),
        });

        const data = await response.json();

        if (response.ok && data.success) {
            displayResults(data);
            lastScrapedData = data;
        } else {
            showError(data.error || "Failed to scrape PAA questions");
        }
    } catch (error) {
        showError(`Network error: ${error.message}`);
    } finally {
        // Re-enable button and hide loading state
        scrapeBtn.disabled = false;
        document.querySelector(".btn-text").classList.remove("hidden");
        document.querySelector(".btn-loader").classList.remove("active");
    }
}

/**
 * Display results in the UI
 */
function displayResults(data) {
    // Show results section
    emptyState.style.display = "none";
    resultsSection.style.display = "block";

    // Display query
    resultQueryEl.textContent = data.query;

    // Clear previous messages
    statusMessageEl.style.display = "none";
    errorMessageEl.style.display = "none";
    questionsContainerEl.style.display = "none";

    // Show status message
    if (data.message) {
        statusMessageEl.textContent = data.message;
        statusMessageEl.style.display = "block";
    }

    // Display questions if found
    if (data.paa_questions && data.paa_questions.length > 0) {
        questionsListEl.innerHTML = "";

        data.paa_questions.forEach((item, index) => {
            const questionEl = document.createElement("div");
            questionEl.className = "question-item";
            questionEl.innerHTML = `
                <span class="question-number">${index + 1}.</span>
                <span class="question-text">${escapeHtml(item.question)}</span>
            `;
            questionsListEl.appendChild(questionEl);
        });

        questionsContainerEl.style.display = "block";
    } else {
        questionsContainerEl.style.display = "none";
        if (!statusMessageEl.textContent) {
            statusMessageEl.textContent = "No PAA questions found for this query";
            statusMessageEl.style.display = "block";
        }
    }

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
}

/**
 * Show error message
 */
function showError(message) {
    emptyState.style.display = "none";
    resultsSection.style.display = "block";
    errorMessageEl.textContent = message;
    errorMessageEl.style.display = "block";
    statusMessageEl.style.display = "none";
    questionsContainerEl.style.display = "none";
    resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
}

/**
 * Close results section
 */
function closeResults() {
    resultsSection.style.display = "none";
    emptyState.style.display = "block";
    queryInput.focus();
}

/**
 * Export results as JSON file
 */
function exportAsJson() {
    if (!lastScrapedData) return;

    const dataStr = JSON.stringify(lastScrapedData, null, 2);
    const dataBlob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `paa-results-${Date.now()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

/**
 * Copy JSON results to clipboard
 */
function copyToClipboard() {
    if (!lastScrapedData) return;

    const dataStr = JSON.stringify(lastScrapedData, null, 2);
    navigator.clipboard.writeText(dataStr).then(() => {
        const originalText = copyJsonBtn.textContent;
        copyJsonBtn.textContent = "✓ Copied!";
        setTimeout(() => {
            copyJsonBtn.textContent = originalText;
        }, 2000);
    }).catch(() => {
        alert("Failed to copy to clipboard");
    });
}

/**
 * Escape HTML special characters
 */
function escapeHtml(text) {
    const map = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;",
    };
    return text.replace(/[&<>"']/g, (m) => map[m]);
}

// Focus on API key input on page load
window.addEventListener("load", () => {
    apiKeyInput.focus();
});
