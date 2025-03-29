#FROM ubuntu:22.04
FROM python:3.9


LABEL maintainer="Mark McCahill <mccahill@duke.edu>"
ARG NB_USER="jovyan"
ARG NB_UID="1000"
ARG NB_GID="1000"
ARG APP_DIR="/app"


# Fix DL4006
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

USER root

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
    apt-get upgrade --yes && \
    apt-get install --yes --no-install-recommends \
    wget \
    curl \
    locales \
    net-tools \
    build-essential \
    git \
    bzip2 \
    vim \
    unzip \
    ssh \
    htop \
    jq \
    libcurl4 \
    postgresql-client \
      && \
    apt-get clean && rm -rf /var/lib/apt/lists/* 

RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen

# Configure environment
ENV SHELL=/bin/bash \
    NB_USER="${NB_USER}" \
    NB_UID=${NB_UID} \
    NB_GID=${NB_GID} \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8 \
    HOME="/home/${NB_USER}" \
    PATH="/home/${NB_USER}/.local/bin:${PATH}" 

# Copy a script that we will use to correct permissions after running certain commands
COPY fix-permissions /usr/local/bin/fix-permissions
RUN chmod a+rx /usr/local/bin/fix-permissions


# Enable prompt color in the skeleton .bashrc before creating the default NB_USER
# hadolint ignore=SC2016
RUN sed -i 's/^#force_color_prompt=yes/force_color_prompt=yes/' /etc/skel/.bashrc 

# Create NB_USER with name jovyan user with UID=1000 and in the 'jovyan' group
# and make sure these dirs are writable by the `users` group.
RUN groupadd --gid $NB_GID jovyan && \
    useradd -l -m -s /bin/bash -N -u $NB_UID --gid $NB_GID $NB_USER && \
    chmod g+w /etc/passwd && \
    fix-permissions "${HOME}" 


RUN pip install --upgrade pip

USER $NB_USER
COPY requirements.txt $HOME/
RUN pip install -r $HOME/requirements.txt

COPY ./app $APP_DIR/

# Create output directory and set permissions
USER root
RUN chmod -R 777 /app/output

EXPOSE 8080
CMD ["fastapi", "run", "app/main.py", "--proxy-headers", "--port", "8080"]

