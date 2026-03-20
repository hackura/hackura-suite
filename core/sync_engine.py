import json
from PySide6.QtCore import QObject, Signal, QThread
from core.db import db_manager
from core.security import license_manager

class SyncWorker(QThread):
    finished = Signal(bool)
    
    def __init__(self):
        super().__init__()

    def run(self):
        if not license_manager.is_pro():
            print("Sync blocked: PRO license required.")
            self.finished.emit(False)
            return

        if not db_manager.use_cloud or not db_manager.cloud_conn:
            self.finished.emit(False)
            return

        try:
            local_conn = db_manager.get_connection()
            cloud_conn = db_manager.cloud_conn
            cursor = cloud_conn.cursor()

            # Mirror Scans
            scans = local_conn.execute("SELECT project_id, type, target, status, results, created_at FROM scans").fetchall()
            for s in scans:
                cursor.execute("""
                    INSERT INTO scans (project_id, type, target, status, results, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (s['project_id'], s['type'], s['target'], s['status'], s['results'], s['created_at']))

            # Mirror Findings
            findings = local_conn.execute("SELECT scan_id, severity, title, description, remediation, created_at FROM findings").fetchall()
            for f in findings:
                cursor.execute("""
                    INSERT INTO findings (scan_id, severity, title, description, remediation, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (f['scan_id'], f['severity'], f['title'], f['description'], f['remediation'], f['created_at']))

            # Mirror Assets
            assets = local_conn.execute("SELECT project_id, name, ip_address, os_type, category, first_seen FROM assets").fetchall()
            for a in assets:
                cursor.execute("""
                    INSERT INTO assets (project_id, name, ip_address, os_type, category, first_seen)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (a['project_id'], a['name'], a['ip_address'], a['os_type'], a['category'], a['first_seen']))

            # Mirror Settings (Vault Keys, etc)
            settings = local_conn.execute("SELECT key, value, is_secret FROM settings").fetchall()
            for s in settings:
                cursor.execute("""
                    INSERT INTO settings (key, value, is_secret)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (key) DO UPDATE SET 
                        value = EXCLUDED.value,
                        is_secret = EXCLUDED.is_secret
                """, (s['key'], s['value'], s['is_secret']))

            cloud_conn.commit()
            self.finished.emit(True)
        except Exception as e:
            print(f"Sync failed: {e}")
            self.finished.emit(False)

sync_engine = SyncWorker()
