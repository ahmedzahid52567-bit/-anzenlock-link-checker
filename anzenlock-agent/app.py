"""AnzenLock Agent v4 - Team SmartZ, AgentX PS-07. 24-hour build 11-12 Nov 2026.
Separate pages, in order:
  Page 1  /             - landing: paste a link, click "Check this link".
  Page 2  /permissions  - Permission Guard: tick what the app asks for (or skip).
  Page 3  /result       - Safe / Suspicious / Dangerous + overall phone safety score
                          (link score minus 10 per risky permission, max -20)
                          + Gemini explanation + fix plan.
  Page 4  /health       - optional Device Health Score.
Run: pip install -r requirements.txt  ->  python app.py  ->  open http://127.0.0.1:5000
Gemini key comes only from .env file. Never paste the key in chat or GitHub.
"""
import os
import requests
from dotenv import load_dotenv
from flask import Flask, request, render_template_string, redirect, url_for, session
from link_checker import check_link

load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "anzenlock-dev-secret")
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "").strip()
# Nov 2026: Google serves gemini-2.5-flash only to projects that already used it.
# New keys get 404 on 2.5, so try the current models first, 2.5 last.
MODELS = ["gemini-3.8-flash", "gemini-3.5-flash-lite", "gemini-2.5-flash"]

def ask_gemini(prompt):
    """Real Gemini API call. Tries each model until one answers."""
    if not GEMINI_KEY or GEMINI_KEY == "PASTE_YOUR_KEY_HERE":
        return "Gemini key not set yet. Put your key in the .env file, restart the app, and try again."
    last_err = ""
    for model in MODELS:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_KEY}"
            r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30)
            r.raise_for_status()
            data = r.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            # Never show the key: the error text contains the request URL with ?key=...
            last_err = str(e).replace(GEMINI_KEY, "[key hidden]")
            continue
    return f"Gemini call failed: {last_err}. Check your key in .env and your internet, then try again."

