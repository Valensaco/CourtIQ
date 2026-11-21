# CourtIQ

Ask questions about a tennis club in plain English. Claude turns each question into a SQL query, runs it on the club database, and explains the answer.

**Live demo:** https://court-iq-nfhe.vercel.app

## What it does
- Chat assistant: "Which coaches generate the most revenue?" returns the answer, the SQL used, and the result table.
- Admin panel: browse members, courts, coaches and bookings.
- Demo limit of 5 questions per hour per visitor.

## How it works
1. The React front end sends the question to the Flask API.
2. Claude writes a SQL query from the database schema.
3. The API runs it on SQLite (read-only, a single SELECT only).
4. Claude turns the rows into a plain-English answer.

## Tech
Python, Flask, React, SQLite, Claude API (`claude-sonnet-5-5`).

## Data
The database holds generated sample data (members, courts, coaches, bookings). It is not real club data.

## Run it yourself
Backend:
```
cd backend
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key
python app.py
```
Frontend:
```
cd frontend
npm install
REACT_APP_API_URL=http://localhost:5000 npm start
```
(The backend listens on port 10000 by default. Set `PORT=5000` or point `REACT_APP_API_URL` at it.)
