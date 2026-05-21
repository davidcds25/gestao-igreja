"""
Integração com WAHA (WhatsApp HTTP API)
Servidor local via Docker dentro do WSL2: detecta IP automaticamente.
"""

import json
import time
import base64
import tempfile
import os
import subprocess
import urllib.request
import urllib.error

try:
    from config import WHATSAPP_API_KEY as _API_KEY
except ImportError:
    _API_KEY = "sua-chave-aqui"
_SESSION  = "default"
_TIMEOUT  = 4


def _detectar_url():
    """Tenta localhost primeiro; se falhar usa o IP do WSL2 automaticamente."""
    for url in ("http://localhost:3000",):
        try:
            urllib.request.urlopen(url + "/api/health", timeout=2)
            return url
        except Exception:
            pass
    try:
        r = subprocess.run(
            ["wsl", "hostname", "-I"],
            capture_output=True, text=True, timeout=5,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        ip = r.stdout.strip().split()[0]
        if ip:
            return f"http://{ip}:3000"
    except Exception:
        pass
    return "http://localhost:3000"


_BASE_URL = _detectar_url()


def _headers():
    return {"X-Api-Key": _API_KEY, "Content-Type": "application/json"}


def _request(method, path, body=None):
    url  = f"{_BASE_URL}{path}"
    data = json.dumps(body).encode() if body else None
    req  = urllib.request.Request(url, data=data, headers=_headers(), method=method)
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            raw = resp.read().decode("utf-8").strip()
            return (json.loads(raw) if raw else {}), None
    except urllib.error.HTTPError as e:
        try:
            detail = json.loads(e.read().decode("utf-8"))
        except Exception:
            detail = {}
        return None, f"HTTP {e.code}: {detail.get('message', e.reason)}"
    except urllib.error.URLError as e:
        return None, f"Servidor offline ou inacessível: {e.reason}"
    except Exception as e:
        return None, str(e)


# ── Sessão ────────────────────────────────────────────────────────────────────

def deletar_sessao():
    """Remove a sessão atual (necessário quando está em estado FAILED)."""
    return _request("DELETE", f"/api/sessions/{_SESSION}")


def desconectar_sessao():
    """Faz logout do WhatsApp — desvincula o número sem deletar a sessão."""
    return _request("POST", f"/api/{_SESSION}/auth/logout")


def criar_instancia():
    """Inicia a sessão WAHA. Recria automaticamente se estiver em estado FAILED."""
    import time
    # Se a sessão existir em estado FAILED, deleta antes de recriar
    data, _ = _request("GET", f"/api/sessions/{_SESSION}")
    if data and data.get("status") == "FAILED":
        _request("DELETE", f"/api/sessions/{_SESSION}")
        time.sleep(0.5)

    data, err = _request("POST", "/api/sessions", {"name": _SESSION})
    if err and ("HTTP 422" in str(err) or "already exists" in str(err).lower()):
        data, err = _request("POST", f"/api/sessions/{_SESSION}/start")
    return data, err


def status_conexao():
    """Retorna o estado da conexão: 'open', 'close', 'connecting' ou None em erro."""
    data, err = _request("GET", f"/api/sessions/{_SESSION}")
    if err:
        return None, err
    status = data.get("status") if data else None
    mapping = {
        "WORKING":       "open",
        "SCAN_QR_CODE":  "connecting",
        "STARTING":      "connecting",
        "STOPPED":       "close",
        "FAILED":        "close",
    }
    return mapping.get(status, "close"), None


def _request_bytes(path):
    """GET que retorna bytes brutos (para endpoints que devolvem imagem PNG)."""
    url = f"{_BASE_URL}{path}"
    req = urllib.request.Request(url, headers=_headers(), method="GET")
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            return resp.read(), None
    except urllib.error.HTTPError as e:
        try:
            detail = json.loads(e.read().decode("utf-8"))
        except Exception:
            detail = {}
        return None, f"HTTP {e.code}: {detail.get('message', e.reason)}"
    except urllib.error.URLError as e:
        return None, f"Servidor offline ou inacessível: {e.reason}"
    except Exception as e:
        return None, str(e)


def obter_qrcode_base64():
    """Retorna o QR Code em base64 (data:image/png;base64,...) para exibição."""
    raw, err = _request_bytes(f"/api/{_SESSION}/auth/qr")
    if err:
        return None, err
    if not raw:
        return None, "Resposta vazia"
    b64 = base64.b64encode(raw).decode("ascii")
    return f"data:image/png;base64,{b64}", None


def abrir_qrcode():
    """Salva o QR Code como imagem temporária e abre no visualizador do sistema."""
    b64, err = obter_qrcode_base64()
    if err:
        return err
    if not b64:
        return "QR Code não disponível."

    if "," in b64:
        b64 = b64.split(",", 1)[1]

    try:
        img_data = base64.b64decode(b64)
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        tmp.write(img_data)
        tmp.close()
        os.startfile(tmp.name)
        return None
    except Exception as e:
        return str(e)


# ── Envio de mensagens ────────────────────────────────────────────────────────

def _formatar_numero(telefone):
    """Normaliza o número para o formato chatId do WAHA (55DDD+número@c.us)."""
    digits = "".join(c for c in telefone if c.isdigit())
    if len(digits) in (10, 11):          # DDD + número sem código do país
        digits = "55" + digits
    return f"{digits}@c.us"


def enviar_mensagem(telefone, texto):
    """Envia mensagem individual. Retorna (dados, erro)."""
    chat_id = _formatar_numero(telefone)
    body    = {"session": _SESSION, "chatId": chat_id, "text": texto}
    return _request("POST", "/api/sendText", body)


def enviar_em_lote(membros, texto, delay=3, progress_cb=None):
    """
    Envia mensagem para uma lista de membros com delay entre cada envio.
    membros: lista de dicts com chaves 'nome' e 'telefone'
    progress_cb: callable(enviados, total, nome_atual) chamado a cada envio
    Retorna lista de (nome, sucesso, detalhe)
    """
    resultados = []
    total = len(membros)

    for i, membro in enumerate(membros):
        nome     = membro["nome"]
        telefone = membro.get("telefone") or ""

        if not telefone.strip():
            resultados.append((nome, False, "Sem telefone cadastrado"))
            if progress_cb:
                progress_cb(i + 1, total, nome)
            continue

        _, err = enviar_mensagem(telefone, texto)
        sucesso = err is None
        resultados.append((nome, sucesso, err or "Enviado"))

        if progress_cb:
            progress_cb(i + 1, total, nome)

        if i < total - 1:
            time.sleep(delay)

    return resultados
