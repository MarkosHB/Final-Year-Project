FROM python:3.12-slim

WORKDIR /app

COPY emisor.py /app/
COPY contrato.abi /app/
COPY contrato.bin /app/
COPY requirements.txt /app/
COPY templates/ /app/templates/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5001

CMD ["python", "emisor.py"]