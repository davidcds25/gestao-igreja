"""
Versículo do dia — bible-api.com (Almeida) com fallback local em português.
Seleciona um versículo determinístico por dia e faz cache no disco.
"""

import json
import threading
import urllib.request
from datetime import date
from pathlib import Path

_CACHE_FILE = Path(__file__).parent.parent / "verse_cache.json"
_BASE_URL   = "https://bible-api.com"
_TIMEOUT    = 6  # segundos

# (ref_url, referência_pt, texto_fallback_pt)
_VERSES = [
    ("john+3:16",         "João 3:16",
     "Porque Deus amou o mundo de tal maneira que deu o seu Filho unigênito, para que todo aquele que nele crê não pereça, mas tenha a vida eterna."),
    ("psalms+23:1",       "Salmos 23:1",
     "O Senhor é o meu pastor; nada me faltará."),
    ("philippians+4:13",  "Filipenses 4:13",
     "Tudo posso naquele que me fortalece."),
    ("romans+8:28",       "Romanos 8:28",
     "Sabemos que todas as coisas cooperam para o bem daqueles que amam a Deus, daqueles que são chamados segundo o seu propósito."),
    ("jeremiah+29:11",    "Jeremias 29:11",
     "Porque eu sei os planos que tenho para vós, diz o Senhor; planos de paz e não de calamidade, para vos dar um futuro e uma esperança."),
    ("proverbs+3:5",      "Provérbios 3:5",
     "Confia no Senhor de todo o teu coração e não te apoies no teu próprio entendimento."),
    ("isaiah+40:31",      "Isaías 40:31",
     "Mas os que esperam no Senhor renovarão as suas forças, subirão com asas como águias, correrão e não se cansarão, caminharão e não se fatigarão."),
    ("matthew+6:33",      "Mateus 6:33",
     "Mas buscai primeiro o Reino de Deus e a sua justiça, e todas essas coisas vos serão acrescentadas."),
    ("joshua+1:9",        "Josué 1:9",
     "Não to ordenei eu? Sê forte e corajoso. Não te apavores, nem te desanimes, porque o Senhor, teu Deus, estará contigo em todos os lugares aonde fores."),
    ("psalms+27:1",       "Salmos 27:1",
     "O Senhor é a minha luz e a minha salvação; a quem temerei? O Senhor é a força da minha vida; a quem me recearei?"),
    ("matthew+11:28",     "Mateus 11:28",
     "Vinde a mim, todos os que estais cansados e sobrecarregados, e eu vos darei descanso."),
    ("john+14:6",         "João 14:6",
     "Eu sou o caminho, a verdade e a vida. Ninguém vem ao Pai senão por mim."),
    ("psalms+46:1",       "Salmos 46:1",
     "Deus é o nosso refúgio e fortaleza, socorro bem presente nas tribulações."),
    ("2+timothy+1:7",     "2 Timóteo 1:7",
     "Porque Deus não nos deu o espírito de temor, mas de poder, de amor e de moderação."),
    ("1+john+4:8",        "1 João 4:8",
     "Aquele que não ama não conhece a Deus, porque Deus é amor."),
    ("psalms+119:105",    "Salmos 119:105",
     "A tua palavra é lâmpada que ilumina os meus passos e luz que clareia o meu caminho."),
    ("john+11:25",        "João 11:25",
     "Disse-lhe Jesus: Eu sou a ressurreição e a vida; quem crê em mim, ainda que morra, viverá."),
    ("romans+6:23",       "Romanos 6:23",
     "Porque o salário do pecado é a morte, mas o dom gratuito de Deus é a vida eterna em Cristo Jesus, nosso Senhor."),
    ("luke+1:37",         "Lucas 1:37",
     "Porque para Deus nada é impossível."),
    ("psalms+37:4",       "Salmos 37:4",
     "Deleita-te também no Senhor, e ele te concederá os desejos do teu coração."),
    ("hebrews+11:1",      "Hebreus 11:1",
     "A fé é a certeza daquilo que esperamos e a prova das coisas que não vemos."),
    ("john+15:13",        "João 15:13",
     "Ninguém tem maior amor do que este: dar a sua vida pelos seus amigos."),
    ("1+peter+5:7",       "1 Pedro 5:7",
     "Lançai sobre ele toda a vossa ansiedade, porque ele tem cuidado de vós."),
    ("isaiah+41:10",      "Isaías 41:10",
     "Não temas, porque eu sou contigo; não te assombres, porque eu sou teu Deus; eu te fortaleço, e te ajudo, e te sustento com a minha destra fiel."),
    ("philippians+4:6",  "Filipenses 4:6",
     "Não andeis ansiosos por coisa alguma; antes em tudo fazei conhecidas as vossas petições a Deus em oração e súplica, com ações de graças."),
    ("psalms+91:1",       "Salmos 91:1",
     "Aquele que habita no esconderijo do Altíssimo, à sombra do Onipotente descansará."),
    ("matthew+22:37",     "Mateus 22:37",
     "Amarás o Senhor, teu Deus, de todo o teu coração, de toda a tua alma e de todo o teu entendimento."),
    ("ephesians+2:8",     "Efésios 2:8",
     "Porque pela graça sois salvos, por meio da fé; e isso não vem de vós; é dom de Deus."),
    ("galatians+2:20",    "Gálatas 2:20",
     "Já estou crucificado com Cristo; e já não sou eu que vivo, mas Cristo vive em mim."),
    ("proverbs+18:10",    "Provérbios 18:10",
     "O nome do Senhor é uma torre forte; para ela corre o justo e fica protegido."),
    ("matthew+5:16",      "Mateus 5:16",
     "Assim brilhe a vossa luz diante dos homens, para que vejam as vossas boas obras e glorifiquem o vosso Pai que está nos céus."),
    ("ephesians+6:10",    "Efésios 6:10",
     "Finalmente, sede fortes no Senhor e na força do seu poder."),
    ("matthew+28:19",     "Mateus 28:19",
     "Portanto ide, fazei discípulos de todas as nações, batizando-os em nome do Pai, e do Filho, e do Espírito Santo."),
    ("psalms+34:8",       "Salmos 34:8",
     "Provai e vede que o Senhor é bom; bem-aventurado o homem que nele se refugia."),
    ("romans+10:9",       "Romanos 10:9",
     "Se com a tua boca confessares Jesus como Senhor e em teu coração creres que Deus o ressuscitou dentre os mortos, serás salvo."),
]


