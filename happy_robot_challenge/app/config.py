from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_key: str
    fmcsa_api_key: str

    class Config:
        env_file = ".env"

_settings = Settings()

def get_settings():
    return _settings
