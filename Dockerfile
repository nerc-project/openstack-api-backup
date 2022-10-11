# This Dockerfile uses a multi-stage build

# Builder Image
FROM python:3.9-slim-bullseye as builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential curl && \
    apt-get clean -y

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

RUN python3 -m venv /opt/venv

COPY src/bin/openstack-api-backup.sh /opt/venv/bin
COPY src/bin/openstack-vm-state.py /opt/venv/bin

# Final Image
FROM python:3.9-slim-bullseye

COPY --from=builder --chown=1001:0 /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

USER 1001

CMD [ "openstack-api-backup.sh" ]
