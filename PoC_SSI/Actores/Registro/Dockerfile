FROM python:3.12-slim

WORKDIR /app

COPY registro.py /app/
COPY requirements.txt /app/
COPY templates/ /app/templates/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5004

CMD ["python", "registro.py"]