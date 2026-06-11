# 🚀 Datastraw Support CRM

A fast, fully functional Customer Support CRM built for the Datastraw Engineering Assessment. This application features a modern UI, a lightweight database, and LLM-powered automations (Agentic Workflows) to accelerate support workflows.

### 🔗 Links
* **Live Application:** https://support-crm-system.up.railway.app/
* **Demo Video:** 

---

## ✨ Features

### Core Requirements (Fully Met)
1. **Create Tickets:** Auto-generated IDs (e.g., TKT-123456) with customer details and issue descriptions.
2. **List & View:** Clean dashboard with a responsive, easy-to-read table.
3. **Search:** Real-time, as-you-type search across names, IDs, emails, subjects, and descriptions.
4. **Filter:** Filter tickets instantly by Status (Open, In Progress, Closed).
5. **Update & Notes:** Detailed ticket view to change statuses and append internal activity notes.

### 🤖 LLM-Powered Automations (Above & Beyond)
Powered by **Groq (Llama-3.1-8b-instant)**, this CRM includes 3 specific AI integrations designed to solve real-world support bottlenecks:
1. **AI Spam Automation (Background):** Detects gibberish or spam during ticket creation and instantly auto-closes the ticket, saving human agents from manual cleanup.
2. **AI Triage Workflow (Background):** Analyzes legitimate tickets to automatically determine and log the **Category**, **Priority**, and **Customer Sentiment** as an internal note.
3. **AI Ticket Summarizer (On-Demand):** A "Generate Summary" button on the ticket detail page that reads the original issue + all subsequent agent updates, outputting a crisp 2-sentence TL;DR + current status for quick context.

---

## 🛠️ Technology Stack

* **Backend:** Python + FastAPI
* **Database:** SQLite3 (Strictly adhering to the 2-table constraint: `tickets` and `notes`)
* **Frontend:** Vanilla JS + HTML5 + Tailwind CSS (via CDN)
* **AI Integration:** Groq API 
* **Package Manager:** `uv` (for ultra-fast dependency resolution)
* **Deployment:** Railway.app (via `Procfile`)

---

## 🏗️ Architectural Decisions

* **LLM Automations vs. "AI Agents":** While the industry loosely uses the term "Agents", I consciously designed these features as *LLM-Powered Automations* and *Agentic Workflows*. They utilize LLMs for classification and summarization, and trigger autonomous database actions (like auto-closing spam), but operate within strict, predictable code paths rather than open-ended reasoning loops.
* **Vanilla JS over a Frontend Framework:** To fulfill the requirement of "shipping working code over perfect code," Vanilla JS was selected. This eliminates complex build steps, avoids CORS issues by allowing FastAPI to serve the static frontend files directly via `StaticFiles`, and simplifies PaaS deployment.
* **Single Deployment:** The frontend and backend run seamlessly as a single full-stack application on a single port.
* **Schema Simplicity:** Kept strictly to the requested 2 tables utilizing Foreign Keys and cascading deletes. AI metadata (sentiment, priority) is injected cleanly as System Notes rather than over-engineering new database columns.
* **Authentication Skipped (MVP Focus):** As per the assignment FAQ, basic authentication was intentionally skipped to ensure a frictionless testing experience for evaluators. Development time was instead invested into delivering high-value AI business logic.

---

## 📂 Project Structure

```text
support-crm-system/
│
├── backend/
│   ├── database.py       # SQLite connection and schema creation
│   ├── main.py           # FastAPI server, REST endpoints, and LLM workflows
│   └── models.py         # Pydantic models for request validation
│
├── frontend/
│   ├── app.js            # Vanilla JS logic & API fetching
│   ├── index.html        # CRM Dashboard
│   ├── create.html       # Ticket Creation Form
│   └── ticket.html       # Ticket Details & AI Summary View
│
├── .env.example          # Template for environment variables
├── .gitignore            # Git ignore rules (protects DB and keys)
├── Procfile              # Deployment command for Railway
├── pyproject.toml        # Project metadata and uv dependencies
├── requirements.txt      # Python dependencies (exported via uv)
└── README.md             # Project documentation
```

---

## 💻 Local Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/shaikhmaaz04/support-crm-system.git
   cd support-crm-system
   ```

2. **Environment Variables:**
   Create a `.env` file in the root directory based on `.env.example`:
   ```env
   GROQ_API_KEY=your_actual_groq_api_key_here
   ```

3. **Install Dependencies & Run:**
   This project uses `uv` for lightning-fast dependency management, but a `requirements.txt` is also provided for standard setups.

   **Method A: Using `uv` (Recommended)**
   ```bash
   # Automatically creates a virtual environment and installs dependencies from pyproject.toml
   uv sync
   
   # Run the application
   uv run uvicorn backend.main:app --reload
   ```

   **Method B: Using standard `pip`**
   ```bash
   # Create a virtual environment
   python -m venv .venv
   
   # Activate on Windows:
   .\.venv\Scripts\activate
   # Activate on Mac/Linux:
   source .venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Run the application
   uvicorn backend.main:app --reload
   ```

4. **Access the App:**
   * **Web App:** Open `http://127.0.0.1:8000` in your browser.
   * **Interactive API Docs:** Open `http://127.0.0.1:8000/docs` to view the auto-generated Swagger UI.
---

*Developed with 💡 by Maaz Shaikh for the Datastraw Assessment.*
