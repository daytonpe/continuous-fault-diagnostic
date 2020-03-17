FROM python:3.7-alpine
COPY . .
RUN apk add --no-cache gcc musl-dev linux-headers
RUN apk update
RUN pip3 install -r ./requirements.txt
COPY . /app
WORKDIR /app
CMD ["gunicorn", "-w 4", "main:app"]