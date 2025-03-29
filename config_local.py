# config_local.py
import os

# Set SESSION_DB_PATH to a writable directory
SESSION_DB_PATH = '/var/lib/pgadmin/sessions'
os.makedirs(SESSION_DB_PATH, exist_ok=True)
