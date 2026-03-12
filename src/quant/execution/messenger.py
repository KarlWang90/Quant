from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Message:
    title: str
    body: str
    channel: str = "openclaw"


class Messenger:
    def send(self, message: Message) -> None:  # pragma: no cover - interface
        raise NotImplementedError