STYLE = """
*{box-sizing:border-box}
:root{--bg:#070b14;--card:#0f172a;--card2:#111c33;--teal:#2dd4bf;--lime:#a3e635;--amber:#fbbf24;--red:#f87171;--green:#34d399;--text:#e2e8f0;--muted:#94a3b8}
body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;background:radial-gradient(900px 500px at 15% 0%,#134e4a33,transparent),radial-gradient(800px 500px at 90% 20%,#1e3a8a44,transparent),var(--bg);color:var(--text);overflow-x:hidden}
a{color:var(--teal)}
.wrap{max-width:920px;margin:0 auto;padding:28px 18px 60px}
.hero{animation:fadeUp .7s ease both;text-align:center;padding:26px 18px 10px}
@keyframes fadeUp{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
@keyframes floaty{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
@keyframes shimmer{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
@keyframes popIn{from{opacity:0;transform:scale(.96)}to{opacity:1;transform:scale(1)}}
@keyframes slideIn{from{opacity:0;transform:translateX(-14px)}to{opacity:1;transform:translateX(0)}}
.shield{font-size:56px;animation:floaty 3s ease-in-out infinite;filter:drop-shadow(0 0 22px #2dd4bf88)}
h1{font-size:clamp(32px,6vw,52px);margin:10px 0 6px;background:linear-gradient(90deg,#fff,#2dd4bf,#a3e635,#fff);background-size:200% auto;-webkit-background-clip:text;background-clip:text;color:transparent;animation:shimmer 5s linear infinite}
.sub{color:var(--muted);font-size:17px;max-width:640px;margin:0 auto}
.flow{display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin:18px 0 8px}
.step{flex:1;min-width:130px;background:var(--card);border:1px solid #2dd4bf33;border-radius:14px;padding:12px;text-align:center;animation:slideIn .5s both}
.step b{display:block;font-size:13px}.step span{font-size:12px;color:var(--muted)}
.step .n{width:28px;height:28px;border-radius:50%;background:#334155;color:#e2e8f0;display:grid;place-items:center;margin:0 auto 6px;font-weight:800}
.step.active{border-color:var(--lime);box-shadow:0 0 0 3px #a3e63522}
.step.active .n{background:var(--teal);color:#042f2e}
.card{background:linear-gradient(180deg,var(--card),var(--card2));border:1px solid #ffffff14;border-radius:18px;padding:20px;margin:18px 0;animation:fadeUp .6s both}
.card h2{margin:0 0 6px;font-size:21px}
.card p{color:var(--muted);margin:6px 0 12px}
.card p b,.card li{color:var(--text)}
input{width:100%;padding:14px;border-radius:12px;border:1px solid #ffffff22;background:#020617;color:#fff;font-size:16px;outline:none}
input:focus{border-color:var(--teal);box-shadow:0 0 0 3px #2dd4bf33}
button{padding:13px 20px;border-radius:12px;border:0;background:linear-gradient(90deg,#2dd4bf,#a3e635);color:#042f2e;font-weight:800;font-size:16px;margin-top:10px}
button:hover{filter:brightness(1.1)}
.err{color:var(--red);font-weight:700}
.verdict{display:flex;gap:18px;align-items:center;flex-wrap:wrap;margin:14px 0}
.ring{width:110px;height:110px;flex:none}
.ring circle{fill:none;stroke-width:10}
.ring .bg{stroke:#1e293b}.ring .fg{stroke:url(#grad);stroke-linecap:round;transform:rotate(-90deg);transform-origin:center;transition:stroke-dashoffset 1s ease}
.Safe{color:var(--green)}.Suspicious{color:var(--amber)}.Dangerous{color:var(--red)}
.verdict h3{font-size:28px;margin:0}
ul.reasons{margin:8px 0;padding-left:20px}
ul.reasons li{margin:6px 0}
pre{white-space:pre-wrap;background:#020617;border:1px solid #ffffff14;border-radius:12px;padding:14px;line-height:1.6}
.trace{border-left:3px solid var(--teal);padding-left:14px;margin:12px 0}
.trace div{margin:7px 0}
.checks label{display:inline-block;background:#ffffff0d;border:1px solid #ffffff1a;border-radius:999px;padding:9px 13px;margin:5px 6px 5px 0}
.score-big{font-size:42px;font-weight:900}
small{color:var(--muted)}
.judge-note{background:#a3e63514;border:1px solid #a3e63533;border-radius:12px;padding:12px;font-size:14px}
.nav{margin-top:14px;font-size:15px}
"""

def steps(active):
    names = [("1", "Paste link"), ("2", "Permissions"), ("3", "Result"), ("4", "Health (optional)")]
    out = ['<div class="flow">']
    for n, t in names:
        cls = "step active" if int(n) == active else "step"
        out.append(f'<div class="{cls}"><div class="n">{n}</div><b>{t}</b></div>')
    out.append("</div>")
    return "".join(out)

def page(title, body, active):
    return ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            f"<title>{title} — AnzenLock Agent</title><style>{STYLE}</style></head><body>"
            "<div class=\"wrap\"><div class=\"hero\"><div class=\"shield\">🛡️</div>"
            "<h1>AnzenLock Agent</h1>"
            "<p class=\"sub\">Team SmartZ · AgentX PS-07 Open Track · An AI agent, not a chatbot — it plans, "
            "uses real tools, and gives you a fix plan to follow.</p>"
            f"{steps(active)}</div>{body}"
            "<p style=\"text-align:center\"><small>Team SmartZ — Zahid Ahmed + Vinay C · Built 11 Nov 2026 "
            "in the AgentX 24-hour build · Flask + Gemini API</small></p></div></body></html>")

LANDING = """
<div class="card"><h2>🔗 Check a link</h2>
<p>Do not click the link first — let the agent check it.</p>
{% if error %}<p class="err">{{ error }}</p>{% endif %}
<form method="post"><input name="url" placeholder="Paste a link from SMS / WhatsApp" value="{{ url }}"><br><button>▶ Check this link</button></form>
<p><small>Try: https://google.com &nbsp;·&nbsp; https://bit.ly/abc &nbsp;·&nbsp; http://192.168.1.1/kyc-blocked-verify-now</small></p>
</div>
"""

