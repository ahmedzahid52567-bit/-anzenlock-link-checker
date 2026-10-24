import sys, types, importlib.util

# Stub flask so we can test the pure logic without installing it
flask_stub = types.ModuleType("flask")
class _App:
    def __init__(self, *a, **k): pass
    def route(self, *a, **k):
        def deco(f): return f
        return deco
    def run(self, *a, **k): pass
flask_stub.Flask = _App
flask_stub.request = types.SimpleNamespace(form={})
flask_stub.render_template_string = lambda *a, **k: ""
sys.modules["flask"] = flask_stub

import os
spec = importlib.util.spec_from_file_location("checker", os.path.join(os.path.dirname(__file__), "anzenlock-link-checker.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

cases = [
    ("https://www.google.com", "Safe", 100),
    ("http://192.168.1.1/kyc-blocked-verify-now", "Dangerous", 15),
    ("https://bit.ly/abc123", "Suspicious", 75),
    ("https://www.sambhram.edu.in/", "Safe", 90),  # www + edu = extra subdomain level, -10, still Safe
]
for url, exp_verdict, exp_score in cases:
    score, verdict, reasons = mod.check_link(url)
    status = "OK " if (verdict == exp_verdict and score == exp_score) else "MISMATCH"
    print(f"{status} {url} -> {verdict} {score}/100 (expected {exp_verdict} {exp_score}) | reasons: {len(reasons)}")
