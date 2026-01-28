from .main import app

# This entry point for ASGI servers (like uvicorn)
# Run with: uvicorn app.asgi:app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
