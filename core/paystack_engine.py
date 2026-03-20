import requests
import json
from core.db import db_manager

class PaystackEngine:
    def __init__(self):
        # In production, this would be a real URL like https://api.hackura.com
        self.backend_url = "http://localhost:8000"

    def initialize_transaction(self, email, amount_ghs, machine_id):
        """Initialize a transaction via the secure backend."""
        db_manager.log_action("Payment Init (Backend)", f"Email: {email} | Machine: {machine_id}")
        
        url = f"{self.backend_url}/initialize-payment"
        payload = {
            "email": email,
            "amount_ghs": amount_ghs,
            "machine_id": machine_id
        }
        
        try:
            resp = requests.post(url, json=payload, timeout=10)
            data = resp.json()
            if data.get("success"):
                return {
                    "success": True, 
                    "checkout_url": data["checkout_url"],
                    "reference": data["reference"]
                }
            error_msg = data.get("detail", "Backend Initialization Failed")
            return {"success": False, "error": error_msg}
        except Exception as e:
            return {"success": False, "error": f"Backend unreachable: {str(e)}"}

    def verify_transaction(self, reference):
        # Verification is now handled by the server webhook.
        # The desktop app just polls for subscription status.
        return {"success": True, "message": "Verification is handled by server webhook."}

paystack_engine = PaystackEngine()
