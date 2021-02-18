ARG BASE_IMAGE=jupyterhub/jupyterhub:latest
FROM "${BASE_IMAGE}"

ENV PATH="/home/${NB_USER}/.local/bin:${PATH}"

# ensure pip is up to date
RUN python3 -m pip install --upgrade pip

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

COPY jupyterhub_config.py /srv/jupyterhub/
COPY wait-for-postgres.sh /srv/jupyterhub/

CMD ["./wait-for-postgres.sh", "jupyterhub", "--config", "/srv/jupyterhub/jupyterhub_config.py"]
