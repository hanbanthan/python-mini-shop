# Dockerfile - He thong quan ly cua hang show_missing
# Build docker build -t mini-store .
# Run: docker run -it --rm -v "$(pwd)/database:/app/database" mini-store 

FROM python:3.11-slim

WORKDIR /app

# Cai dependency truoc de tan dung Docker layer cache (chi rebuild lai
# buoc nay khi requirements.txt thay doi, khong phai moi lan sua code).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# CLI can input tuong tac (input()) -> chay voi 'docker run -it'
ENTRYPOINT ["python", "main.py"]