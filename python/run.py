import uvicorn


if __name__ == "__main__":
    # Use import string to enable reload
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


