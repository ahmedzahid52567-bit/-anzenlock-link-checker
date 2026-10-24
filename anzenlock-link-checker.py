"""AnzenLock Week-1 starter: Link Checker (single file, no DB, no ML).
Run: pip install flask  ->  python anzenlock-link-checker.py  ->  open http://127.0.0.1:5000
Rule-based only: safe for VTU mini demo. Paste a link, get Safe / Suspicious / Dangerous + plain-language reasons.
"""
import re, ipaddress
from urllib.parse import urlparse
from flask import Flask, request, render_template_string

app = Flask(__name__)
SHORTENERS = {"bit.ly","tinyurl.com","t.co","goo.gl","is.gd","cutt.ly","rebrand.ly","shorturl.at"}
SCAM_WORDS = ["kyc","blocked","suspended","lottery","winner","prize","verify-now","urgent","account-locked","free-recharge","bank-update"]
SUSPICIOUS_TLDS = {".tk",".ml",".ga",".cf",".gq",".xyz",".top",".buzz"}

def check_link(raw):
    url = raw.strip()
    if not url:
        return 0, "Empty", ["Paste a link first."]
    if not re.match(r"^https?://", url, re.I):
        url = "http://" + url
    try:
        p = urlparse(url)
        host = (p.hostname or "").lower()
    except Exception:
        return 0, "Invalid", ["Could not parse this link. Do not click it."]
    score, reasons = 100, []
    def deduct(n, msg):
        nonlocal score
        score = max(0, score - n); reasons.append(msg)
    if p.scheme == "http":
        deduct(15, "Uses http, not https — data on this page is not encrypted.")
    try:
        ipaddress.ip_address(host); deduct(35, "Link uses a raw IP address instead of a real domain name — a classic phishing sign.")
    except ValueError:
        pass
    if host in SHORTENERS or any(host.endswith("."+s) for s in SHORTENERS):
        deduct(25, "URL shortener hides the real destination — expand it before trusting it.")
    if any(w in url.lower() for w in SCAM_WORDS):
        deduct(25, "Link text uses pressure/scam words (KYC / blocked / lottery / urgent).")
    if any(host.endswith(t) for t in SUSPICIOUS_TLDS):
        deduct(15, "Domain uses a TLD often abused for phishing.")
    if host.count(".") >= 3:
        deduct(10, "Many subdomains — attackers use this to fake a trusted brand (e.g. bank.com.attacker.site).")
    if len(url) > 120:
        deduct(10, "Very long link — often hides the real destination.")
    if "xn--" in host:
        deduct(15, "Punycode in domain — can fake letters (e.g. paypaI vs paypal).")
    if " @" in url or "@" in (p.path or ""):
        deduct(15, "Contains @ in the link — can redirect you somewhere else.")
    if not reasons:
        reasons.append("No red flags found by these checks. Still check the sender before entering OTPs/passwords.")
    label = "Safe" if score >= 80 else ("Suspicious" if score >= 50 else "Dangerous")
    return score, label, reasons

PAGE = """<!doctype html><title>AnzenLock — Link Checker</title>
<style>body{font-family:system-ui;max-width:640px;margin:40px auto;padding:0 16px}input{width:100%;padding:12px;font-size:16px}button{padding:12px 20px;margin-top:10px;font-size:16px}.Safe{color:green}.Suspicious{color:#b77900}.Dangerous{color:red}</style>
<h1>🔒 AnzenLock — Link Checker</h1><p>Paste a link from SMS / WhatsApp. Do not click it first — check it here.</p>
<form method=post><input name=url placeholder="https://example.com/..." value="{{q}}"><br><button>Check link</button></form>
{% if result %}<h2 class="{{result[1]}}">{{result[1]}} — {{result[0]}} / 100</h2><ul>{% for r in result[2] %}<li>{{r}}</li>{% endfor %}</ul>{% endif %}
<p><small>Week-1 mini MVP · rule-based only · Prepared by Zahid Ahmed</small></p>"""

@app.route("/", methods=["GET","POST"])
def home():
    q = request.form.get("url","") if request.method=="POST" else ""
    result = check_link(q) if request.method=="POST" else None
    return render_template_string(PAGE, q=q, result=result)

if __name__ == "__main__":
    app.run(debug=True)
