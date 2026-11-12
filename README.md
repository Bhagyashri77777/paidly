# 💸 Paidly — Your AI Payments Copilot

Paidly turns plain English into real PayPal payments. Type a payment request in natural language — Google Gemini extracts the structured payment details and Paidly creates and captures a real order through PayPal's Orders v2 REST API (Sandbox) while tracking all freelancer transactions in a live dashboard.

## ✨ What It Does
1. **Natural Language Extraction:** Type a sentence like `"create a payment of 25 USD for website consulting"` and Google Gemini parses the amount, currency, and description into strict JSON.
2. **PayPal Orders v2 API Integration:** Authenticates via OAuth 2.0 client credentials and calls the PayPal Sandbox Orders v2 endpoint (`/v2/checkout/orders`) to create a live order and approval link.
3. **One-Click Capture & Live Tracker:** Captures the transaction via `/v2/checkout/orders/{id}/capture` and updates the live freelancer earnings dashboard.

## 🚀 How to Run Locally

1. **Clone this repository:**

    git clone https://github.com/Bhagyashri77777/paidly.git
    cd paidly

2. **Install dependencies:**

    pip install -r requirements.txt

3. **Run the Streamlit app:**

    streamlit run app.py

4. **Add your free API keys:**
   Paste your free **PayPal Sandbox Client ID & Secret** (from `developer.paypal.com`) and **Google Gemini API Key** (from `aistudio.google.com`) into the left sidebar of the app (or set `PAYPAL_CLIENT_ID`, `PAYPAL_SECRET`, and `GEMINI_API_KEY` as environment variables).

5. **Test the flow:**
   Type `"create a payment of 25 USD for website consulting"` in the chat box, view the generated PayPal Sandbox order, and click **Capture the payment** to complete the transaction.

## 🛠️ Built With
- **AI:** Google Gemini API (`gemini-2.5-flash`) for natural-language payment extraction (AI coding assistants were also used during development)
- **Payments:** PayPal Orders v2 REST API & OAuth 2.0 (PayPal Developer Sandbox)
- **Frontend & Stack:** Python, Streamlit, Pandas, Requests

## 📄 License
MIT License — see the `LICENSE` file for details.
