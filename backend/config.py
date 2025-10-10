import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    RETELL_API_KEY = os.getenv("RETELL_API_KEY")
    RETELL_BASE_URL = "https://api.retell.ai/v2"

settings = Settings()