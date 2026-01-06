import sqlite3
import random
from datetime import datetime, timedelta

conn = sqlite3.connect('courtiq.db')
cursor = conn.cursor()

first_names = ['Emma', 'Liam', 'Olivia', 'Noah', 'Ava', 'Ethan', 'Sophia', 'Mason', 'Isabella', 'William']
last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
tiers = ['Premium', 'Standard', 'Junior']
lesson_types = ['private', 'semi-private', 'group', 'court-rental']

cursor.execute('SELECT MAX(member_id) FROM members')
start_member_id = (cursor.fetchone()[0] or 0) + 1

cursor.execute('SELECT MAX(booking_id) FROM bookings')
start_booking_id = (cursor.fetchone()[0] or 0) + 1

print("Adding 80 members...")
members_data = []
for i in range(80):
    mid = start_member_id + i
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    email = f"{name.lower().replace(' ', '.')}.{mid}@email.com"
    phone = f"555-{random.randint(1000, 9999)}"
    tier = random.choice(tiers)
    days_ago = random.randint(0, 365)
    join_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
    members_data.append((mid, name, email, phone, tier, join_date, 'active'))

cursor.executemany('INSERT INTO members VALUES (?,?,?,?,?,?,?)', members_data)

cursor.execute('SELECT member_id FROM members')
all_members = [r[0] for r in cursor.fetchall()]

cursor.execute('SELECT coach_id FROM coaches')
all_coaches = [r[0] for r in cursor.fetchall()]

cursor.execute('SELECT court_id FROM courts')
all_courts = [r[0] for r in cursor.fetchall()]

print("Generating bookings...")
bid = start_booking_id
bookings_data = []
start_date = datetime.now() - timedelta(days=180)

for day in range(180):
    current_date = start_date + timedelta(days=day)
    num_bookings = random.randint(2, 8)
    for _ in range(num_bookings):
        mid = random.choice(all_members)
        cid = random.choice(all_coaches)
        ctid = random.choice(all_courts)
        lt = random.choice(lesson_types)
        h = random.randint(8, 19)
        p = random.randint(35, 90)
        st = random.choice(['completed', 'cancelled', 'completed', 'completed'])
        cr = 'weather' if st == 'cancelled' and random.random() > 0.5 else None
        bdate = current_date.strftime('%Y-%m-%d')
        bookings_data.append((bid, mid, cid, ctid, lt, bdate, f"{h:02d}:00", f"{h+1:02d}:00", 60, p, st, cr, bdate))
        bid += 1

sql = 'INSERT INTO bookings VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)'
cursor.executemany(sql, bookings_data)
conn.commit()
conn.close()

print(f"Done! Added {len(members_data)} members and {len(bookings_data)} bookings")