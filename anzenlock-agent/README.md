# AnzenLock Agent — Team SmartZ | AgentX PS-07

An AI agent, not a chatbot. It plans, uses real tools, and waits for your confirmation before any fix.

**Problem:** people lose money clicking scam links in SMS and WhatsApp.
**Flow:** You ask → Agent plans → Agent checks → Fix plan → You confirm.

## What it does
1. **Link Checker (real tool)** — scores a link Safe / Suspicious / Dangerous (100 / 75 / 15 on the tested demos).
2. **Gemini API (real call)** — explains the verdict in simple words and gives a 3-step fix plan.
3. **Permission Guard** — flags risky app permissions (Location / Contacts / SMS).
4. **Device Health Score** — simple score from free storage and outdated apps.
5. **Human confirmation** — nothing is fixed automatically. The fix plan only runs after you click Confirm.

## Demo links (1-click in the app)
- Safe: https://google.com
- Suspicious: https://bit.ly/abc
- Dangerous: http://192.168.1.1/kyc-blocked-verify-now

## Run it locally
```bash
pip install -r requirements.txt
# copy .env.example to .env and put your free Gemini API key in it — never commit .env
python app.py
# open http://127.0.0.1:5000
```

## Deploy it (free, SnapDeploy)
Start command: `python app.py` · Port: `5000` · Set env var `GEMINI_API_KEY` in the host dashboard (never in the repo).

## Team
Team SmartZ — Zahid Ahmed (leader) + Vinay C · Built 11–12 Nov 2026 in the AgentX 24-hour build · Python, Flask, Gemini API, HTML

## Links
- Idea deck: https://docs.google.com/presentation/d/1VdXcUBgGk2wdMCeCcaBbmsDPRvsG25KF/edit?usp=sharing
- Hackathon: AgentX 2026 (Hack4Hack), PS-07 Open Track
