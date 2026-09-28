import os
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

client = Hindsight(
    base_url="https://api.hindsight.vectorize.io",
    api_key=os.getenv("HINDSIGHT_API_KEY")
)

client.create_bank(
    bank_id="ai-scam-shield",
    name="AI Scam Shield"
)

print("Hindsight memory bank created!")