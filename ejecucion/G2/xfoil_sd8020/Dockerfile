# Local tag must be checked against image ID sha256:4ea55efc8f3c56c542acc2d525b9477a73d6a55b8f4d41a7587431fb719f92fb before building.
FROM codex-aero-openfoam:13

# Separate image; never modify the running CFD or historical containers.
RUN rm -f /etc/apt/sources.list.d/openfoam.list \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends xfoil=6.99.dfsg+1-3 \
    && rm -rf /var/lib/apt/lists/*

LABEL org.opencontainers.image.title="C02 isolated XFOIL evaluation"