def _daily_entry():
    """Retorna a entrada do dia de forma determinística."""
    return _VERSES[date.today().toordinal() % len(_VERSES)]


def _load_cache():
    try:
        if _CACHE_FILE.exists():
            data = json.loads(_CACHE_FILE.read_text(encoding="utf-8"))
            if data.get("date") == str(date.today()):
                return data.get("verse")
    except Exception:
        pass
    return None


def _save_cache(verse):
    try:
        _CACHE_FILE.write_text(
            json.dumps({"date": str(date.today()), "verse": verse},
                       ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception:
        pass


def _fallback():
    _, reference, text = _daily_entry()
    return {"text": text, "reference": reference}


def _fetch():
    url_ref, _, _ = _daily_entry()
    url = f"{_BASE_URL}/{url_ref}?translation=almeida"
    req = urllib.request.Request(url, headers={"User-Agent": "SistemaGestao/1.0"})
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return {
        "text":      data["text"].strip(),
        "reference": data["reference"],
    }


def get_verse_of_day(callback):
    """
    Chama callback({"text": ..., "reference": ...}) com o versículo do dia.
    Ordem de prioridade: cache local → API → fallback embutido.
    A chamada à API é feita em background thread para não travar a UI.
    """
    cached = _load_cache()
    if cached:
        callback(cached)
        return

    def _worker():
        try:
            verse = _fetch()
        except Exception:
            verse = _fallback()
        _save_cache(verse)
        callback(verse)

    threading.Thread(target=_worker, daemon=True).start()
