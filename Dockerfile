FROM python:3.9-slim
WORKDIR /app

# 1. First debug: Check initial directory state
RUN ls -la

COPY requirements.txt .

# 2. Debug after copying requirements
RUN ls -la

RUN pip install --no-cache-dir -r requirements.txt

# 3. Critical debug: Check files BEFORE Python file copy
RUN ls -la

# Explicitly list files instead of using *.py
COPY simulation_03.py concurrent_demo.py .

# 4. Final verification
RUN ls -la
