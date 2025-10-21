import os
import smtplib
import pytest
from alerts import enviar_email_alerta


class DummySMTP:
    def __init__(self, host, port, timeout=10):
        self.host = host
        self.port = port
        self.sent = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def starttls(self):
        pass

    def login(self, user, password):
        if user == "bad":
            raise smtplib.SMTPAuthenticationError(535, b"Auth failed")

    def sendmail(self, frm, to, msg):
        self.sent = (frm, to, msg)
        return {}


def test_enviar_email_alerta_success(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.test")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_USER", "user@test")
    monkeypatch.setenv("SMTP_PASS", "secret")
    monkeypatch.setattr("smtplib.SMTP", DummySMTP)

    ok = enviar_email_alerta("Assunto", "Corpo", ["dest@test"])
    assert ok is True


def test_enviar_email_alerta_missing_config(monkeypatch):
    # ensure required env missing -> returns False and does not raise
    monkeypatch.delenv("SMTP_HOST", raising=False)
    monkeypatch.delenv("SMTP_USER", raising=False)
    monkeypatch.delenv("SMTP_PASS", raising=False)
    ok = enviar_email_alerta("Assunto", "Corpo", ["dest@test"])
    assert ok is False