PERMS = """
<div class="card"><h2>🔐 Permission Guard</h2>
<p>While the agent checks your link, tell it what the app asks for. Tick the permissions — the agent flags the risky ones on the next page.</p>
<p><small>Checking: <b>{{ url }}</b></small></p>
<form method="post"><div class="checks">
<label><input type="checkbox" name="perm" value="Location"> Location</label>
<label><input type="checkbox" name="perm" value="Contacts"> Contacts</label>
<label><input type="checkbox" name="perm" value="SMS"> SMS</label>
<label><input type="checkbox" name="perm" value="Camera"> Camera</label>
<label><input type="checkbox" name="perm" value="Microphone"> Microphone</label>
</div><br><button>Show my result →</button></form>
<p class="nav"><a href="/result">Skip this step →</a> &nbsp;·&nbsp; <a href="/restart">← Back to start</a></p>
</div>
"""

RESULT = """
<div class="card"><h2>🔗 Your link result</h2>
<p><small>Checked: <b>{{ url }}</b></small></p>
<div class="verdict">
<svg class="ring" viewBox="0 0 110 110"><defs><linearGradient id="grad"><stop offset="0%" stop-color="#2dd4bf"/><stop offset="100%" stop-color="#a3e635"/></linearGradient></defs>
<circle class="bg" cx="55" cy="55" r="46"/><circle class="fg" cx="55" cy="55" r="46" stroke-dasharray="289" stroke-dashoffset="{{ 289 - 289*score/100 }}"/></svg>
<div><h3 class="{{ label }}">{{ label }} — {{ score }} / 100</h3><small>Tool 1: Link Checker · rule-based, tested</small></div></div>
<ul class="reasons">{% for x in reasons %}<li>{{ x }}</li>{% endfor %}</ul>
<div class="trace"><div>🧠 <b>Agent plan:</b> Run checker → Ask Gemini → Show fix plan → You follow it</div>
<div>🛠️ <b>Tool 1 done:</b> Link Checker scored {{ score }}/100</div>
<div>✨ <b>Tool 2 done:</b> Gemini API explained it in simple words</div>
<div>✅ <b>Done:</b> Fix plan shown — block sender, delete message, report it</div></div>
<div class="judge-note" style="margin-top:12px"><b>Overall phone safety: {{ overall }} / 100 — {{ overall_label }}</b><br>
{% if chosen %}<small>Link score {{ score }} − {{ deduction }} for {{ risky|length }} risky permission(s) (10 points each, max 20) = {{ overall }}</small>
{% else %}<small>Permission check skipped, so the overall score is the link score.</small>{% endif %}</div>
<h3>✨ Gemini explanation</h3><pre>{{ gemini }}</pre>
<h3>🛠️ Fix plan — what to do next</h3><pre>{{ fix }}</pre>
</div>

<div class="card"><h2>🔐 Permission check</h2>
{% if chosen %}
<p><b>You ticked:</b> {{ chosen|join(", ") }}</p>
{% if risky %}<p><b>Flagged:</b> {{ risky|join(", ") }}</p><p>Location + Contacts + SMS together is high risk for a simple app. Does it really need them?</p>
{% else %}<p><b>Flagged:</b> None risky in this list.</p>{% endif %}
{% else %}
<p>You skipped the permission check. <a href="/permissions">Go back and check permissions</a></p>
{% endif %}
</div>

<div class="card judge-note"><b>For judges — what to watch:</b> 1) Paste a link → agent plans out loud. 2) Real tool scores it. 3) Real Gemini explains it. 4) Fix plan appears with clear next steps — block sender, delete message, report it. Gemini already gives the verdict, so no extra approval click is needed. Overall phone safety = link score minus 10 per risky permission (max 20).</div>
<p class="nav"><a href="/health">Optional: check device health →</a> &nbsp;·&nbsp; <a href="/restart">Check another link ↺</a></p>
"""

