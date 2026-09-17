# PKG-00 skeleton image: runs the no-op worker shell (apps/worker/src/nquiry_worker).
# outbox/projection/recovery workers are not implemented until Phase 4/8/9.
FROM python:3.13-slim

WORKDIR /repo
COPY pyproject.toml README.md ./
COPY packages ./packages
COPY apps/worker ./apps/worker
COPY apps/api ./apps/api
# apps/api is copied too: pyproject.toml's [tool.setuptools] package-dir
# maps both nquiry_api and nquiry_worker as top-level packages of one
# shared distribution, so `pip install .` needs both source trees present
# regardless of which service a given image actually runs.

RUN pip install --no-cache-dir .

CMD ["python", "-m", "nquiry_worker"]
