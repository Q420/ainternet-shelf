#!/usr/bin/env python3
"""Run the §7 live demonstration (Piece 8) against NVIDIA's
hosted API — the first live run: two real model seats in one
recorded run.

The credential is the custom.nvidia connector's: a surrogate is
attached to requests for integrate.api.nvidia.com by the
connector machinery and swapped for the real key on the
approved request. No key value appears here, in the record, or
in any log.

Usage: PYTHONPATH=src python3 scripts/run_live_demo_2026_11_22.py
Writes live-demo/run.db, live-demo/report.json, live-demo/run.html.
"""
import os
import sys
import urllib.request

sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..",
                                "src"))

from dynamic_credentials import add_surrogate_to_request

HOST = "integrate.api.nvidia.com"


class SurrogateHandler(urllib.request.BaseHandler):
    handler_order = 100

    def https_request(self, req):
        if req.host == HOST:
            add_surrogate_to_request(req, "custom.nvidia",
                                     allowed_hosts=[HOST])
        return req


urllib.request.install_opener(
    urllib.request.build_opener(SurrogateHandler()))

from framework.adapter import OpenAICompatibleAdapter
from framework.live_run import run_demonstration

HERE = os.path.join(os.path.dirname(__file__), "..", "live-demo")
os.makedirs(HERE, exist_ok=True)

adapter = OpenAICompatibleAdapter(
    endpoint=f"https://{HOST}/v1/chat/completions",
    model=os.environ.get("ADAPTER_MODEL", "moonshotai/kimi-k3.1-pro"),
    api_key=None, api_key_env="NVIDIA_API_KEY", timeout=180.0)

report = run_demonstration(
    os.path.join(HERE, "run.db"), adapter,
    report_path=os.path.join(HERE, "report.json"),
    observer_out=os.path.join(HERE, "run.html"))
import json
print(json.dumps(report, indent=1))
