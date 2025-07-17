FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Create /workspace and give write permissions to group 0 (root group)
RUN mkdir -p /workspace && chmod -R g+rwX /workspace

# Also set the root group as the owner
RUN chgrp -R 0 /workspace

EXPOSE 8080
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
