import os
import json
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env file
load_dotenv()

# Initialize Groq Client
# It automatically picks up the GROQ_API_KEY from your .env file
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Import our database connection and Pydantic models
from backend.database import get_db_connection, init_db
from backend.models import TicketCreate, TicketUpdate

# Initialize database on startup
init_db()

app = FastAPI(title="Datastraw Support CRM API")

# Allow CORS so frontend and backend can communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# ENDPOINT 1: CREATE TICKET (With AI Spam & Triage Automations)
# ---------------------------------------------------------
@app.post("/api/tickets")
def create_ticket(ticket: TicketCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Auto-generate ticket ID
    unique_id = str(uuid.uuid4().hex[:6]).upper()
    ticket_id = f"TKT-{unique_id}"
    
    # Default values before AI analysis
    ai_status = "Open"
    ai_note = None
    
    # --- AI PROCESSING ---
    try:
        prompt = f"""
        Analyze this customer support ticket.
        Subject: {ticket.subject}
        Description: {ticket.description}
        
        Return ONLY a JSON object with these exact keys:
        - "is_spam": boolean (true if it's gibberish like 'asdfg' or obvious spam, else false)
        - "priority": string ("High", "Medium", "Low")
        - "sentiment": string ("Angry", "Neutral", "Happy")
        - "category": string ("Order Issue", "Technical Support", "Billing", "Feature Request", "Other")
        """
        
        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        analysis = json.loads(chat_completion.choices[0].message.content)
        
        if analysis.get("is_spam"):
            ai_status = "Closed"
            ai_note = "🤖 AI Agent: Ticket auto-closed because it was flagged as spam/gibberish."
        else:
            prio = analysis.get("priority", "Medium")
            sent = analysis.get("sentiment", "Neutral")
            cat = analysis.get("category", "Other")
            ai_note = f"🤖 AI Triage: Category is [{cat}]. Priority is [{prio}]. Sentiment is [{sent}]."
            
    except Exception as e:
        print(f"AI Processing Failed: {e}")
        pass
    
    # Insert ticket into database
    cursor.execute('''
        INSERT INTO tickets (ticket_id, customer_name, customer_email, subject, description, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (ticket_id, ticket.customer_name, ticket.customer_email, ticket.subject, ticket.description, ai_status))
    
    # If AI generated a note, insert it into the notes table
    if ai_note:
        cursor.execute("INSERT INTO notes (ticket_id, note_text) VALUES (?, ?)", (ticket_id, ai_note))
    
    conn.commit()
    conn.close()
    
    return {"ticket_id": ticket_id, "created_at": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}

# ---------------------------------------------------------
# ENDPOINT 2: LIST & SEARCH TICKETS
# ---------------------------------------------------------
@app.get("/api/tickets")
def get_tickets(
    status: Optional[str] = Query(None, description="Filter by Open, In Progress, Closed"),
    search: Optional[str] = Query(None, description="Search by name, email, ID, or subject")
):
    conn = get_db_connection()
    
    query = "SELECT ticket_id, customer_name, subject, status, created_at FROM tickets WHERE 1=1"
    params = []
    
    if status:
        query += " AND status = ?"
        params.append(status)
        
    if search:
        # Search across all required fields
        query += " AND (customer_name LIKE ? OR ticket_id LIKE ? OR customer_email LIKE ? OR subject LIKE ? OR description LIKE ?)"
        search_term = f"%{search}%"
        params.extend([search_term, search_term, search_term, search_term, search_term])
        
    query += " ORDER BY created_at DESC"
    
    cursor = conn.execute(query, params)
    tickets = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return tickets

# ---------------------------------------------------------
# ENDPOINT 3: GET TICKET DETAILS
# ---------------------------------------------------------
@app.get("/api/tickets/{ticket_id}")
def get_ticket_detail(ticket_id: str):
    conn = get_db_connection()
    
    # Get the ticket
    ticket_cursor = conn.execute("SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,))
    ticket = ticket_cursor.fetchone()
    
    if not ticket:
        conn.close()
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    ticket_dict = dict(ticket)
    
    # Get associated notes
    notes_cursor = conn.execute("SELECT note_text, created_at FROM notes WHERE ticket_id = ? ORDER BY created_at DESC", (ticket_id,))
    notes = [dict(row) for row in notes_cursor.fetchall()]
    
    ticket_dict["notes"] = notes
    conn.close()
    
    return ticket_dict

# ---------------------------------------------------------
# ENDPOINT 4: UPDATE TICKET STATUS & ADD NOTE
# ---------------------------------------------------------
@app.put("/api/tickets/{ticket_id}")
def update_ticket(ticket_id: str, update_data: TicketUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Check if ticket exists
    cursor.execute("SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # 2. Update status if provided
    if update_data.status:
        cursor.execute("UPDATE tickets SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE ticket_id = ?", 
                       (update_data.status, ticket_id))
    
    # 3. Add note if provided
    if update_data.notes:
        cursor.execute("INSERT INTO notes (ticket_id, note_text) VALUES (?, ?)", 
                       (ticket_id, update_data.notes))
        # Update timestamp
        cursor.execute("UPDATE tickets SET updated_at = CURRENT_TIMESTAMP WHERE ticket_id = ?", (ticket_id,))
        
    conn.commit()
    conn.close()
    
    return {"success": True, "updated_at": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}

# ---------------------------------------------------------
# ENDPOINT 5: AI TICKET SUMMARIZER (On Demand)
# ---------------------------------------------------------
@app.get("/api/tickets/{ticket_id}/summary")
def get_ticket_summary(ticket_id: str):
    conn = get_db_connection()
    
    ticket = conn.execute("SELECT subject, description, status FROM tickets WHERE ticket_id = ?", (ticket_id,)).fetchone()
    notes = conn.execute("SELECT note_text FROM notes WHERE ticket_id = ?", (ticket_id,)).fetchall()
    conn.close()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    # Combine ticket info, STATUS, and all notes to give the AI context
    context = f"Status: {ticket['status']}\nSubject: {ticket['subject']}\nDescription: {ticket['description']}\n"
    if notes:
        context += "Notes/Updates:\n" + "\n".join([n['note_text'] for n in notes])
        
    try:
        prompt = f"""
        You are an expert support agent. Summarize the following ticket in exactly 2 or 3 clear, professional sentences. 
        You MUST explicitly state the current Status of the ticket in your summary (e.g., "This ticket is currently In Progress...").
        Include the initial problem and any major updates from the notes.
        DO NOT include any conversational filler. Just output the summary directly.
        
        Context:
        {context}
        """
        
        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.3
        )
        return {"summary": chat_completion.choices[0].message.content}
    except Exception as e:
        print(f"Summarizer Failed: {e}")
        raise HTTPException(status_code=500, detail="AI generation failed")

# ---------------------------------------------------------
# HOST FRONTEND FILES
# Must be at the very bottom so it doesn't block /api routes!
# ---------------------------------------------------------
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")