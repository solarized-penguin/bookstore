import uvicorn


if __name__ == "__main__":
    config = uvicorn.Config("web_api:create_app", factory=True, host="0.0.0.0", port=8080, reload=True)
    server = uvicorn.Server(config)
    server.run()
