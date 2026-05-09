FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY benchmarks ./benchmarks

RUN python -m pip install --upgrade pip && python -m pip install -e .

CMD ["python", "-m", "prodkit_browser.jobs.docs_to_rag", "--fixture", "benchmarks/fixtures/docs_pages.json"]

