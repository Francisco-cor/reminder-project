from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_PHONE_NUMBER: str
    TWILIO_SMS_NUMBER: str

     # Credenciales de Outlook/Microsoft Graph <--- NUEVA SECCIÓN
    OUTLOOK_TENANT_ID: str
    OUTLOOK_CLIENT_ID: str
    OUTLOOK_CLIENT_SECRET: str
    OUTLOOK_SENDER_EMAIL: str # El email desde el que se enviarán los correos

    class Config:
        env_file = ".env"

settings = Settings()