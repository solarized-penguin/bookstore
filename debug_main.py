import uvicorn
import logging
from web_api.core import get_settings

if __name__ == "__main__":
    print("Running with settings: ", get_settings().model_dump_json(indent=2))

    config = uvicorn.Config(
        "web_api:create_app", factory=True, host="0.0.0.0", port=8080, reload=True, log_level=logging.DEBUG
    )
    server = uvicorn.Server(config)
    server.run()
