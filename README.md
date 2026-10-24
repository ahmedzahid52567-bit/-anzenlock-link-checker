# AnzenLock Link Checker

Week-1 starter for AnzenLock, a VTU mini project on proactive mobile security.

Paste a link, get a simple verdict: **Safe / Suspicious / Dangerous**, with plain-language reasons.

## How it works

Rule-based only, no database, no ML. It checks, in simple words:
- http instead of https
- raw IP address instead of a real domain name
- URL shorteners that hide the real destination
- pressure / scam words in the link (KYC, blocked, lottery, urgent)
- domain endings often abused for phishing

Each problem lowers the score from 100.

## Example results

| Link | Verdict |
|---|---|
| https://www.google.com | Safe 100/100 |
| https://www.sambhram.edu.in/ | Safe 90/100 |
| https://bit.ly/abc123 | Suspicious 75/100 |
| http://192.168.1.1/kyc-blocked-verify-now | Dangerous 15/100 |

## Tech

Python + Flask, single file. No database, no account, no data leaves your machine — the checker never fetches or clicks the pasted link.

## Run it

```bash
pip install -r requirements.txt
python anzenlock-link-checker.py
```

Then open http://127.0.0.1:5000

## Test it

```bash
python test_checker.py
```

This tests the checking logic without needing Flask installed.

## License

MIT — see LICENSE.
