import uvicorn


from config import Config

Config("config.yaml")

if __name__ == "__main__":
    # run fastapi server using uvicorn
    uvicorn.run(
        "api.api_main:fast_api",
        host="0.0.0.0",
        port=9902,
        log_level="info",
        reload=True,
    )
