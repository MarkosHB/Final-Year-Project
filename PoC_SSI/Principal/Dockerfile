FROM python:3.12-slim

WORKDIR /app

COPY main.py /app/
COPY requirements.txt /app/

COPY flujos /app/flujos/
COPY templates /app/templates/
COPY static /app/static/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "main.py"]