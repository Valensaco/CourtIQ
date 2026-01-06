import os
import subprocess

# Remove old database
if os.path.exists('courtiq.db'):
    os.remove('courtiq.db')
    print("Old database removed")

# Run setup to create fresh database
subprocess.run(['python3', 'setup_database.py'])
print("Database reset complete!")
