FROM python:3.11-alpine
LABEL authors="Clifford Onyonka"

WORKDIR /capstone
EXPOSE 8000

COPY . .
RUN pip install -r requirements.txt

CMD ["chainlit", "run", "./app.py", "--host", "0.0.0.0", "--port", "8000", "-h"]
