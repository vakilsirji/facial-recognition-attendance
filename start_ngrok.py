import nest_asyncio
import uvicorn
from pyngrok import ngrok

import os

# 1. Authenticate ngrok (use environment variable or default token)
NGROK_TOKEN = os.getenv("NGROK_AUTHTOKEN", "3BR78NJ5sKpsOYkMqaxVtPYJdDu_3i9WaJqu4s2jLhbkoHFsK")
ngrok.set_auth_token(NGROK_TOKEN)

# 2. Open a tunnel on port 8000
public_url = ngrok.connect(8000).public_url
print(f"=======================================================")
print(f" -> ngrok tunnel available at: {public_url}")
print(f"=======================================================\n")

# 3. Allow FastAPI to run inside the Colab notebook
nest_asyncio.apply()

# 4. Run the server! (Make sure main.py is uploaded)
uvicorn.run("main:app", host="0.0.0.0", port=8000)
