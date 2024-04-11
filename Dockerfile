FROM python:3.10-slim

COPY requirements.txt .
# RUN pip install uv
# RUN uv venv
RUN pip install -r requirements.txt

ENV ENV=prod

WORKDIR /app
COPY . ./

# Run the Streamlit app
CMD streamlit run app.py --server.port 8080 --server.address 0.0.0.0 --server.enableCORS=false --server.enableWebsocketCompression=false
