"""
CourtIQ Database Setup Script
Creates database, tables, and sample data for tennis club analytics
"""

import sqlite3
from datetime import datetime


def create_database():
    """Create and populate the CourtIQ database"""

    # Connect to database (creates file if it doesn't exist)
    conn = sqlite3.connect('courtiq.db')
    cursor = conn.cursor()

    print("Creating tables...")

    # Create Members table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS members
                   (
                       member_id
                       INTEGER
                       PRIMARY
                       KEY,
                       name
                       TEXT
                       NOT
                       NULL,
                       email
                       TEXT
                       UNIQUE
                       NOT
                       NULL,
                       phone
                       TEXT,
                       membership_tier
                       TEXT,
                       join_date
                       DATE
                       NOT
                       NULL,
                       status
                       TEXT
                       DEFAULT
                       'active'
                   )
                   ''')

    # Create Courts table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS courts
                   (
                       court_id
                       INTEGER
                       PRIMARY
                       KEY,
                       court_name
                       TEXT
                       NOT
                       NULL,
                       surface_type
                       TEXT,
                       indoor
                       INTEGER
                       DEFAULT
                       0
                   )
                   ''')

    # Create Coaches table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS coaches
                   (
                       coach_id
                       INTEGER
                       PRIMARY
                       KEY,
                       name
                       TEXT
                       NOT
                       NULL,
                       specialty
                       TEXT,
                       hourly_rate
                       REAL
                       NOT
                       NULL,
                       weekly_available_hours
                       INTEGER
                       DEFAULT
                       40
                   )
                   ''')

    # Create Bookings table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS bookings
                   (
                       booking_id
                       INTEGER
                       PRIMARY
                       KEY,
                       member_id
                       INTEGER
                       NOT
                       NULL,
                       coach_id
                       INTEGER,
                       court_id
                       INTEGER
                       NOT
                       NULL,
                       lesson_type
                       TEXT,
                       booking_date
                       DATE
                       NOT
                       NULL,
                       start_time
                       TEXT
                       NOT
                       NULL,
                       end_time
                       TEXT
                       NOT
                       NULL,
                       duration_minutes
                       INTEGER
                       NOT
                       NULL,
                       price
                       REAL
                       NOT
                       NULL,
                       status
                       TEXT
                       DEFAULT
                       'scheduled',
                       cancellation_reason
                       TEXT,
                       created_at
                       TEXT
                       DEFAULT
                       CURRENT_TIMESTAMP,
                       FOREIGN
                       KEY
                   (
                       member_id
                   ) REFERENCES members
                   (
                       member_id
                   ),
                       FOREIGN KEY
                   (
                       coach_id
                   ) REFERENCES coaches
                   (
                       coach_id
                   ),
                       FOREIGN KEY
                   (
                       court_id
                   ) REFERENCES courts
                   (
                       court_id
                   )
                       )
                   ''')

    print("Tables created successfully!")
    print("\nInserting sample data...")

    # Insert Members
    members_data = [
        (1, 'Sarah Johnson', 'sarah.j@email.com', '555-0101', 'Premium', '2023-01-15', 'active'),
        (2, 'Michael Chen', 'mchen@email.com', '555-0102', 'Standard', '2023-03-20', 'active'),
        (3, 'Emily Rodriguez', 'emily.r@email.com', '555-0103', 'Premium', '2022-06-10', 'active'),
        (4, 'David Kim', 'dkim@email.com', '555-0104', 'Junior', '2024-01-05', 'active'),
        (5, 'Lisa Anderson', 'lisa.a@email.com', '555-0105', 'Standard', '2023-09-12', 'active'),
        (6, 'James Wilson', 'jwilson@email.com', '555-0106', 'Premium', '2022-11-30', 'active'),
        (7, 'Maria Garcia', 'mgarcia@email.com', '555-0107', 'Standard', '2024-02-14', 'active'),
        (8, 'Robert Taylor', 'rtaylor@email.com', '555-0108', 'Junior', '2023-07-22', 'active')
    ]
    cursor.executemany('INSERT OR IGNORE INTO members VALUES (?,?,?,?,?,?,?)', members_data)

    # Insert Courts
    courts_data = [
        (1, 'Court 1', 'hard', 0),
        (2, 'Court 2', 'hard', 0),
        (3, 'Court 3', 'clay', 0),
        (4, 'Court 4', 'hard', 1),
        (5, 'Court 5', 'hard', 1)
    ]
    cursor.executemany('INSERT OR IGNORE INTO courts VALUES (?,?,?,?)', courts_data)

    # Insert Coaches
    coaches_data = [
        (1, 'Alex Martinez', 'advanced', 85.00, 35),
        (2, 'Jordan Lee', 'junior', 60.00, 40),
        (3, 'Sam Peterson', 'adult', 75.00, 38),
        (4, 'Chris Wong', 'advanced', 90.00, 32)
    ]
    cursor.executemany('INSERT OR IGNORE INTO coaches VALUES (?,?,?,?,?)', coaches_data)

    # Insert Bookings
    bookings_data = [
        (1, 1, 1, 1, 'private', '2025-12-01', '09:00', '10:00', 60, 85.00, 'completed', None, '2025-11-28 10:00:00'),
        (2, 3, 3, 2, 'private', '2025-12-01', '14:00', '15:00', 60, 75.00, 'completed', None, '2025-11-29 14:30:00'),
        (3, 2, 2, 3, 'semi-private', '2025-12-02', '10:00', '11:00', 60, 45.00, 'cancelled', 'weather',
         '2025-11-30 09:00:00'),
        (4, 5, 3, 1, 'group', '2025-12-03', '16:00', '17:30', 90, 35.00, 'completed', None, '2025-12-01 11:00:00'),
        (5, 1, 1, 4, 'private', '2025-12-04', '08:00', '09:00', 60, 85.00, 'cancelled', 'member-request',
         '2025-12-03 15:00:00'),
        (6, 6, 4, 1, 'private', '2025-12-05', '11:00', '12:00', 60, 90.00, 'completed', None, '2025-12-04 10:00:00'),
        (7, 3, 1, 2, 'private', '2025-12-06', '09:00', '10:00', 60, 85.00, 'completed', None, '2025-12-05 08:00:00'),
        (8, 4, 2, 3, 'private', '2025-12-07', '15:00', '16:00', 60, 60.00, 'completed', None, '2025-12-06 12:00:00'),
        (9, 2, None, 5, 'court-rental', '2025-12-08', '18:00', '19:00', 60, 40.00, 'cancelled', 'weather',
         '2025-12-07 16:00:00'),
        (10, 7, 3, 1, 'semi-private', '2025-12-09', '10:00', '11:00', 60, 45.00, 'completed', None,
         '2025-12-08 09:00:00'),
        (11, 1, 1, 2, 'private', '2025-12-10', '14:00', '15:00', 60, 85.00, 'completed', None, '2025-12-09 11:00:00'),
        (12, 3, 4, 4, 'private', '2025-12-11', '09:00', '10:00', 60, 90.00, 'completed', None, '2025-12-10 10:00:00'),
        (13, 6, 1, 1, 'private', '2025-12-12', '16:00', '17:00', 60, 85.00, 'cancelled', 'member-request',
         '2025-12-11 14:00:00'),
        (14, 5, 2, 3, 'group', '2025-12-13', '17:00', '18:30', 90, 35.00, 'completed', None, '2025-12-12 15:00:00'),
        (15, 1, 1, 1, 'private', '2025-12-14', '10:00', '11:00', 60, 85.00, 'completed', None, '2025-12-13 09:00:00'),
        (16, 8, 2, 2, 'private', '2025-12-15', '11:00', '12:00', 60, 60.00, 'completed', None, '2025-12-14 10:00:00'),
        (17, 3, 3, 4, 'private', '2025-12-16', '15:00', '16:00', 60, 75.00, 'completed', None, '2025-12-15 12:00:00'),
        (18, 2, None, 5, 'court-rental', '2025-12-17', '19:00', '20:00', 60, 40.00, 'completed', None,
         '2025-12-16 14:00:00'),
        (19, 6, 4, 1, 'private', '2025-12-18', '09:00', '10:00', 60, 90.00, 'completed', None, '2025-12-17 11:00:00'),
        (20, 1, 1, 2, 'private', '2025-12-19', '14:00', '15:00', 60, 85.00, 'cancelled', 'weather',
         '2025-12-18 10:00:00'),
        (21, 1, 1, 1, 'private', '2025-10-15', '09:00', '10:00', 60, 85.00, 'cancelled', 'member-request',
         '2025-10-14 10:00:00'),
        (22, 1, 1, 1, 'private', '2025-10-22', '09:00', '10:00', 60, 85.00, 'cancelled', 'member-request',
         '2025-10-21 10:00:00'),
        (23, 1, 1, 2, 'private', '2025-11-05', '14:00', '15:00', 60, 85.00, 'completed', None, '2025-11-04 11:00:00'),
        (24, 1, 1, 2, 'private', '2025-11-12', '14:00', '15:00', 60, 85.00, 'cancelled', 'member-request',
         '2025-11-11 09:00:00'),
        (25, 3, 4, 1, 'private', '2025-10-10', '10:00', '11:00', 60, 90.00, 'completed', None, '2025-10-09 12:00:00'),
        (26, 3, 1, 2, 'private', '2025-11-08', '09:00', '10:00', 60, 85.00, 'completed', None, '2025-11-07 10:00:00')
    ]
    cursor.executemany('INSERT OR IGNORE INTO bookings VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)', bookings_data)

    conn.commit()
    print("Sample data inserted successfully!")

    # Verify data
    print("\n" + "=" * 60)
    print("DATABASE VERIFICATION")
    print("=" * 60)

    cursor.execute("SELECT COUNT(*) FROM members")
    print(f"✓ Members: {cursor.fetchone()[0]} records")

    cursor.execute("SELECT COUNT(*) FROM courts")
    print(f"✓ Courts: {cursor.fetchone()[0]} records")

    cursor.execute("SELECT COUNT(*) FROM coaches")
    print(f"✓ Coaches: {cursor.fetchone()[0]} records")

    cursor.execute("SELECT COUNT(*) FROM bookings")
    print(f"✓ Bookings: {cursor.fetchone()[0]} records")

    print("\n" + "=" * 60)
    print("SAMPLE QUERY TEST")
    print("=" * 60)

    # Test query: Top members by bookings
    cursor.execute('''
                   SELECT m.name, COUNT(*) as booking_count
                   FROM members m
                            JOIN bookings b ON m.member_id = b.member_id
                   GROUP BY m.member_id, m.name
                   ORDER BY booking_count DESC LIMIT 3
                   ''')

    print("\nTop 3 Members by Bookings:")
    for row in cursor.fetchall():
        print(f"  • {row[0]}: {row[1]} bookings")

    conn.close()
    print("\n✓ Database setup complete! File created: courtiq.db")
    print("\nNext step: Run queries or build the AI backend")


if __name__ == "__main__":
    create_database()