FROM node:24-trixie-slim

ARG CODEX_VERSION=0.166.0
RUN apt-get update \
 && apt-get install -y --no-install-recommends openssh-server git python3 python3-venv python-is-python3 ca-certificates curl ripgrep \
 && rm -rf /var/lib/apt/lists/* \
 && rm -f /etc/ssh/ssh_host_* \
 && npm install -g "@openai/codex@${CODEX_VERSION}" \
 && mkdir -p /run/sshd /work /var/lib/kiss-ssh /home/node/.codex \
 && chown node:node /work /home/node/.codex \
 && usermod --password '*' node

ENV NPM_CONFIG_PREFIX=/home/node/.local
ENV PATH=/home/node/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
RUN printf '%s\n' 'export NPM_CONFIG_PREFIX=/home/node/.local' \
      'export PATH=/home/node/.local/bin:/usr/local/bin:$PATH' > /etc/profile.d/kiss-path.sh

# Only plugin resources enter the image, even with a repository-root context.
COPY .agents/plugins/marketplace.json /opt/kiss-chris-stack/.agents/plugins/marketplace.json
COPY .codex-plugin/plugin.json /opt/kiss-chris-stack/.codex-plugin/plugin.json
COPY plugin.json SKILL.md LICENSE README.md /opt/kiss-chris-stack/
COPY skills/ /opt/kiss-chris-stack/skills/
COPY hooks/ /opt/kiss-chris-stack/hooks/
COPY scripts/ /opt/kiss-chris-stack/scripts/
COPY assets/ /opt/kiss-chris-stack/assets/
COPY references/ /opt/kiss-chris-stack/references/
COPY agents/ /opt/kiss-chris-stack/agents/
COPY licenses/ /opt/kiss-chris-stack/licenses/
COPY docs/ /opt/kiss-chris-stack/docs/
COPY agent-traces/user-feedback/README.md /opt/kiss-chris-stack/agent-traces/user-feedback/README.md

COPY --chown=node:node containers/remote/codex-container.toml /home/node/.codex/config.toml
USER node
RUN codex plugin marketplace add /opt/kiss-chris-stack \
 && codex plugin add kiss-chris-stack@kiss-chris-stack
USER root

COPY containers/remote/sshd_config /etc/ssh/sshd_config
COPY containers/remote/entrypoint.sh /usr/local/bin/kiss-entrypoint
RUN chmod 755 /usr/local/bin/kiss-entrypoint
WORKDIR /work
EXPOSE 2222
ENTRYPOINT ["/usr/local/bin/kiss-entrypoint"]
