import sqlite3
import os
import psycopg2
from psycopg2.extras import RealDictCursor

class DatabaseManager:
    def __init__(self, db_path=None):
        if db_path is None:
            # Persistent Storage in User Home
            base_dir = os.path.join(os.path.expanduser("~"), "HackuraSuite", "data")
            os.makedirs(base_dir, exist_ok=True)
            self.db_path = os.path.join(base_dir, "settings.db")
            
            # Migration Logic: Move legacy DB if it exists in current dir
            legacy_db = "settings.db"
            if os.path.exists(legacy_db) and not os.path.exists(self.db_path):
                import shutil
                shutil.move(legacy_db, self.db_path)
                print(f"Migrated legacy database to {self.db_path}")
        else:
            self.db_path = db_path
            
        self.cloud_conn = None
        self.use_cloud = False
        self.init_db()

    def setup_cloud(self, url, callback=None):
        """Attempts to connect to cloud DB in a separate thread."""
        import threading
        def connect():
            try:
                self.cloud_conn = psycopg2.connect(url, connect_timeout=5)
                self.use_cloud = True
                if callback: callback(True)
            except Exception as e:
                print(f"Cloud DB Connection Failed: {e}")
                self.use_cloud = False
                if callback: callback(False)

        thread = threading.Thread(target=connect)
        thread.daemon = True
        thread.start()

    def get_connection(self):
        if self.use_cloud and self.cloud_conn:
            return self.cloud_conn
        
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        conn = self.get_connection()
        # Configuration settings
        conn.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                is_secret INTEGER DEFAULT 0
            )
        ''')
        
        # Audit Logs
        conn.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Client Management
        conn.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                website TEXT,
                logo_path TEXT,
                authorization_status TEXT DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Project Management (linked to clients)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients (id)
            )
        ''')

        # Scan History
        conn.execute('''
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                type TEXT NOT NULL,
                target TEXT NOT NULL,
                status TEXT,
                results TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')

        # Detailed Findings
        conn.execute('''
            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id INTEGER,
                severity TEXT,
                title TEXT,
                description TEXT,
                remediation TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (scan_id) REFERENCES scans (id)
            )
        ''', )
        conn.commit()

    def set_setting(self, key, value, is_secret=False):
        from core.security import vault
        if is_secret and vault:
            value = vault.encrypt(value)
        
        conn = self.get_connection()
        conn.execute("INSERT OR REPLACE INTO settings (key, value, is_secret) VALUES (?, ?, ?)", (key, value, 1 if is_secret else 0))
        conn.commit()

    def get_setting(self, key, default=None, is_secret=False):
        from core.security import vault
        conn = self.get_connection()
        res = conn.execute("SELECT value, is_secret FROM settings WHERE key = ?", (key,)).fetchone()
        if res:
            val = res['value']
            if res['is_secret'] and vault:
                decrypted = vault.decrypt(val)
                return decrypted if decrypted is not None else val
            return val
        return default

    def log_action(self, action, details=""):
        conn = self.get_connection()
        conn.execute("INSERT INTO audit_logs (action, details) VALUES (?, ?)", (action, details))
        conn.commit()

    def prune_logs(self):
        conn = self.get_connection()
        conn.execute("DELETE FROM audit_logs WHERE created_at < date('now', '-30 days')")
        conn.commit()
        self.vacuum()

    def vacuum(self):
        # Vacuum cannot be run inside a transaction
        conn = sqlite3.connect(self.db_path)
        conn.execute("VACUUM")

    def clear_projects(self):
        conn = self.get_connection()
        conn.execute("DELETE FROM findings")
        conn.execute("DELETE FROM scans")
        conn.execute("DELETE FROM projects")
        conn.commit()
        self.log_action("Maintenance", "All projects and scan data cleared")

    def factory_reset(self):
        conn = self.get_connection()
        tables = ["findings", "scans", "projects", "clients", "audit_logs", "settings"]
        for table in tables:
            conn.execute(f"DELETE FROM {table}")
        conn.commit()
        # This triggers the setup wizard on next launch
        conn.close()

db_manager = DatabaseManager()
