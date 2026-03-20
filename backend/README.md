# Paystack Secure Backend Instructions

This backend handles secure payment initialization and webhook verification for the Hackura Suite.

## Setup

1. **Install Dependencies**:
   ```bash
   pip install fastapi uvicorn requests python-dotenv
   ```

2. **Configure Environment**:
   Edit `backend/.env` and add your Paystack Secret Key:
   ```env
   PAYSTACK_SECRET_KEY=sk_test_xxxx
   ```

3. **Run the Server**:
   ```bash
   python3 -m backend.main
   ```
   The server will start at `http://localhost:8000`.

## Testing Locally (Sandbox Mode)

1. **Expose Localhost**:
   Paystack needs to send webhooks to your server. Use `ngrok` or similar:
   ```bash
   ngrok http 8000
   ```
   Take the forwarded URL (e.g., `https://random.ngrok-free.app`).

2. **Configure Paystack Webhook**:
   - Go to [Paystack Settings > API Keys & Webhooks](https://dashboard.paystack.com/#/settings/developer).
   - Set the **Webhook URL** to `https://your-ngrok-url.app/webhook`.
   - Ensure you are in **Test Mode**.

3. **Run Desktop App**:
   - Go to the **Licensing** view.
   - Click "UPGRADE TO PRO".
   - It will open the browser. Use a [Paystack Test Card](https://paystack.com/docs/payments/test-cards/) (e.g., GH Mobile Money success card).
   - Once payment is successful, return to the desktop app and click "CHECK STATUS".

## Deployment
When deploying to production:
- Update `backend_url` in `core/paystack_engine.py` and `core/security.py` to your production URL.
- Use a production-grade database (e.g., PostgreSQL).
- Ensure the `PAYSTACK_SECRET_KEY` is set as an environment variable in your hosting provider.
