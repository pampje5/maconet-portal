# app/core/config.py
import os


API_KEY = "CHANGE_ME"
JWT_SECRET = "CHANGE_ME_JWT_SECRET"
JWT_ALG = "HS256"
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")