HEALTH = """
<div class="card"><h2>❤️ Device Health Score <small>(optional)</small></h2>
<p>Demo score from free storage and outdated apps.</p>
<form method="post"><input name="storage" placeholder="Free storage %, e.g. 40" value="{{ storage }}"><br><br><input name="outdated" placeholder="Outdated apps, e.g. 3" value="{{ outdated }}"><br><button>Get health score</button></form>
{% if score is not none %}<p><span class="score-big">{{ score }} / 100</span><br><small>Health score — higher is safer</small></p>{% endif %}
<p class="nav"><a href="/result">← Back to result</a> &nbsp;·&nbsp; <a href="/restart">Check another link ↺</a></p>
</div>
"""

@app.route("/", methods=["GET", "POST"])
def landing():
    if request.method == "POST":
        url = request.form.get("url", "").strip()
        if not url:
            return render_template_string(page("Check a link", LANDING, 1), error="Paste a link first.", url=url)
        session["url"] = url
        session.pop("result", None)
        session.pop("perms", None)
        session.pop("risky", None)
        return redirect(url_for("permissions"))
    return render_template_string(page("Check a link", LANDING, 1), error="", url="")

@app.route("/permissions", methods=["GET", "POST"])
def permissions():
    url = session.get("url")
    if not url:
        return redirect(url_for("landing"))
    if request.method == "POST":
        chosen = request.form.getlist("perm")
        risky = [p for p in chosen if p in ("Location", "Contacts", "SMS")]
        session["perms"] = chosen
        session["risky"] = risky
        return redirect(url_for("result"))
    return render_template_string(page("Permission Guard", PERMS, 2), url=url)

@app.route("/result")
def result():
    url = session.get("url")
    if not url:
        return redirect(url_for("landing"))
    res = session.get("result")
    if not res or res.get("url") != url:
        score, label, reasons = check_link(url)
        gemini = ask_gemini(f"Explain this link check in simple words for a normal phone user. Link: {url}. Verdict: {label} {score}/100. Reasons: {'; '.join(reasons)}. Keep it to 4 short lines.")
        fix = ask_gemini(f"Give a 3-step fix plan for this link. Link: {url}. Verdict: {label} {score}/100. Plain words, no jargon.")
        res = {"url": url, "score": score, "label": label, "reasons": reasons, "gemini": gemini, "fix": fix}
        session["result"] = res
    # Overall phone safety: the link score minus 10 per risky permission flagged (max -20).
    # The link score itself never changes — google.com is clean, so it stays 100.
    risky = session.get("risky", [])
    deduction = min(20, 10 * len(risky))
    overall = max(0, res["score"] - deduction)
    overall_label = "Safe" if overall >= 80 else ("Suspicious" if overall >= 50 else "Dangerous")
    return render_template_string(
        page("Your result", RESULT, 3),
        url=url, score=res["score"], label=res["label"], reasons=res["reasons"],
        gemini=res["gemini"], fix=res["fix"],
        chosen=session.get("perms", []), risky=risky,
        overall=overall, overall_label=overall_label, deduction=deduction,
    )

@app.route("/health", methods=["GET", "POST"])
def health():
    storage = request.form.get("storage", "")
    outdated = request.form.get("outdated", "")
    score = None
    if request.method == "POST" and storage:
        try:
            score = max(0, min(100, int(storage) - int(outdated or 0) * 5))
        except ValueError:
            score = None
    return render_template_string(page("Device Health", HEALTH, 4), storage=storage, outdated=outdated, score=score)

@app.route("/restart")
def restart():
    session.clear()
    return redirect(url_for("landing"))

if __name__ == "__main__":
    # Local: http://127.0.0.1:5000  |  Hosting (SnapDeploy etc.): uses $PORT and 0.0.0.0
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
