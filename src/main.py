import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "api.api_main:fast_api",
        host="0.0.0.0",
        port=9901,
        log_level="info",
        reload=True,
    )
