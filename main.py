import os
import uvicorn

if __name__ == "__main__":
    # Render sets the PORT environment variable dynamically
    port = int(os.environ.get("PORT", 8000))
    
    # Use string syntax "src.app:app" to enable reload without issues
    uvicorn.run("src.app:app", port=port, reload=True)