FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
ENV UV_PROJECT_ENVIRONMENT=/opt/lab-venv PYTHONUTF8=1
WORKDIR /lab
# The source repository is bind-mounted at runtime; no separate lab copy.
CMD ["sleep", "infinity"]
