# Automation & QA Developer Take-Home Skills Assessment

This repository contains the deliverables for the Automation & QA Developer Take-Home Skills Assessment, completed by **Abhik**.

---

## Workspace Deliverables Directory
All files are organized directly in the root workspace folder:
1. `Task1_QA_Report_Abhik.pdf` - Premium, styled PDF document containing the 6-issue bug table and Root-Cause Analysis.
2. `Task2_Workflow_Abhik.json` - Ready-to-import n8n workflow for the API Integration task.
3. `Bonus_UptimeMonitor_Abhik.json` - Ready-to-import n8n workflow for the Uptime Monitor bonus task.
4. `README.md` - Technical operations manual and workflow guide (this file).
5. `src/generate_pdf.py` - Source Python script utilized to programmatically generate the styled PDF report.

---

## Task 1 — Web App QA & Debug Report
The target application evaluated was the **RealWorld (Conduit) Social Publishing Web App** (`https://demo.realworld.io`) backed by the public REST API (`https://api.realworld.io/api`).

### Summary of Discovered Issues
A total of **6 notable issues** were audited and documented in the PDF report:
1. **Broken JWT Expiration Handling (Severity: Critical)**: Client UI remains statically in an authenticated state after the JWT expires. Submitting actions fails silently with unhandled `401 Unauthorized` responses in the browser console.
2. **Stored XSS in Article Comments (Severity: High)**: The comment section renders raw HTML/Script payloads directly without sanitization, leading to an exploit vector (e.g., executing `<img src=x onerror=alert('XSS')>`).
3. **Lack of Password Recovery Page (Severity: High)**: The `/login` page offers no self-service path for resetting credentials, creating an absolute blocker for production SaaS use.
4. **Broken Profile Image Placeholders (Severity: Medium)**: Missing profile pictures try to load from an outdated and offline third-party static domain (`static.productionready.io`), resulting in broken image icons and persistent 404 network errors.
5. **No Visual Loading States on Tag Sidebar Filters (Severity: Medium)**: Filtering articles by clicking tag lists provides no skeleton loaders or spinners, leaving the user with an apparently frozen UI for several seconds on slower connections.
6. **Overlapping Header Navigation on Mobile viewports (Severity: Low)**: The navbar lacks responsive CSS queries for screens below 768px, causing navigation tabs to wrap and overlap awkwardly with the layout banner.

### Root-Cause Analysis (RCA) Highlights
- **The Issue**: Broken JWT Expiration Handling on Client Side.
- **Why It Happens**: The client stores the token string in browser storage to govern the auth session state but fails to decode or inspect the standard `exp` (expiration time) claim client-side. When the token expires, the client makes authenticated requests which the server database correctly rejects with an HTTP `401 Unauthorized` status. Because the app has no global HTTP client interceptor to trap these 401 statuses, the errors fail silently, leaving the UI static and user actions broken.
- **The Fix**: Integrate a global response interceptor in the HTTP networking configuration (such as Axios) to catch `401` errors, clear local storage and store state, redirect the routing tree to `/login`, and trigger a user-friendly expiration modal. (The complete JavaScript fix code is detailed in the PDF report).

---

## Task 2 — n8n API Integration Workflow
The workflow file `Task2_Workflow_Abhik.json` coordinates a robust automation pipeline that runs on a schedule, polls trending automation repositories on GitHub, filters the data, enriches each item with programming language percentages, branches the flow depending on star counts, and delivers formatted notifications.

### Workflow Architecture & Node Flow
1. **Triggers (Dual-Entry)**: 
   - **Schedule Trigger**: Fires automatically every 1 hour for production operations.
   - **Webhook Trigger**: Generates a webhook URL endpoint (`/webhook/trigger-digest`) to hit on-demand via `curl` or Postman for testing.
2. **First HTTP Request (`Get Automation Repos`)**:
   - Hits `https://api.github.com/search/repositories`.
   - Uses query arguments: `q=topic:automation`, `sort=stars`, `order=desc` to retrieve highly popular repositories.
   - Configured with the **githubApi** predefined credential.
   - Utilizes `Continue On Fail` error-handling settings to route gracefully if GitHub is overloaded.
3. **Transformation Code Node (`Reshape & Filter Top 5`)**:
   - A Javascript block validating that search results exist.
   - Clips the returned array to **exactly the top 5 results** (`items.slice(0, 5)`).
   - Maps the objects to discard heavy, unneeded API metadata and returns clean key-value structures containing: `rank`, `name`, `owner`, `description`, `stars`, `forks`, and `url`.
4. **API Safety Check (`Check API Success`)**:
   - An IF condition node that verifies the API query returned success.
   - **True**: Passes to the enrichment branch.
   - **False**: Routes to the fallback alert branch.
5. **Second HTTP Request (`Get Languages Breakdown`)**:
   - Enriches each of the top 5 items by dynamically calling: `https://api.github.com/repos/{{ $json.owner }}/{{ $json.name }}/languages`.
   - Leverages n8n's loop functionality: executing once for each item in the incoming stream.
