FROM python:3.12-slim

WORKDIR /app

COPY verificador.py /app/
COPY contrato.abi /app/
COPY requirements.txt /app/
COPY templates/ /app/templates/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5003

CMD ["python", "verificador.py"]