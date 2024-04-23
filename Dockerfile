FROM python:3.11

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=src/main.py
EXPOSE 5000

ENV FLASK_APP=src/app.py
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
