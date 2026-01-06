"""
CourtIQ Flask Backend
Handles API requests from React frontend
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from anthropic import Anthropic
from dotenv import load_dotenv
from collections import defaultdict
from datetime import datetime, timedelta

load_dotenv()

app = Flask(__name__)
CORS(app)

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# Rate limiting
request_tracker = defaultdict(list)
MAX_REQUESTS_PER_IP = 100

SCHEMA = """
Database Schema for CourtIQ (Tennis Club Analytics):

TABLE: members
- member_id (INTEGER, PRIMARY KEY)
- name (TEXT)
- email (TEXT)
- phone (TEXT)
- membership_tier (TEXT: Premium, Standard, Junior)
- join_date (DATE)
- status (TEXT: active, inactive, churned)

TABLE: courts
- court_id (INTEGER, PRIMARY KEY)
- court_name (TEXT)
- surface_type (TEXT: hard, clay, grass)
- indoor (INTEGER: 0 or 1)

TABLE: coaches
- coach_id (INTEGER, PRIMARY KEY)
- name (TEXT)
- specialty (TEXT)
- hourly_rate (REAL)
- weekly_available_hours (INTEGER)

TABLE: bookings
- booking_id (INTEGER, PRIMARY KEY)
- member_id (INTEGER, FOREIGN KEY)
- coach_id (INTEGER, FOREIGN KEY, nullable)
- court_id (INTEGER, FOREIGN KEY)
- lesson_type (TEXT: private, semi-private, group, court-rental)
- booking_date (DATE)
- start_time (TEXT)
- end_time (TEXT)
- duration_minutes (INTEGER)
- price (REAL)
- status (TEXT: completed, cancelled, no-show, scheduled)
- cancellation_reason (TEXT: weather, member-request, coach-unavailable)
- created_at (TEXT)

Current date context: 2026-01-02
"""


def get_sql_from_question(question, conversation_history=None):
    """Convert natural language to SQL using Claude with conversation context"""

    # Build context from conversation history
    # Build context from conversation history
    context = ""
    if conversation_history:
        context = "\n\nRecent conversation for context (maintain same formatting style):\n"
        for msg in conversation_history[-3:]:  # Last 3 exchanges
            if msg.get('question'):
                context += f"User asked: {msg['question']}\n"
            if msg.get('answer'):
                context += f"Assistant answered: {msg['answer'][:300]}...\n"  # Include more of answer to capture format

    prompt = f"""You are a SQL expert for a tennis club database. Generate ONLY the SQL query needed to answer the question. No explanation, no markdown, just the query.

{SCHEMA}
{context}

Current question: {question}

IMPORTANT: If the previous response used a specific format (like a list), maintain that same format for follow-up questions.

Return ONLY the SQL query."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    sql_query = message.content[0].text.strip()

    if sql_query.startswith("```"):
        sql_query = sql_query.split("\n", 1)[1]
        sql_query = sql_query.rsplit("```", 1)[0]

    return sql_query.strip()








def execute_query(sql_query):
    """Execute SQL against database"""
    try:
        conn = sqlite3.connect('courtiq.db')
        cursor = conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        conn.close()
        return results, column_names, None
    except Exception as e:
        return None, None, str(e)

def format_results(results, column_names):
    """Format query results as text"""
    if not results:
        return "No results found."
    
    output = "\n" + " | ".join(column_names) + "\n"
    output += "-" * (len(output) - 2) + "\n"
    
    for row in results:
        output += " | ".join(str(val) if val is not None else "NULL" for 
val in row) + "\n"
    
    return output


def get_natural_language_answer(question, sql_query, results, column_names):
    """Generate natural language answer from results"""
    results_text = format_results(results, column_names)

    prompt = f"""Based on the SQL results, provide a clear answer to the user's question.
    
    IMPORTANT: 
    - Respond in the SAME LANGUAGE the user asked their question in (English, Spanish, etc.).
    - Use plain text only - NO markdown, NO asterisks, NO special formatting
    - Write naturally without bold, italics, or other formatting symbols

User Question: {question}

SQL Query: {sql_query}

Results:
{results_text}

Provide a conversational, natural answer in the user's language. Speak directly and simply - avoid technical phrases. 

If presenting multiple items, format it clearly as a bulleted list with line breaks between items. Use proper spacing to make it easy to read."""


    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text.strip()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})


