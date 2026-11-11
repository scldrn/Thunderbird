FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl gnupg && rm -rf /var/lib/apt/lists/*
COPY openfoam13.complete.deb /tmp/openfoam13.deb
RUN curl -fsSL https://dl.openfoam.org/gpg.key -o /etc/apt/trusted.gpg.d/openfoam.asc && printf '%s\n' 'deb https://dl.openfoam.org/ubuntu noble main' > /etc/apt/sources.list.d/openfoam.list && apt-get update && expected=$(apt-cache show openfoam13 | sed -n 's/^SHA256: //p' | head -n 1) && test -n "$expected" && printf '%s  /tmp/openfoam13.deb\n' "$expected" | sha256sum -c - && apt-get install -y --no-install-recommends /tmp/openfoam13.deb && rm -f /tmp/openfoam13.deb && rm -rf /var/lib/apt/lists/*
SHELL ["/bin/bash", "-c"]
WORKDIR /cases
CMD ["/bin/bash", "-c", "source /opt/openfoam13/etc/bashrc && foamRun -help"]
