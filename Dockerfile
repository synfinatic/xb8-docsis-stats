from python:3.12

RUN pip install poetry==1.7.0 && \
    mkdir /code

ENV \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.0.0

WORKDIR /code
COPY poetry.lock .
COPY pyproject.toml .
RUN poetry install

COPY ./xb8_docsis_stats .

ENV MODEM=10.0.0.1
ENV USERNAME=admin
ENV PASSWORD=INVALID_PASSWORD_CHANGE_ME
ENV GRAPHITE=127.0.0.1:2003
ENV PREFIX=modem
ENV INTERVAL=300
ENV LEVEL=info

CMD poetry run ./xb8-stats.py \
    --modem $MODEM \
    --username $USERNAME \
    --password $PASSWORD \
    --graphite $GRAPHITE \
    --prefix $PREFIX \
    --interval $INTERVAL \
    --log-level $LEVEL
