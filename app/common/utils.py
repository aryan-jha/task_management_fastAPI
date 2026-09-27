from typing import Annotated, Any

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi_mail import (
    ConnectionConfig,
    FastMail,
    MessageSchema,
    MessageType,
    NameEmail,
)
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.connection import get_db
from app.modules.users.model import UserModel

conf = ConnectionConfig(
    MAIL_USERNAME=settings.EMAIL_SENDER,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.EMAIL_SENDER,
    MAIL_PORT=465,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False,
)


def is_authenticated(request: Request, db: Annotated[Session, Depends(get_db)]):

    try:
        user_token: str = request.headers.get("Authorization", "").split(" ")[-1]

        decoded_token: Any | None = jwt.decode(
            user_token, settings.SECRET_KEY, settings.TOKEN_ALGO
        ).get("id")

        user: UserModel | None = (
            db.query(UserModel).filter(UserModel.id == decoded_token).first()
        )

        if not user:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "You are unauthorized!")

        return user

    except InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "You are unauthorized!")


def _welcome_email_html(name: str | None = None) -> str:
    greeting = f"Hi {name}," if name else "Hi there,"
    return f"""
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Welcome</title>
      </head>
      <body style="margin:0;padding:0;background-color:#f4f6f8;font-family:Arial,Helvetica,sans-serif;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color:#f4f6f8;padding:32px 12px;">
          <tr>
            <td align="center">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:560px;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 8px 24px rgba(15,23,42,0.08);">
                <tr>
                  <td style="background:linear-gradient(135deg,#2563eb,#1d4ed8);padding:32px 28px;text-align:center;">
                    <p style="margin:0 0 8px;color:#bfdbfe;font-size:13px;letter-spacing:1.5px;text-transform:uppercase;">Welcome aboard</p>
                    <h1 style="margin:0;color:#ffffff;font-size:26px;line-height:1.3;">Your account is ready</h1>
                  </td>
                </tr>
                <tr>
                  <td style="padding:32px 28px 16px;color:#0f172a;">
                    <p style="margin:0 0 16px;font-size:16px;line-height:1.6;">{greeting}</p>
                    <p style="margin:0 0 16px;font-size:16px;line-height:1.6;color:#334155;">
                      Thanks for registering. Your account has been created successfully and you can now sign in to start creating and managing your tasks.
                    </p>
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin:24px 0;background-color:#f8fafc;border-radius:12px;">
                      <tr>
                        <td style="padding:18px 20px;">
                          <p style="margin:0 0 10px;font-size:14px;font-weight:700;color:#1e293b;">What you can do next</p>
                          <p style="margin:0 0 8px;font-size:14px;line-height:1.5;color:#475569;">1. Sign in with your email and password</p>
                          <p style="margin:0 0 8px;font-size:14px;line-height:1.5;color:#475569;">2. Create your first task</p>
                          <p style="margin:0;font-size:14px;line-height:1.5;color:#475569;">3. Track progress as you complete work</p>
                        </td>
                      </tr>
                    </table>
                    <p style="margin:0;font-size:16px;line-height:1.6;color:#334155;">
                      If you did not create this account, you can ignore this email.
                    </p>
                  </td>
                </tr>
                <tr>
                  <td style="padding:8px 28px 32px;">
                    <p style="margin:0;font-size:14px;line-height:1.6;color:#64748b;">
                      — Aryan
                    </p>
                  </td>
                </tr>
                <tr>
                  <td style="background-color:#f8fafc;padding:18px 28px;text-align:center;border-top:1px solid #e2e8f0;">
                    <p style="margin:0;font-size:12px;line-height:1.5;color:#94a3b8;">
                      This is an automated message. Please do not reply to this email.
                    </p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """


async def sendEmail(emails: list[str], name: str | None = None) -> Any:

    mailSubject: str = "Welcome — your account is ready"
    mailBody: str = _welcome_email_html(name)

    message = MessageSchema(
        subject=mailSubject,
        recipients=emails,
        body=mailBody,
        subtype=MessageType.html,
    )
    await FastMail(conf).send_message(message)
    return {"message": "email has been sent"}
