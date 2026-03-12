from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from urllib import request

from quant.execution.messenger import Message, Messenger


class OpenClawMessenger(Messenger):
    """Send messages via webhook or local file for Open Claw integration."""

    def __init__(self) -> None:
        self.webhook = os.getenv("OPENCLAW_WEBHOOK_URL", "").strip()
        self.file_path = os.getenv("OPENCLAW_MESSAGE_FILE", "").strip()
        self.channel = os.getenv("OPENCLAW_CHANNEL_NAME", "openclaw")

    def send(self, message: Message) -> None:
        payload = {
            "channel": self.channel,
            "title": message.title,
            "body": message.body,
            "ts": datetime.utcnow().isoformat(),
        }

        if self.webhook:
            data = json.dumps(payload).encode("utf-8")
            req = request.Request(self.webhook, data=data, headers={"Content-Type": "application/json"})
            request.urlopen(req, timeout=10)
            return

        if self.file_path:
            path = Path(self.file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(payload, ensure_ascii=False) + "\n")
            return

        # fallback: print to console
        print(f"[OpenClaw] {payload['title']}\n{payload['body']}")
