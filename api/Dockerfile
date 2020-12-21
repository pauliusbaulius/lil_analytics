# TODO non-root containers

FROM python:3.8-alpine

EXPOSE 5000

RUN pip install fastapi uvicorn sqlalchemy jinja2 aiofiles

WORKDIR api/

COPY api/ api/

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "5000"]