# AnzenLock Agent — Team SmartZ | AgentX PS-07

An AI agent, not a chatbot. It plans, uses real tools, and gives you a fix plan to follow.

**Problem:** people lose money clicking scam links in SMS and WhatsApp.
**Flow:** You ask → Agent plans → Agent checks → Fix plan → You follow it.

## Pages (separate, in order)
1. `/` — **Landing:** paste a link, click "Check this link". Nothing else on the page.
2. `/permissions` — **Permission Guard:** tick what the app asks for (Location / Contacts / SMS / Camera / Microphone), or skip this step.
3. `/result` — **Verdict + fix:** Safe / Suspicious / Dangerous link score, **overall phone safety score** (link score minus a trust-based penalty per risky permission — trusted 5/max 15, unknown 10/30, suspicious 15/30, dangerous 20/40), Gemini explanation in simple words, 3-step fix plan, and the permission flags.
4. `/health` — **Optional:** Device Health Score from free storage and outdated apps.

## What it does
1. **Link Checker (real tool)** — scores a link Safe / Suspicious / Dangerous (100 / 75 / 15 on the tested demos).
2. **Gemini API (real call)** — explains the verdict in simple words and gives a 3-step fix plan. Tries gemini-3.8-flash, then gemini-3.5-flash-lite, then gemini-2.5-flash (Google limits 2.5 to projects that already used it).
3. **Permission Guard** — flags risky app permissions (Location / Contacts / SMS).
4. **Device Health Score** — simple score from free storage and outdated apps.
5. **Overall phone safety score (v4.2 trust algorithm)** — link score minus a trust-based penalty per risky permission: trusted sites 5 each (max 15, so they stay in 85–100), unknown sites 10 each (max 30), suspicious links 15 each (max 30), dangerous links 20 each (max 40). Examples: google.com 100 with Location + Contacts + SMS flagged = **85/100**; an unknown clean link with the same permissions = 70/100; bit.ly 75 with 3 risky permissions = 45/100; a dangerous link with any risky permission = 0/100. Trust only counts after the link passes the safety checks — a dangerous link is dangerous whatever its host.
5. **You decide** — the agent gives the verdict and a clear fix plan (block sender, delete message, report it). Nothing runs automatically; you follow the plan.

## Demo links
- Safe: https://google.com
- Suspicious: https://bit.ly/abc
- Dangerous: http://192.168.1.1/kyc-blocked-verify-now
- Dangerous 20/100: https://192.168.1.1/kyc-blocked-verify-now-urgent-lottery-winner-free-recharge-account-locked-bank-update-suspended-prize-claim-now

## Run it locally
```bash
pip install -r requirements.txt
# copy .env.example to .env and put your free Gemini API key in it — never commit .env
python app.py
# open http://127.0.0.1:5000
```

## Deploy it (free, SnapDeploy)
Root directory: `anzenlock-agent` · Start command: `python app.py` · Port: `5000` · Set env var `GEMINI_API_KEY` in the host dashboard (never in the repo).

## Team
Team SmartZ — Zahid Ahmed (leader) + Vinay C · Built 11–12 Nov 2026 in the AgentX 24-hour build · Python, Flask, Gemini API, HTML

## Links
- Idea deck: https://docs.google.com/presentation/d/1VdXcUBgGk2wdMCeCcaBbmsDPRvsG25KF/edit?usp=sharing
- Hackathon: AgentX 2026 (Hack4Hack), PS-07 Open Track
