FROM atendai/evolution-api:latest
WORKDIR /evolution
RUN npm install @whiskeysockets/baileys@latest --save 2>&1 | tail -5
