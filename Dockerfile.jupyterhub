ARG BASE_IMAGE=jupyterhub/jupyterhub:latest
FROM "${BASE_IMAGE}"

ENV PATH="/home/jovyan/.local/bin:${PATH}"

# ensure pip is up to date
RUN python3 -m pip install --upgrade pip

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

COPY jupyterhub_config.py /srv/jupyterhub/
