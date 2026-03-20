import hmac
import hashlib
import os
import requests
from fastapi import FastAPI, Request, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
from .database import update_user_plan, get_user
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Hackura Paystack Backend")

PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
PAYSTACK_WEBHOOK_SECRET = os.getenv("PAYSTACK_WEBHOOK_SECRET") # Same as Secret Key usually

class PaymentInit(BaseModel):
    email: str
    amount_ghs: float
    machine_id: str

@app.post("/initialize-payment")
async def initialize_payment(data: PaymentInit):
    """
    Step 1: Desktop app requests payment initialization.
    Secret key is used here on the server.
    """
    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "email": data.email,
        "amount": int(data.amount_ghs * 100),
        "currency": "GHS",
        "metadata": {
            "machine_id": data.machine_id
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    res_data = response.json()
    
    if res_data.get("status"):
        return {
            "success": True,
            "checkout_url": res_data["data"]["authorization_url"],
            "reference": res_data["data"]["reference"]
        }
    
    raise HTTPException(status_code=400, detail=res_data.get("message", "Payment initialization failed"))

@app.post("/webhook")
async def paystack_webhook(request: Request, x_paystack_signature: str = Header(None)):
    """
    Step 2: Paystack sends success notification.
    We verify the signature to ensure it's actually from Paystack.
    """
    body = await request.body()
    
    # Verify signature
    computed_signature = hmac.new(
        PAYSTACK_SECRET_KEY.encode('utf-8'),
        body,
        hashlib.sha512
    ).hexdigest()
    
    if computed_signature != x_paystack_signature:
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    data = await request.json()
    
    if data["event"] == "charge.success":
        reference = data["data"]["reference"]
        email = data["data"]["customer"]["email"]
        machine_id = data["data"]["metadata"]["machine_id"]
        
        # Verify transaction with Paystack immediately for extra safety (Optional but recommended)
        verify_url = f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
        v_resp = requests.get(verify_url, headers=headers)
        v_data = v_resp.json()
        
        if v_data.get("status") and v_data["data"]["status"] == "success":
            # Update local server database
            update_user_plan(machine_id, email, "PRO")
            print(f"Plan upgraded to PRO for Machine ID: {machine_id}")
            
    return {"status": "success"}

@app.get("/subscription-status/{machine_id}")
async def get_status(machine_id: str):
    """
    Step 3: Desktop app checks its status periodically.
    """
    user = get_user(machine_id)
    if not user:
        return {"machine_id": machine_id, "plan": "TRIAL"}
    
    return {
        "machine_id": user["machine_id"],
        "plan": user["plan"],
        "updated_at": user["updated_at"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