@app.route('/stats/summary', methods=['GET'])
def get_summary_stats():
    """Get quick summary stats for dashboard cards"""
    try:
        conn = sqlite3.connect('courtiq.db')
        cursor = conn.cursor()

        # Active members
        cursor.execute('SELECT COUNT(*) FROM members WHERE status="active"')
        active_members = cursor.fetchone()[0]

        # Revenue this month
        cursor.execute('''
                       SELECT COALESCE(SUM(price), 0)
                       FROM bookings
                       WHERE status = "completed"
                         AND strftime('%Y-%m', booking_date) = strftime('%Y-%m', 'now')
                       ''')
        revenue_this_month = cursor.fetchone()[0]

        # Bookings today
        cursor.execute('''
                       SELECT COUNT(*)
                       FROM bookings
                       WHERE DATE (booking_date) = DATE ('now')
                       ''')
        bookings_today = cursor.fetchone()[0]

        conn.close()

        return jsonify({
            "active_members": active_members,
            "revenue_this_month": round(revenue_this_month, 2),
            "bookings_today": bookings_today
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/admin/revenue-chart', methods=['GET'])
def get_revenue_chart():
    """Get revenue data for chart with configurable time period"""
    try:
        # Get time period from query parameter (default: 30 days)
        days = request.args.get('days', 30, type=int)

        conn = sqlite3.connect('courtiq.db')
        cursor = conn.cursor()

        cursor.execute('''
                       SELECT
                           DATE (booking_date) as date, SUM (CASE WHEN status='completed' THEN price ELSE 0 END) as revenue
                       FROM bookings
                       WHERE booking_date >= DATE ('now', '-' || ? || ' days')
                       GROUP BY DATE (booking_date)
                       ORDER BY date
                       ''', (days,))

        results = cursor.fetchall()
        conn.close()

        data = [{"date": row[0], "revenue": round(row[1], 2)} for row in results]

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500




@app.route('/ask', methods=['POST'])
def ask_question():
    """Main endpoint for processing questions"""
    try:
        data = request.json
        question = data.get('question', '').strip()
        conversation_history = data.get('history', [])
        # Rate limiting check
        client_ip = request.remote_addr
        now = datetime.now()

        # Clean old requests (older than 1 hour)
        request_tracker[client_ip] = [
            req_time for req_time in request_tracker[client_ip]
            if now - req_time < timedelta(hours=1)
        ]

        # Check if limit exceeded
        if len(request_tracker[client_ip]) >= MAX_REQUESTS_PER_IP:
            return jsonify({
                "question": question,
                "sql": None,
                "answer": "You've reached the demo limit of 5 questions per hour. This helps manage API costs. If you'd like to see more or discuss this project, feel free to connect with me on LinkedIn!",
                "results": None
            })

        # Track this request
        request_tracker[client_ip].append(now)

        if not question:
            return jsonify({"error": "No question provided"}), 400
# check if it's a casual greeting or non-data question
        # Check if it's a casual greeting or non-data question
        casual_keywords = ['hello', 'hi', 'hey', 'thanks', 'thank you', 'bye', 'goodbye']
        question_words = question.lower().split()
        if any(keyword in question_words for keyword in casual_keywords):
            return jsonify({
                "question": question,
                "sql": None,
                "answer": "Hi! I'm here to help you analyze your tennis club data. Try asking questions like: 'Which members have the highest cancellation rate?' or 'How much revenue did we generate last month?'",
                "results": None
            })
        
        # Generate SQL
        sql_query = get_sql_from_question(question, conversation_history)

        # Execute query
        results, column_names, error = execute_query(sql_query)

        if error:
            return jsonify({
                "question": question,
                "sql": None,
                "answer": "I couldn't understand that question. Please ask about members, bookings, coaches, courts, or revenue. For example: 'How many active members do we have?' or 'What's our revenue this month?'",
                "results": None
            })
        
        # Generate answer
        answer = get_natural_language_answer(question, sql_query, results, 
column_names)
        
        return jsonify({
            "question": question,
            "sql": sql_query,
            "answer": answer,
            "results": {
                "columns": column_names,
                "rows": results
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# ADMIN ENDPOINTS - Add these to your app.py file
# ============================================================================

# MEMBERS ENDPOINTS
@app.route('/admin/members', methods=['GET'])
def get_members():
    """Get all members"""
    try:
        conn = sqlite3.connect('courtiq.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM members ORDER BY join_date DESC')
        members = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(members)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/admin/members', methods=['POST'])
def create_member():
    """Create a new member"""
    try:
        data = request.json
        conn = sqlite3.connect('courtiq.db')
        cursor = conn.cursor()
        cursor.execute('''
                       INSERT INTO members (name, email, phone, membership_tier, join_date, status)
                       VALUES (?, ?, ?, ?, ?, ?)
                       ''', (data['name'], data['email'], data.get('phone'), data['membership_tier'],
                             data['join_date'], data.get('status', 'active')))
        conn.commit()
        member_id = cursor.lastrowid
        conn.close()
        return jsonify({"id": member_id, "message": "Member created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/admin/members/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    """Update a member"""
    try:
        data = request.json
        conn = sqlite3.connect('courtiq.db')
        cursor = conn.cursor()
        cursor.execute('''
                       UPDATE members
                       SET name=?,
                           email=?,
                           phone=?,
                           membership_tier=?,
                           status=?
                       WHERE member_id = ?
                       ''', (data['name'], data['email'], data.get('phone'),
                             data['membership_tier'], data['status'], member_id))
        conn.commit()
        conn.close()
        return jsonify({"message": "Member updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/admin/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    """Delete a member"""
    try:
        conn = sqlite3.connect('courtiq.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM members WHERE member_id=?', (member_id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Member deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# COACHES ENDPOINTS
@app.route('/admin/coaches', methods=['GET'])
def get_coaches():
    """Get all coaches"""
    try:
        conn = sqlite3.connect('courtiq.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM coaches')
        coaches = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(coaches)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/admin/coaches', methods=['POST'])
def create_coach():
    """Create a new coach"""
    try:
        data = request.json
        conn = sqlite3.connect('courtiq.db')
        cursor = conn.cursor()
        cursor.execute('''
                       INSERT INTO coaches (name, specialty, hourly_rate, weekly_available_hours)
                       VALUES (?, ?, ?, ?)
                       ''', (data['name'], data['specialty'], data['hourly_rate'],
                             data.get('weekly_available_hours', 40)))
        conn.commit()
        coach_id = cursor.lastrowid
        conn.close()
        return jsonify({"id": coach_id, "message": "Coach created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/admin/coaches/<int:coach_id>', methods=['DELETE'])
def delete_coach(coach_id):
    """Delete a coach"""
    try:
        conn = sqlite3.connect('courtiq.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM coaches WHERE coach_id=?', (coach_id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Coach deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# COURTS ENDPOINTS
@app.route('/admin/courts', methods=['GET'])
def get_courts():
    """Get all courts"""
    try:
        conn = sqlite3.connect('courtiq.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM courts')
        courts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(courts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/admin/courts', methods=['POST'])
def create_court():
    """Create a new court"""
    try:
        data = request.json
        conn = sqlite3.connect('courtiq.db')
        cursor = conn.cursor()
        cursor.execute('''
                       INSERT INTO courts (court_name, surface_type, indoor)
                       VALUES (?, ?, ?)
                       ''', (data['court_name'], data['surface_type'], data.get('indoor', 0)))
        conn.commit()
        court_id = cursor.lastrowid
        conn.close()
        return jsonify({"id": court_id, "message": "Court created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/admin/courts/<int:court_id>', methods=['DELETE'])
def delete_court(court_id):
    """Delete a court"""
    try:
        conn = sqlite3.connect('courtiq.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM courts WHERE court_id=?', (court_id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Court deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# BOOKINGS ENDPOINTS
@app.route('/admin/bookings', methods=['GET'])
def get_bookings():
    """Get all bookings with member and coach names"""
    try:
        conn = sqlite3.connect('courtiq.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
                       SELECT b.*,
                              m.name as member_name,
                              c.name as coach_name,
                              co.court_name
                       FROM bookings b
                                JOIN members m ON b.member_id = m.member_id
                                LEFT JOIN coaches c ON b.coach_id = c.coach_id
                                JOIN courts co ON b.court_id = co.court_id
                       ORDER BY b.booking_date DESC, b.start_time DESC LIMIT 100
                       ''')
        bookings = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(bookings)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/admin/bookings', methods=['POST'])
def create_booking():
    """Create a new booking"""
    try:
        data = request.json
        conn = sqlite3.connect('courtiq.db')
        cursor = conn.cursor()
        cursor.execute('''
                       INSERT INTO bookings (member_id, coach_id, court_id, lesson_type,
                                             booking_date, start_time, end_time, duration_minutes,
                                             price, status, cancellation_reason)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                       ''', (
                           data['member_id'],
                           data.get('coach_id'),
                           data['court_id'],
                           data['lesson_type'],
                           data['booking_date'],
                           data['start_time'],
                           data['end_time'],
                           data['duration_minutes'],
                           data['price'],
                           data.get('status', 'scheduled'),
                           data.get('cancellation_reason')
                       ))
        conn.commit()
        booking_id = cursor.lastrowid
        conn.close()
        return jsonify({"id": booking_id, "message": "Booking created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/admin/bookings/<int:booking_id>', methods=['PUT'])
def update_booking(booking_id):
    """Update a booking (mainly for cancellations)"""
    try:
        data = request.json
        conn = sqlite3.connect('courtiq.db')
        cursor = conn.cursor()
        cursor.execute('''
                       UPDATE bookings
                       SET status=?,
                           cancellation_reason=?
                       WHERE booking_id = ?
                       ''', (data['status'], data.get('cancellation_reason'), booking_id))
        conn.commit()
        conn.close()
        return jsonify({"message": "Booking updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/admin/bookings/<int:booking_id>', methods=['DELETE'])
def delete_booking(booking_id):
    """Delete a booking"""
    try:
        conn = sqlite3.connect('courtiq.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM bookings WHERE booking_id=?', (booking_id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Booking deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# DASHBOARD STATS
@app.route('/admin/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics"""
    try:
        conn = sqlite3.connect('courtiq.db')
        cursor = conn.cursor()

        # Total members
        cursor.execute('SELECT COUNT(*) FROM members WHERE status="active"')
        total_members = cursor.fetchone()[0]

        # Total revenue (completed bookings)
        cursor.execute('SELECT SUM(price) FROM bookings WHERE status="completed"')
        total_revenue = cursor.fetchone()[0] or 0

        # Bookings this month
        cursor.execute('''
                       SELECT COUNT(*)
                       FROM bookings
                       WHERE strftime('%Y-%m', booking_date) = strftime('%Y-%m', 'now')
                       ''')
        bookings_this_month = cursor.fetchone()[0]

        # Revenue this month
        cursor.execute('''
                       SELECT SUM(price)
                       FROM bookings
                       WHERE status = "completed"
                         AND strftime('%Y-%m', booking_date) = strftime('%Y-%m', 'now')
                       ''')
        revenue_this_month = cursor.fetchone()[0] or 0

        conn.close()

        return jsonify({
            "total_members": total_members,
            "total_revenue": round(total_revenue, 2),
            "bookings_this_month": bookings_this_month,
            "revenue_this_month": round(revenue_this_month, 2)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
