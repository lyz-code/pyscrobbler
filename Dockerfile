FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

# Install dependencies
COPY ./requirements.txt /app
RUN pip install -r requirements.txt

# Configure persistence
RUN mkdir /data
ENV DATABASE_URL="tinydb:///data/database.tinydb"

# Configure application
ENV LOG_LEVEL="debug"
ENV MODULE_NAME="pyscrobbler"
COPY ./src/pyscrobbler /app/pyscrobbler
