# TODO non-root containers

FROM python:3.8-slim-buster

EXPOSE 80

RUN pip install pipenv

COPY Pipfile Pipfile.lock /

# https://stackoverflow.com/questions/46503947/how-to-get-pipenv-running-in-docker
RUN pipenv install --system --deploy --ignore-pipfile

ADD bot/ bot/

ENV BOT_TOKEN ${BOT_TOKEN}
ENV COMMAND_PREFIX ${COMMAND_PREFIX}
ENV STATUS_MESSAGE ${STATUS_MESSAGE}
ENV INVITE_LINK ${INVITE_LINK}
ENV GITHUB_LINK ${GITHUB_LINK}
ENV PYTHONPATH "${PYTHONPATH}:/bot"
ENV BOT_OWNER_ID ${BOT_OWNER_ID}
ENV BOT_ID ${BOT_ID}
ENV FASTAPI_KEY ${FASTAPI_KEY}

CMD ["python3", "-u", "bot/main.py"]