import os
import logging
from typing import List, Dict, Any

import pandas as pd
import smtplib
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

DEFAULT_DIAS_VENCER = int(os.getenv("ALERT_DIAS_VENCER", "30"))
DEFAULT_DIAS_PARADO = int(os.getenv("ALERT_DIAS_PARADO", "90"))


def carregar_estoque(caminho: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(
            caminho, parse_dates=["data_vencimento"], dayfirst=False
        )
        return df
    except Exception as e:
        logger.error(f"Falha ao carregar estoque: {e}")
        return pd.DataFrame()


def verificar_vencimento(
    df_estoque: pd.DataFrame, dias_alerta: int = DEFAULT_DIAS_VENCER
) -> pd.DataFrame:
    if df_estoque.empty:
        return pd.DataFrame()
    hoje = pd.Timestamp.now().normalize()
    df = df_estoque.copy()
    df["data_vencimento"] = pd.to_datetime(
        df["data_vencimento"], errors="coerce"
    )
    df["dias_para_vencer"] = (df["data_vencimento"] - hoje).dt.days
    return df[df["dias_para_vencer"] <= dias_alerta]


def verificar_parado(
    df_estoque: pd.DataFrame, dias_parado_threshold: int = DEFAULT_DIAS_PARADO
) -> pd.DataFrame:
    if df_estoque.empty:
        return pd.DataFrame()
    df = df_estoque.copy()
    # garante coluna dias_parado existe
    if "dias_parado" not in df.columns:
        return pd.DataFrame()
    return df[
        pd.to_numeric(df["dias_parado"], errors="coerce")
        >= dias_parado_threshold
    ]


def _env_bool(name: str) -> bool:
    v = os.getenv(name, "")
    return str(v).lower() in ("1", "true", "yes", "on")


def enviar_email_alerta(
    assunto: str, corpo: str, destinatarios: List[str]
) -> bool:
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    smtp_no_auth = _env_bool("SMTP_NO_AUTH")

    if not host:
        logger.warning("SMTP_HOST não configurado — email não será enviado.")
        return False
    if not destinatarios:
        logger.warning(
            "Nenhum destinatário fornecido — email não será enviado."
        )
        return False
    # Se não for modo no-auth, user/pass são necessários
    if not smtp_no_auth and (not user or not password):
        logger.warning("Credenciais SMTP ausentes e SMTP_NO_AUTH não ativado.")
        return False

    msg = MIMEText(corpo, "plain", "utf-8")
    msg["Subject"] = assunto
    msg["From"] = user if user else host
    msg["To"] = ", ".join(destinatarios)

    try:
        with smtplib.SMTP(host, port, timeout=10) as s:
            # quando autenticado normalmente usamos STARTTLS + login
            if not smtp_no_auth:
                try:
                    s.starttls()
                except Exception:
                    # alguns servidores como localhost com MailHog não suportam starttls
                    logger.debug("starttls não disponível/no-op")
                s.login(user, password)
            s.sendmail(msg["From"], destinatarios, msg.as_string())
        logger.info("E-mail de alerta enviado.")
        return True
    except Exception as e:
        logger.error(f"Falha ao enviar email: {e}")
        return False


def gerar_alertas_e_enviar(
    caminho_estoque: str, destinatarios: List[str]
) -> Dict[str, Any]:
    df = carregar_estoque(caminho_estoque)
    vencimentos = verificar_vencimento(df)
    parados = verificar_parado(df)
    mensagens = []
    if not vencimentos.empty:
        mensagens.append(
            "Produtos próximos ao vencimento:\n"
            + vencimentos.to_string(index=False)
        )
    if not parados.empty:
        mensagens.append(
            "Produtos parados por muito tempo:\n"
            + parados.to_string(index=False)
        )
    if mensagens:
        corpo = "\n\n".join(mensagens)
        assunto = "Alerta de Estoque - Sistema"
        enviado = enviar_email_alerta(assunto, corpo, destinatarios)
        return {
            "vencimentos": len(vencimentos),
            "parados": len(parados),
            "enviado": enviado,
        }
    return {"vencimentos": 0, "parados": 0, "enviado": False}
