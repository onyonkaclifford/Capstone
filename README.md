# Capstone Project

## Development

Note: Create a `.env` file with keys similar to those of `.env.sample` and fill in the correct values before proceeding
with development (the `.env` file is not checked into Git because it contains secrets)

- Run: `chainlit run ./src/app.py --port 8000 -w`

## Deployment

1. Build image: `docker build -t capstone .`
2. Run: `docker run -dp 0.0.0.0:8000:8000 --env-file .env capstone`
