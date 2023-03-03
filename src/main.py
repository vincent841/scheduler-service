import uvicorn


from config import Config

if __name__ == "__main__":
    # create application configuration
    Config("config.yaml")

    # run fastapi server using uvicorn
    uvicorn.run(
        "api.api_main:fast_api",
        host="0.0.0.0",
        port=9902,
        log_level="info",
        reload=True,
    )
