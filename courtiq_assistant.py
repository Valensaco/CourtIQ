"""
CourtIQ AI Assistant
Converts natural language questions into SQL queries and returns answers
"""

import sqlite3
import os
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Anthropic client
client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# Database schema for context
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


def get_sql_from_question(question):
    """
    Use Claude to convert a natural language question into SQL
    """
    prompt = f"""You are a SQL expert for a tennis club database. Given the following schema and a user question, generate ONLY the SQL query needed to answer it. Do not include any explanation, markdown formatting, or additional text.

{SCHEMA}

User Question: {question}

Generate a valid SQLite query that answers this question. Return ONLY the SQL query, nothing else."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    sql_query = message.content[0].text.strip()

    # Remove markdown code blocks if present
    if sql_query.startswith("```"):
        sql_query = sql_query.split("\n", 1)[1]
        sql_query = sql_query.rsplit("```", 1)[0]

    return sql_query.strip()


def execute_query(sql_query):
    """
    Execute SQL query against the database
    """
    try:
        conn = sqlite3.connect('courtiq.db')
        cursor = conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        conn.close()
        return results, column_names
    except Exception as e:
        return None, str(e)


def format_results(results, column_names):
    """
    Format query results into a readable string
    """
    if not results:
        return "No results found."

    # Create header
    output = "\n" + " | ".join(column_names) + "\n"
    output += "-" * (len(output) - 2) + "\n"

    # Add rows
    for row in results:
        output += " | ".join(str(val) if val is not None else "NULL" for val in row) + "\n"

    return output


def get_natural_language_answer(question, sql_query, results, column_names):
    """
    Use Claude to generate a natural language answer from the SQL results
    """
    results_text = format_results(results, column_names)

    prompt = f"""You are a helpful assistant for a tennis club manager. Based on the SQL query results below, provide a clear, concise answer to the user's question in natural language.

User Question: {question}

SQL Query Used: {sql_query}

Results:
{results_text}

Provide a clear, conversational answer that directly addresses the question. Include specific numbers and names from the results."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text.strip()


def ask_question(question):
    """
    Main function to process a question end-to-end
    """
    print(f"\n{'=' * 60}")
    print(f"QUESTION: {question}")
    print(f"{'=' * 60}")

    # Step 1: Generate SQL
    print("\n[1] Generating SQL query...")
    sql_query = get_sql_from_question(question)
    print(f"Generated SQL:\n{sql_query}")

    # Step 2: Execute SQL
    print("\n[2] Executing query...")
    results, column_names = execute_query(sql_query)

    if results is None:
        print(f"❌ Error executing query: {column_names}")
        return

    print(f"✓ Query executed successfully. Found {len(results)} result(s).")

    # Step 3: Generate natural language answer
    print("\n[3] Generating answer...")
    answer = get_natural_language_answer(question, sql_query, results, column_names)

    print(f"\n{'=' * 60}")
    print("ANSWER:")
    print(f"{'=' * 60}")
    print(answer)
    print(f"{'=' * 60}\n")


def main():
    """
    Interactive loop for asking questions
    """
    print("\n" + "=" * 60)
    print("CourtIQ AI Assistant")
    print("Ask questions about your tennis club in natural language")
    print("Type 'quit' to exit")
    print("=" * 60 + "\n")

    # Example questions
    print("Example questions you can ask:")
    print("  • Which members have the highest cancellation rate?")
    print("  • How much revenue did we lose to weather cancellations in December?")
    print("  • Which coaches generate the most revenue?")
    print("  • Show me the top 5 members by total bookings")
    print()

    while True:
        question = input("Your question: ").strip()

        if question.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye!")
            break

        if not question:
            continue

        try:
            ask_question(question)
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    main()