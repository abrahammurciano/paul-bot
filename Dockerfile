FROM python:3.11
RUN pip install poetry
WORKDIR /code
COPY . /code/
RUN poetry config virtualenvs.create false
RUN poetry install --only main --no-interaction --no-ansi
CMD ["python", "-m", "paul_bot"]