import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

from app.core.config import settings

logger = logging.getLogger("webbook.email")


class EmailService:
    @staticmethod
    def send_password_reset_email(to_email: str, reset_token: str) -> bool:
        reset_url = (
            f"{settings.FRONTEND_URL}/reinitialiser-mot-de-passe?token={reset_token}"
        )
        subject = "Réinitialisation de votre mot de passe WebBook"

        from_email = settings.SMTP_FROM_EMAIL or settings.SMTP_USER
        from_name = settings.SMTP_FROM_NAME

        text_content = (
            f"Bonjour,\n\n"
            f"Vous avez demandé la réinitialisation du mot de passe de votre compte WebBook.\n"
            f"Veuillez ouvrir le lien ci-dessous dans votre navigateur pour définir un nouveau mot de passe :\n\n"
            f"{reset_url}\n\n"
            f"Ce lien est valable pendant {settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES} minutes.\n"
            f"Si vous n'êtes pas à l'origine de cette demande, vous pouvez ignorer cet email en toute sécurité.\n\n"
            f"L'équipe WebBook"
        )

        html_content = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 560px; margin: 0 auto; padding: 24px; color: #0f172a; background-color: #f8fafc;">
            <div style="text-align: center; margin-bottom: 24px;">
                <h1 style="color: #4f46e5; margin: 0; font-size: 26px; font-weight: 800;">WebBook</h1>
                <p style="color: #64748b; font-size: 14px; margin-top: 4px;">Votre carnet personnel de favoris & mémos</p>
            </div>
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 28px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                <h2 style="font-size: 18px; margin-top: 0; color: #0f172a;">Demande de réinitialisation</h2>
                <p style="font-size: 15px; color: #334155; line-height: 1.6;">
                    Vous avez demandé la réinitialisation du mot de passe de votre compte WebBook. Cliquez sur le bouton ci-dessous pour en définir un nouveau :
                </p>
                <div style="text-align: center; margin: 28px 0;">
                    <a href="{reset_url}" style="background-color: #4f46e5; color: #ffffff; padding: 12px 28px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 15px; display: inline-block;">
                        Réinitialiser mon mot de passe
                    </a>
                </div>
                <p style="font-size: 13px; color: #64748b; line-height: 1.5;">
                    Ce lien est valable pendant <strong>{settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES} minutes</strong>. Si vous n'êtes pas à l'origine de cette demande, vous pouvez ignorer cet email en toute sécurité.
                </p>
                <hr style="border: none; border-top: 1px solid #f1f5f9; margin: 20px 0;" />
                <p style="font-size: 12px; color: #94a3b8; word-break: break-all;">
                    Si le bouton ne fonctionne pas, copiez-collez cette adresse dans votre navigateur :<br />
                    <a href="{reset_url}" style="color: #4f46e5;">{reset_url}</a>
                </p>
            </div>
        </div>
        """

        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            logger.warning(
                "Configuration SMTP non définie (SMTP_USER ou SMTP_PASSWORD absent). Email de réinitialisation simulé pour %s : %s",
                to_email,
                reset_url,
            )
            return True

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = formataddr((from_name, from_email))
            msg["To"] = to_email

            msg.attach(MIMEText(text_content, "plain", "utf-8"))
            msg.attach(MIMEText(html_content, "html", "utf-8"))

            smtp_password = "".join(settings.SMTP_PASSWORD.split())

            if settings.SMTP_PORT == 465:
                with smtplib.SMTP_SSL(
                    settings.SMTP_HOST, settings.SMTP_PORT, timeout=15.0
                ) as server:
                    server.login(settings.SMTP_USER, smtp_password)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(
                    settings.SMTP_HOST, settings.SMTP_PORT, timeout=15.0
                ) as server:
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    server.login(settings.SMTP_USER, smtp_password)
                    server.send_message(msg)

            logger.info(
                "Email de réinitialisation envoyé avec succès à %s via SMTP (%s)",
                to_email,
                settings.SMTP_HOST,
            )
            return True
        except smtplib.SMTPAuthenticationError as exc:
            logger.error(
                "Erreur d'authentification SMTP pour %s (vérifiez l'adresse et le mot de passe d'application) : %s",
                settings.SMTP_USER,
                exc,
            )
            return False
        except Exception as exc:
            logger.error(
                "Erreur lors de l'envoi de l'email via SMTP (%s:%s) : %s",
                settings.SMTP_HOST,
                settings.SMTP_PORT,
                exc,
            )
            return False
