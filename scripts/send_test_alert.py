import os
from alerts import enviar_email_alerta

# configurar via env ou setar aqui (NÃO commit credenciais)
# os.environ["SMTP_HOST"] = "smtp.example.com"
# os.environ["SMTP_PORT"] = "587"
# os.environ["SMTP_USER"] = "user@example.com"
# os.environ["SMTP_PASS"] = "supersecret"

dest = os.getenv("ALERT_EMAILS", "seu@teste.local").split(",")
ok = enviar_email_alerta(
    "Teste de Alerta", "Corpo do teste", [d.strip() for d in dest]
)
print("Enviado?", ok)
