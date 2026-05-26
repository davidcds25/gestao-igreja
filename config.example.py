# Copie este arquivo para config.py e preencha com os seus valores.
# O config.py NÃO é enviado ao GitHub (está no .gitignore).

# Nome da organização exibido no sistema
APP_NAME = "Minha Igreja"

# Chave de autenticação do WAHA (WhatsApp HTTP API)
# Defina a mesma chave no docker-compose.yml em WHATSAPP_API_KEY
WHATSAPP_API_KEY = "sua-chave-aqui"

# Credenciais do administrador padrão (geradas na primeira execução)
ADMIN_EMAIL    = "admin@sistema.com"
ADMIN_PASSWORD = "admin123"

# API Bíblia — api.bible (https://api.bible) — plano Starter gratuito: 5K calls/mês
# Endpoint base: https://rest.api.bible
# Cadastro e chave em: https://api.bible
#
# IDs de traduções em Português disponíveis (plano gratuito):
#   NVI Portuguesa:              35b94e98b2e3a01a-01  (recomendada)
#   Nova Versão Transformadora:  41a6caa722a21d88-01
#   NVI Moçambique 2024:         a47cbe7792801aa8-01
BIBLE_API_KEY = "sua-chave-aqui"
BIBLE_ID      = "35b94e98b2e3a01a-01"
