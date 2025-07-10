from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_PHONE_NUMBER: str

    class Config:
        env_file = ".env"

settings = Settings()