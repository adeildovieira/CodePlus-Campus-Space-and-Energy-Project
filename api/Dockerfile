FROM python:3.9

# Maintainer information
LABEL maintainer1="Mark McCahill <mccahill@duke.edu>"
LABEL maintainer2="Desmond Boateng <dkb34@duke.edu>"
LABEL maintainer3="Gabriel Mendoza <gam70@duke.edu>"
LABEL maintainer4="Shriya Minocha <sm997@duke.edu>"
LABEL maintainer5="Adeildo Vieira <av259@duke.edu>"

# Define build arguments
ARG NB_USER="jovyan"
ARG NB_UID="1000"
ARG NB_GID="1000"
ARG APP_DIR="/app"

# Fix DL4006: Use bash shell for RUN commands
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Switch to the root user to install packages
USER root

# Set environment variable for non-interactive apt-get
ENV DEBIAN_FRONTEND=noninteractive

# Update and install required packages
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

# Generate locale for en_US.UTF-8
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen

# Configure environment variables
ENV SHELL=/bin/bash \
    NB_USER="${NB_USER}" \
    NB_UID=${NB_UID} \
    NB_GID=${NB_GID} \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8 \
    HOME="/home/${NB_USER}" \
    PATH="/home/${NB_USER}/.local/bin:${PATH}"

# Copy the script to fix permissions
COPY fix-permissions /usr/local/bin/fix-permissions
RUN chmod a+rx /usr/local/bin/fix-permissions

# Enable color prompt in the skeleton .bashrc
RUN sed -i 's/^#force_color_prompt=yes/force_color_prompt=yes/' /etc/skel/.bashrc

# Create NB_USER with the specified UID and GID
RUN groupadd --gid $NB_GID jovyan && \
    useradd -l -m -s /bin/bash -N -u $NB_UID --gid $NB_GID $NB_USER && \
    chmod g+w /etc/passwd && \
    fix-permissions "${HOME}"

# Upgrade pip
RUN pip install --upgrade pip

# Switch to NB_USER for installing Python packages and copying app files
USER $NB_USER

# Copy requirements.txt to the home directory and install dependencies
COPY requirements.txt $HOME/
RUN pip install -r $HOME/requirements.txt

# Copy the app directory to the specified APP_DIR
COPY ./app $APP_DIR/

# Expose port 8080 for the FastAPI application
EXPOSE 8080

# Start the FastAPI application
CMD ["uvicorn", "app.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8080"]
