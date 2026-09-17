# PKG-00 skeleton image: boots the FastAPI toolchain shell (apps/api/src/nquiry_api).
# No domain/authority/persistence behavior exists yet — see nquiry_api/main.py.
FROM python:3.13-slim

WORKDIR /repo
COPY pyproject.toml README.md ./
COPY packages ./packages
COPY apps/api ./apps/api
COPY apps/worker ./apps/worker
# apps/worker is copied too: pyproject.toml's [tool.setuptools] package-dir
# maps both nquiry_api and nquiry_worker as top-level packages of one
# shared distribution, so `pip install .` needs both source trees present
# regardless of which service a given image actually runs.

RUN pip install --no-cache-dir .

EXPOSE 8000
CMD ["uvicorn", "nquiry_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
