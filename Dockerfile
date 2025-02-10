FROM ghcr.io/astral-sh/uv:python3.13-alpine
WORKDIR /code
COPY . /code/
RUN apk add --no-cache gcc linux-headers musl-dev python3-dev && uv sync --frozen
CMD ["uv", "run", "paul"]