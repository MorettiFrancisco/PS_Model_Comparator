FROM python:3.11-slim

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY requirements.txt pyproject.toml uv.lock* ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -r requirements.txt

COPY . /app

EXPOSE 8000

CMD ["python", "run.py"]