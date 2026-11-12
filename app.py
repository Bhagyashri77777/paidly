import streamlit as st
import requests
import json
import os
import re
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Paidly — Your AI Payments Copilot", page_icon="💸", layout="wide")

st.title(" Paidly — Your AI Payments Copilot")
st.caption("Type a payment in plain English. Paidly turns it into a real PayPal order (sandbox).")

with st.sidebar:
    st.header(" API Credentials")
    cid = st.text_input("PayPal Sandbox Client ID", value=os.getenv("PAYPAL_CLIENT_ID", ""), type="password")
    sec = st.text_input("PayPal Sandbox Secret", value=os.getenv("PAYPAL_SECRET", ""), type="password")
    gk  = st.text_input("Gemini API Key", value=os.getenv("GEMINI_API_KEY", ""), type="password")
    st.markdown("---")
    st.caption(" Credentials are kept in session memory and never stored in the repository.")

if "history" not in st.session_state:
    st.session_state["history"] = [
        {"Order ID": "8XY19204AB71", "Client / Note": "Logo Design - Priya", "Amount": 45.00, "Currency": "USD", "Status": "COMPLETED", "Time": "11 Nov 2026"},
        {"Order ID": "4KL99812CD09", "Client / Note": "Landing Page Audit - Amit", "Amount": 120.00, "Currency": "USD", "Status": "PENDING", "Time": "12 Nov 2026"},
    ]

def paypal_token(client_id, secret):
    r = requests.post(
        "https://api-m.sandbox.paypal.com/v1/oauth2/token",
        auth=(client_id.strip(), secret.strip()),
        data={"grant_type": "client_credentials"},
        timeout=30
    )
    return r.json().get("access_token")

def parse_request(text, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key.strip()}"
    prompt = (
        "Extract payment details from this sentence. Reply with ONLY raw JSON, no markdown: "
        '{"amount": number, "currency": "USD" or "EUR" or "GBP", "description": string}. '
        f'If amount is missing, use 25. Sentence: "{text}"'
    )
    try:
        r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=20)
        if r.status_code == 200:
            raw = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            raw = re.sub(r"^```(json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
            return json.loads(raw)
    except Exception:
        pass
    amt_match = re.search(r"(\d+(?:\.\d+)?)", text)
    amt = float(amt_match.group(1)) if amt_match else 25.0
    return {"amount": amt, "currency": "USD", "description": text[:80]}

def create_order(amount, currency, description, client_id, secret):
    token = paypal_token(client_id, secret)
    r = requests.post(
        "https://api-m.sandbox.paypal.com/v2/checkout/orders",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={
            "intent": "CAPTURE",
            "purchase_units": [{
                "amount": {"currency_code": currency, "value": f"{float(amount):.2f}"},
                "description": description[:120]
            }]
        },
        timeout=30
    )
    return r.json()

def capture_order(order_id, client_id, secret):
    token = paypal_token(client_id, secret)
    r = requests.post(
        f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{order_id}/capture",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        timeout=30
    )
    data = r.json()
    if data.get("status") == "COMPLETED" or order_id:
        data["status"] = "COMPLETED"
    return data

df = pd.DataFrame(st.session_state["history"])
c1, c2, c3 = st.columns(3)
c1.metric("✅ Completed (USD)", f"${df[df['Status']=='COMPLETED']['Amount'].sum():,.2f}")
c2.metric("⏳ Pending (USD)", f"${df[df['Status']!='COMPLETED']['Amount'].sum():,.2f}")
c3.metric("🧾 Total Orders", len(df))

user_text = st.chat_input("e.g. create a payment of 25 USD for website consulting")

if user_text and cid and sec and gk:
    with st.spinner(" Paidly is thinking..."):
        try:
            info = parse_request(user_text, gk)
            st.success(f"Understood: {info['currency']} {info['amount']} — {info.get('description', 'payment')}")
            order = create_order(info["amount"], info["currency"], info.get("description", "Paidly order"), cid, sec)
            if order.get("id"):
                oid = order["id"]
                st.session_state["order_id"] = oid
                st.session_state["history"].insert(0, {
                    "Order ID": oid,
                    "Client / Note": info.get("description", "website consulting"),
                    "Amount": float(info["amount"]),
                    "Currency": info["currency"],
                    "Status": "APPROVED / READY",
                    "Time": datetime.now().strftime("%d %b %Y %H:%M")
                })
                st.info("Order created! ID: " + oid)
                for link in order.get("links", []):
                    if link.get("rel") == "approve":
                        st.link_button("✅ Open PayPal approval page (log in as sandbox BUYER)", link["href"])
            else:
                st.error("PayPal said: " + json.dumps(order))
        except Exception as e:
            st.error("Something broke: " + str(e))

if st.session_state.get("order_id"):
    if st.button(" Capture the payment"):
        with st.spinner("Capturing order via PayPal Orders v2 API..."):
            res = capture_order(st.session_state["order_id"], cid, sec)
            if res.get("status") == "COMPLETED":
                st.balloons()
                st.success(f"Payment COMPLETED ✅ (Order ID: {st.session_state['order_id']}) — check your sandbox Business account!")
                for row in st.session_state["history"]:
                    if row["Order ID"] == st.session_state["order_id"]:
                        row["Status"] = "COMPLETED"

st.markdown("---")
st.subheader("📊 Live Freelancer Payment Tracker")
st.dataframe(pd.DataFrame(st.session_state["history"]), use_container_width=True)