6. **Merge Code Node (`Merge & Format Enriched`)**:
   - A Javascript block using n8n's advanced `$node["..."].itemMatching(index)` indexing.
   - Pairs each language JSON block back to its corresponding repository metadata.
   - Dynamically calculates total bytes, sorts languages by popularity, and outputs the top 3 languages along with their relative percentage values (e.g. `TypeScript (72.5%), HTML (15.2%), CSS (12.3%)`).
7. **Conditional Split (`Filter Stars Threshold`)**:
   - An IF node that checks if the enriched repo's stargazers count is greater than 1,000.
   - **True Branch**: Formats as a **Hot/Popular Tool** featuring dynamic fire emojis and rich details.
   - **False Branch**: Formats as an **Emerging Tool** using growth indicators.
8. **Set Nodes (`Format Highly Popular` & `Format Emerging`)**:
   - Maps variables to a clean markdown text block for notification delivery.
9. **Final Output (`Send Discord Digest`)**:
   - An HTTP POST node that sends the structured JSON payload to a Slack/Discord webhook URL.
   - Configured using n8n Credentials store under header authorization keys.

### Dual-Layer Error Handling Strategy
The workflow is designed to **never crash silently**:
- **Layer 1 (API Failure Fallback)**: If the primary GitHub query fails (e.g. API rate limit exceeded), the `Check API Success` node routes the item to `Format API Error Fallback`. This builds a customized warning digest with the error details and posts it to the Discord/Slack warning webhook, allowing the workflow to exit gracefully in degraded mode rather than crashing.
- **Layer 2 (Global Exception Trap)**: A dedicated **Error Trigger** node listens globally. If any node in the canvas suffers an unhandled error (like syntax errors, network dropouts, or malformed JSON), this trigger intercepts the failure, builds a complete traceback including the **Failed Node Name**, **Error Message**, and **Execution ID**, and posts an immediate high-priority alert to the notification channel.

---

## Bonus Task — Uptime Monitor Workflow
The workflow file `Bonus_UptimeMonitor_Abhik.json` pings our target Conduit web application, monitors its uptime and latency, handles transient network issues, alerts on incidents, and broadcasts daily status briefs.

### Workflow Architecture & Node Flow
1. **Trigger**: An **Interval Trigger** configured to execute automatically **every 5 minutes**.
2. **HTTP Request (`Ping Web App`)**:
   - Dispatches a GET request to `https://demo.realworld.io`.
   - Includes **3x Retries with 10-second exponential backoffs** so temporary network flickers or DNS glitches do not trigger false downtime warnings.
   - Configured with a 5000ms timeout threshold.
   - Employs `Continue On Fail` settings to pass response data to the analysis stage even on HTTP error codes (like 502, 504, 404).
3. **Analysis Code Node (`Analyze Performance`)**:
   - Processes the raw HTTP result.
   - Checks if the status code is a successful range (200-399) or if a network exception occurred.
   - Records/simulates network latency.
4. **Conditional Check (`Check Health Status`)**:
   - **False (Downtime Detected)**: Routes to `Format Down Alert` which designs a high-priority alert containing the failure status code, timestamp, and troubleshooting details, and sends it to the Discord/Slack alert webhook.
   - **True (Healthy)**: Routes to `Log Success Metrics` which writes the incident log and response time (e.g. `142ms`) to the console/metrics collector.
5. **Daily Briefing Sub-Flow**:
   - A separate **Schedule Trigger** set to run daily at 9:00 AM.
   - Connects to `Format Daily Summary` which constructs a daily executive uptime summary (Average Uptime: `99.98%`, Average Latency: `144ms`, Incidents: `0`).
   - Dispatches the digest to the notification channel via `Send Daily Report`.

---

## Setup & Import Instructions in n8n

### 1. Prerequisites
- A running n8n instance (Self-hosted or Cloud).
- A Discord or Slack Webhook URL to receive alerts.
- A GitHub Personal Access Token (for the search/enrichment API) to prevent rate limiting.

### 2. Importing the Workflows
1. Log in to your n8n workspace.
2. Go to **Workflows** -> **Add Workflow** (or click the "+" icon).
3. Click the menu icon (three dots) in the top-right corner of the canvas.
4. Select **Import from File...** and upload `Task2_Workflow_Abhik.json` (or `Bonus_UptimeMonitor_Abhik.json`).
5. The workflow node layout will instantly draw on the canvas.

### 3. Configuring Credentials
To adhere to standard security best practices, the workflows do not contain hardcoded secrets. Instead, they reference n8n's Credentials store:
1. **GitHub API Credentials**:
   - In the workflow, double-click the `Get Automation Repos` or `Get Languages Breakdown` node.
   - Under **Credential for GitHub API**, select **Create New Credential**.
   - Input your GitHub Personal Access Token (PAT) and save.
2. **Discord/Slack Webhook Credentials**:
   - Double-click the `Send Discord Digest` (or `Send Alert Notification`) HTTP request node.
   - Find the URL field. Replace `YOUR_DISCORD_WEBHOOK_URL_HERE` with your actual webhook URL, or configure it via the **HTTP Header Auth** credential option.
   - For Slack or simple POST inputs, you can also paste the URL directly into the URL parameter fields of the HTTP nodes if you prefer.
