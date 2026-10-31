FROM mcr.microsoft.com/devcontainers/base:debian-13

ENV PATH="/home/vscode/.local/bin:${PATH}"

RUN rm -f /etc/apt/sources.list.d/yarn.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl gnupg \
        python3 python3-pip python3-venv \
    && install -d -m 0755 /etc/apt/keyrings \
    && curl -fsSL https://download.qgis.org/downloads/qgis-archive-keyring.gpg \
        -o /etc/apt/keyrings/qgis-archive-keyring.gpg \
    && printf "Types: deb\nURIs: https://qgis.org/debian\nSuites: trixie\nArchitectures: amd64\nComponents: main\nSigned-By: /etc/apt/keyrings/qgis-archive-keyring.gpg\n" \
        > /etc/apt/sources.list.d/qgis.sources \
    && apt-get update \
    && apt-get install -y --no-install-recommends qgis qt6-wayland \
    && rm -rf /var/lib/apt/lists/*

ENV LANG="C.UTF-8" LC_ALL="C.UTF-8"
