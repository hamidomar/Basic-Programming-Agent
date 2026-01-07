"""
Configuration for Gemini + E2B Code Execution Agent
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# E2B API key (required)
E2B_API_KEY = os.getenv("E2B_API_KEY")

if not E2B_API_KEY:
    raise ValueError(
        "E2B_API_KEY not found in environment.\n"
        "Create a .env file with: E2B_API_KEY=your-key-here\n"
        "Get your key from: https://e2b.dev/"
    )

# GCP configuration (optional - can be set at runtime)
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "")
GCP_LOCATION = os.getenv("GCP_LOCATION", "us-central1")

# Gemini model configuration
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")

print("✓ Configuration loaded")
print(f"  E2B API Key: {'*' * 20}{E2B_API_KEY[-4:]}")
if GCP_PROJECT_ID:
    print(f"  GCP Project: {GCP_PROJECT_ID}")
print(f"  GCP Location: {GCP_LOCATION}")
print(f"  Gemini Model: {GEMINI_MODEL}")
