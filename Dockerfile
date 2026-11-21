FROM python:3.12-slim
WORKDIR /artifact
COPY hytwin/ hytwin/
COPY tests/ tests/
RUN python -m unittest discover -s tests -v
ENTRYPOINT ["python", "-m", "hytwin"]
CMD ["demo", "--output", "/results"]
