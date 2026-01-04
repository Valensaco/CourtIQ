import sqlite3

conn = sqlite3.connect('courtiq.db')
cursor = conn.cursor()

# Q1: Which members have the highest cancellation rate in the last 30 days?
print("Q1: Members with highest cancellation rate (last 30 days)\n")
cursor.execute('''
    SELECT 
        m.member_id,
        m.name,
        COUNT(CASE WHEN b.status = 'cancelled' THEN 1 END) as cancellations,
        COUNT(*) as total_bookings,
        ROUND(100.0 * COUNT(CASE WHEN b.status = 'cancelled' THEN 1 END) / COUNT(*), 2) as cancellation_rate_pct
    FROM members m
    JOIN bookings b ON m.member_id = b.member_id
    WHERE b.booking_date >= date('2026-01-02', '-30 days')
    GROUP BY m.member_id, m.name
    HAVING COUNT(*) >= 2
    ORDER BY cancellation_rate_pct DESC
    LIMIT 5
''')

for row in cursor.fetchall():
    print(f"  {row[1]}: {row[2]} cancellations / {row[3]} bookings = {row[4]}%")

conn.close()
