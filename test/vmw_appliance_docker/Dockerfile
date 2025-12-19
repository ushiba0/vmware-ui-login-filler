FROM python:3.11-slim
RUN apt-get update && apt-get install -y sed zip && rm -rf /var/lib/apt/lists/*
COPY ./main.py /main.py
WORKDIR /app
CMD ["/bin/bash"]

