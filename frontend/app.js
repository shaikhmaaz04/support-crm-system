const API_BASE_URL = '/api';

// Formatting Utilities
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

function getStatusBadge(status) {
    if (status === 'Open') return '<span class="bg-emerald-100 text-emerald-700 border border-emerald-200 px-2.5 py-0.5 rounded-full text-xs font-medium">Open</span>';
    if (status === 'In Progress') return '<span class="bg-amber-100 text-amber-700 border border-amber-200 px-2.5 py-0.5 rounded-full text-xs font-medium">In Progress</span>';
    if (status === 'Closed') return '<span class="bg-slate-100 text-slate-700 border border-slate-200 px-2.5 py-0.5 rounded-full text-xs font-medium">Closed</span>';
    return `<span class="bg-gray-100 text-gray-800 px-2.5 py-0.5 rounded-full text-xs font-medium">${status}</span>`;
}

// -----------------------------------------------------
// INIT ROUTER (Runs code based on current page)
// -----------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('ticketsTableBody')) initDashboard();
    if (document.getElementById('createTicketForm')) initCreate();
    if (document.getElementById('ticketDetailContainer')) initDetail();
});

// -----------------------------------------------------
// PAGE: DASHBOARD (Home)
// -----------------------------------------------------
async function initDashboard() {
    const loadTickets = async () => {
        const searchVal = document.getElementById('searchInput').value;
        const statusVal = document.getElementById('statusFilter').value;
        
        let query = '?';
        if (searchVal) query += `search=${encodeURIComponent(searchVal)}&`;
        if (statusVal) query += `status=${encodeURIComponent(statusVal)}`;

        try {
            const res = await fetch(`${API_BASE_URL}/tickets${query}`);
            const tickets = await res.json();
            const tbody = document.getElementById('ticketsTableBody');
            tbody.innerHTML = '';

            if (tickets.length === 0) {
                tbody.innerHTML = `<tr><td colspan="6" class="px-6 py-12 text-center text-slate-500">
                    <svg class="mx-auto h-12 w-12 text-slate-300 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                    No tickets found.
                </td></tr>`;
                return;
            }

            tickets.forEach(t => {
                tbody.innerHTML += `
                    <tr class="hover:bg-slate-50 transition">
                        <td class="px-6 py-4 whitespace-nowrap text-sm font-mono text-blue-600 font-medium">${t.ticket_id}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-900 font-medium">${t.customer_name}</td>
                        <td class="px-6 py-4 text-sm text-slate-600 truncate max-w-[200px]">${t.subject}</td>
                        <td class="px-6 py-4 whitespace-nowrap">${getStatusBadge(t.status)}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-500">${formatDate(t.created_at)}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <a href="ticket.html?id=${t.ticket_id}" class="text-blue-600 hover:text-blue-900">View &rarr;</a>
                        </td>
                    </tr>
                `;
            });
        } catch (err) {
            console.error(err);
        }
    };

    loadTickets();
    document.getElementById('searchInput').addEventListener('input', loadTickets);
    document.getElementById('statusFilter').addEventListener('change', loadTickets);
}

// -----------------------------------------------------
// PAGE: CREATE TICKET
// -----------------------------------------------------
function initCreate() {
    document.getElementById('createTicketForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const payload = {
            customer_name: document.getElementById('customer_name').value,
            customer_email: document.getElementById('customer_email').value,
            subject: document.getElementById('subject').value,
            description: document.getElementById('description').value,
        };

        const btn = e.target.querySelector('button');
        btn.textContent = 'Submitting...'; btn.disabled = true;

        try {
            const res = await fetch(`${API_BASE_URL}/tickets`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (res.ok) window.location.href = 'index.html';
        } catch (err) {
            alert('Failed to create ticket.');
            btn.textContent = 'Submit Ticket'; btn.disabled = false;
        }
    });
}

// -----------------------------------------------------
// PAGE: TICKET DETAIL & UPDATE
// -----------------------------------------------------
async function initDetail() {
    const urlParams = new URLSearchParams(window.location.search);
    const ticketId = urlParams.get('id');
    
    if (!ticketId) { document.body.innerHTML = 'Invalid Ticket ID'; return; }

    const fetchDetail = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/tickets/${ticketId}`);
            if (!res.ok) throw new Error('Not found');
            const t = await res.json();

            // Populate DOM
            document.getElementById('header-status').innerHTML = getStatusBadge(t.status);
            document.getElementById('detail-id').textContent = t.ticket_id;
            document.getElementById('detail-subject').textContent = t.subject;
            document.getElementById('detail-name').textContent = t.customer_name;
            document.getElementById('detail-email').textContent = t.customer_email;
            document.getElementById('detail-date').textContent = formatDate(t.created_at);
            document.getElementById('detail-desc').textContent = t.description;
            document.getElementById('update-status').value = t.status;

            // Populate Notes
            const notesDiv = document.getElementById('notesList');
            notesDiv.innerHTML = '';
            if (t.notes.length === 0) {
                notesDiv.innerHTML = '<p class="text-sm text-slate-500 italic">No activity yet.</p>';
            } else {
                t.notes.forEach(note => {
                    notesDiv.innerHTML += `
                        <div class="bg-slate-50 p-4 rounded-lg border border-slate-100">
                            <div class="text-xs text-slate-400 mb-2">${formatDate(note.created_at)}</div>
                            <p class="text-sm text-slate-700 whitespace-pre-wrap">${note.note_text}</p>
                        </div>
                    `;
                });
            }
        } catch (err) {
            document.getElementById('ticketDetailContainer').innerHTML = '<p class="text-red-500">Ticket not found.</p>';
        }
    };

    await fetchDetail();

    // Handle AI Summarize
    const btnSummarize = document.getElementById('btn-summarize');
    if (btnSummarize) {
        btnSummarize.addEventListener('click', async () => {
            const resultBox = document.getElementById('ai-summary-result');
            
            btnSummarize.textContent = 'Summarizing...';
            btnSummarize.disabled = true;
            resultBox.classList.remove('hidden');
            resultBox.textContent = '🤖 Reading ticket context and generating summary...';

            try {
                const res = await fetch(`${API_BASE_URL}/tickets/${ticketId}/summary`);
                if (!res.ok) throw new Error('AI generation failed');
                const data = await res.json();
                
                // Set the summary text
                resultBox.innerHTML = `${data.summary}`;
            } catch (err) {
                resultBox.textContent = '❌ Failed to generate AI summary. Please try again later.';
            } finally {
                btnSummarize.textContent = 'Generate Summary';
                btnSummarize.disabled = false;
            }
        });
    }

    // Handle Update Submission
    document.getElementById('updateTicketForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const status = document.getElementById('update-status').value;
        const noteText = document.getElementById('update-note').value;

        const payload = { status: status };
        if (noteText.trim() !== '') payload.notes = noteText;

        const btn = e.target.querySelector('button');
        const originalText = btn.textContent;
        btn.textContent = 'Saving...'; btn.disabled = true;

        try {
            await fetch(`${API_BASE_URL}/tickets/${ticketId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            document.getElementById('update-note').value = ''; // Clear note box
            await fetchDetail(); // Refresh data
        } catch (err) {
            alert('Failed to update ticket.');
        } finally {
            btn.textContent = originalText; btn.disabled = false;
        }
    });
}