# TODO non-root containers

FROM python:3.8-alpine

EXPOSE 5000

# TODO pipenv for api and separate for bot!
RUN pip install fastapi uvicorn sqlalchemy jinja2 aiofiles python-multipart

WORKDIR api/

COPY api/ api/

ENV FASTAPI_KEY ${FASTAPI_KEY}
ENV DOMAIN ${DOMAIN}

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "5000"]