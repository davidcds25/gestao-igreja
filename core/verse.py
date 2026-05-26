"""
Versículo do dia e busca sob demanda.
Usa scripture.api.bible (autenticado) quando BIBLE_API_KEY + BIBLE_ID estão
configurados; fallback para lista local em PT se a API falhar ou não estiver
configurada.
"""

import json
import re
import threading
import urllib.request
from datetime import date
from pathlib import Path

_CACHE_FILE    = Path(__file__).parent.parent / "verse_cache.json"
_PREFS_FILE    = Path(__file__).parent.parent / "user_prefs.json"
_TIMEOUT       = 8
_SCRIPTURE_URL = "https://rest.api.bible/v1/bibles"

try:
    from config import BIBLE_API_KEY, BIBLE_ID as _CONFIG_BIBLE_ID
except ImportError:
    BIBLE_API_KEY    = ""
    _CONFIG_BIBLE_ID = ""

# Lista canônica dos 66 livros — nome PT, código USFM e número de capítulos
LIVROS_BIBLIA = [
    {"nome": "Gênesis",           "usfm": "GEN", "caps": 50},
    {"nome": "Êxodo",             "usfm": "EXO", "caps": 40},
    {"nome": "Levítico",          "usfm": "LEV", "caps": 27},
    {"nome": "Números",           "usfm": "NUM", "caps": 36},
    {"nome": "Deuteronômio",      "usfm": "DEU", "caps": 34},
    {"nome": "Josué",             "usfm": "JOS", "caps": 24},
    {"nome": "Juízes",            "usfm": "JDG", "caps": 21},
    {"nome": "Rute",              "usfm": "RUT", "caps": 4},
    {"nome": "1 Samuel",          "usfm": "1SA", "caps": 31},
    {"nome": "2 Samuel",          "usfm": "2SA", "caps": 24},
    {"nome": "1 Reis",            "usfm": "1KI", "caps": 22},
    {"nome": "2 Reis",            "usfm": "2KI", "caps": 25},
    {"nome": "1 Crônicas",        "usfm": "1CH", "caps": 29},
    {"nome": "2 Crônicas",        "usfm": "2CH", "caps": 36},
    {"nome": "Esdras",            "usfm": "EZR", "caps": 10},
    {"nome": "Neemias",           "usfm": "NEH", "caps": 13},
    {"nome": "Ester",             "usfm": "EST", "caps": 10},
    {"nome": "Jó",                "usfm": "JOB", "caps": 42},
    {"nome": "Salmos",            "usfm": "PSA", "caps": 150},
    {"nome": "Provérbios",        "usfm": "PRO", "caps": 31},
    {"nome": "Eclesiastes",       "usfm": "ECC", "caps": 12},
    {"nome": "Cantares",          "usfm": "SNG", "caps": 8},
    {"nome": "Isaías",            "usfm": "ISA", "caps": 66},
    {"nome": "Jeremias",          "usfm": "JER", "caps": 52},
    {"nome": "Lamentações",       "usfm": "LAM", "caps": 5},
    {"nome": "Ezequiel",          "usfm": "EZK", "caps": 48},
    {"nome": "Daniel",            "usfm": "DAN", "caps": 12},
    {"nome": "Oséias",            "usfm": "HOS", "caps": 14},
    {"nome": "Joel",              "usfm": "JOL", "caps": 3},
    {"nome": "Amós",              "usfm": "AMO", "caps": 9},
    {"nome": "Obadias",           "usfm": "OBA", "caps": 1},
    {"nome": "Jonas",             "usfm": "JON", "caps": 4},
    {"nome": "Miquéias",          "usfm": "MIC", "caps": 7},
    {"nome": "Naum",              "usfm": "NAM", "caps": 3},
    {"nome": "Habacuque",         "usfm": "HAB", "caps": 3},
    {"nome": "Sofonias",          "usfm": "ZEP", "caps": 3},
    {"nome": "Ageu",              "usfm": "HAG", "caps": 2},
    {"nome": "Zacarias",          "usfm": "ZEC", "caps": 14},
    {"nome": "Malaquias",         "usfm": "MAL", "caps": 4},
    {"nome": "Mateus",            "usfm": "MAT", "caps": 28},
    {"nome": "Marcos",            "usfm": "MRK", "caps": 16},
    {"nome": "Lucas",             "usfm": "LUK", "caps": 24},
    {"nome": "João",              "usfm": "JHN", "caps": 21},
    {"nome": "Atos",              "usfm": "ACT", "caps": 28},
    {"nome": "Romanos",           "usfm": "ROM", "caps": 16},
    {"nome": "1 Coríntios",       "usfm": "1CO", "caps": 16},
    {"nome": "2 Coríntios",       "usfm": "2CO", "caps": 13},
    {"nome": "Gálatas",           "usfm": "GAL", "caps": 6},
    {"nome": "Efésios",           "usfm": "EPH", "caps": 6},
    {"nome": "Filipenses",        "usfm": "PHP", "caps": 4},
    {"nome": "Colossenses",       "usfm": "COL", "caps": 4},
    {"nome": "1 Tessalonicenses", "usfm": "1TH", "caps": 5},
    {"nome": "2 Tessalonicenses", "usfm": "2TH", "caps": 3},
    {"nome": "1 Timóteo",         "usfm": "1TI", "caps": 6},
    {"nome": "2 Timóteo",         "usfm": "2TI", "caps": 4},
    {"nome": "Tito",              "usfm": "TIT", "caps": 3},
    {"nome": "Filemon",           "usfm": "PHM", "caps": 1},
    {"nome": "Hebreus",           "usfm": "HEB", "caps": 13},
    {"nome": "Tiago",             "usfm": "JAS", "caps": 5},
    {"nome": "1 Pedro",           "usfm": "1PE", "caps": 5},
    {"nome": "2 Pedro",           "usfm": "2PE", "caps": 3},
    {"nome": "1 João",            "usfm": "1JN", "caps": 5},
    {"nome": "2 João",            "usfm": "2JN", "caps": 1},
    {"nome": "3 João",            "usfm": "3JN", "caps": 1},
    {"nome": "Judas",             "usfm": "JUD", "caps": 1},
    {"nome": "Apocalipse",        "usfm": "REV", "caps": 22},
]

# Traduções PT disponíveis no plano gratuito de api.bible
BIBLE_TRANSLATIONS = [
    {"label": "NVI Portuguesa",         "id": "35b94e98b2e3a01a-01"},
    {"label": "Nova Versão Transformadora", "id": "41a6caa722a21d88-01"},
    {"label": "NVI Moçambique 2024",    "id": "a47cbe7792801aa8-01"},
]


def get_bible_id() -> str:
    """Retorna o BIBLE_ID ativo: user_prefs.json → config.py → ""."""
    try:
        if _PREFS_FILE.exists():
            prefs = json.loads(_PREFS_FILE.read_text(encoding="utf-8"))
            if prefs.get("bible_id"):
                return prefs["bible_id"]
    except Exception:
        pass
    return _CONFIG_BIBLE_ID


def set_bible_id(new_id: str):
    """Salva a preferência de tradução em user_prefs.json e invalida o cache."""
    try:
        prefs = {}
        if _PREFS_FILE.exists():
            prefs = json.loads(_PREFS_FILE.read_text(encoding="utf-8"))
        prefs["bible_id"] = new_id
        _PREFS_FILE.write_text(
            json.dumps(prefs, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        # invalida cache do versículo do dia para recarregar com nova tradução
        if _CACHE_FILE.exists():
            _CACHE_FILE.unlink()
    except Exception:
        pass

# (usfm_id, referência_pt, texto_fallback)
_VERSES = [
    ("JHN.3.16",      "João 3:16",
     "Porque Deus amou o mundo de tal maneira que deu o seu Filho unigênito, para que todo aquele que nele crê não pereça, mas tenha a vida eterna."),
    ("PSA.23.1",      "Salmos 23:1",
     "O Senhor é o meu pastor; nada me faltará."),
    ("PHP.4.13",      "Filipenses 4:13",
     "Tudo posso naquele que me fortalece."),
    ("ROM.8.28",      "Romanos 8:28",
     "Sabemos que todas as coisas cooperam para o bem daqueles que amam a Deus, daqueles que são chamados segundo o seu propósito."),
    ("JER.29.11",     "Jeremias 29:11",
     "Porque eu sei os planos que tenho para vós, diz o Senhor; planos de paz e não de calamidade, para vos dar um futuro e uma esperança."),
    ("PRO.3.5",       "Provérbios 3:5",
     "Confia no Senhor de todo o teu coração e não te apoies no teu próprio entendimento."),
    ("ISA.40.31",     "Isaías 40:31",
     "Mas os que esperam no Senhor renovarão as suas forças, subirão com asas como águias, correrão e não se cansarão, caminharão e não se fatigarão."),
    ("MAT.6.33",      "Mateus 6:33",
     "Mas buscai primeiro o Reino de Deus e a sua justiça, e todas essas coisas vos serão acrescentadas."),
    ("JOS.1.9",       "Josué 1:9",
     "Não to ordenei eu? Sê forte e corajoso. Não te apavores, nem te desanimes, porque o Senhor, teu Deus, estará contigo em todos os lugares aonde fores."),
    ("PSA.27.1",      "Salmos 27:1",
     "O Senhor é a minha luz e a minha salvação; a quem temerei? O Senhor é a força da minha vida; a quem me recearei?"),
    ("MAT.11.28",     "Mateus 11:28",
     "Vinde a mim, todos os que estais cansados e sobrecarregados, e eu vos darei descanso."),
    ("JHN.14.6",      "João 14:6",
     "Eu sou o caminho, a verdade e a vida. Ninguém vem ao Pai senão por mim."),
    ("PSA.46.1",      "Salmos 46:1",
     "Deus é o nosso refúgio e fortaleza, socorro bem presente nas tribulações."),
    ("2TI.1.7",       "2 Timóteo 1:7",
     "Porque Deus não nos deu o espírito de temor, mas de poder, de amor e de moderação."),
    ("1JN.4.8",       "1 João 4:8",
     "Aquele que não ama não conhece a Deus, porque Deus é amor."),
    ("PSA.119.105",   "Salmos 119:105",
     "A tua palavra é lâmpada que ilumina os meus passos e luz que clareia o meu caminho."),
    ("JHN.11.25",     "João 11:25",
     "Disse-lhe Jesus: Eu sou a ressurreição e a vida; quem crê em mim, ainda que morra, viverá."),
    ("ROM.6.23",      "Romanos 6:23",
     "Porque o salário do pecado é a morte, mas o dom gratuito de Deus é a vida eterna em Cristo Jesus, nosso Senhor."),
    ("LUK.1.37",      "Lucas 1:37",
     "Porque para Deus nada é impossível."),
    ("PSA.37.4",      "Salmos 37:4",
     "Deleita-te também no Senhor, e ele te concederá os desejos do teu coração."),
    ("HEB.11.1",      "Hebreus 11:1",
     "A fé é a certeza daquilo que esperamos e a prova das coisas que não vemos."),
    ("JHN.15.13",     "João 15:13",
     "Ninguém tem maior amor do que este: dar a sua vida pelos seus amigos."),
    ("1PE.5.7",       "1 Pedro 5:7",
     "Lançai sobre ele toda a vossa ansiedade, porque ele tem cuidado de vós."),
    ("ISA.41.10",     "Isaías 41:10",
     "Não temas, porque eu sou contigo; não te assombres, porque eu sou teu Deus; eu te fortaleço, e te ajudo, e te sustento com a minha destra fiel."),
    ("PHP.4.6",       "Filipenses 4:6",
     "Não andeis ansiosos por coisa alguma; antes em tudo fazei conhecidas as vossas petições a Deus em oração e súplica, com ações de graças."),
    ("PSA.91.1",      "Salmos 91:1",
     "Aquele que habita no esconderijo do Altíssimo, à sombra do Onipotente descansará."),
    ("MAT.22.37",     "Mateus 22:37",
     "Amarás o Senhor, teu Deus, de todo o teu coração, de toda a tua alma e de todo o teu entendimento."),
    ("EPH.2.8",       "Efésios 2:8",
     "Porque pela graça sois salvos, por meio da fé; e isso não vem de vós; é dom de Deus."),
    ("GAL.2.20",      "Gálatas 2:20",
     "Já estou crucificado com Cristo; e já não sou eu que vivo, mas Cristo vive em mim."),
    ("PRO.18.10",     "Provérbios 18:10",
     "O nome do Senhor é uma torre forte; para ela corre o justo e fica protegido."),
    ("MAT.5.16",      "Mateus 5:16",
     "Assim brilhe a vossa luz diante dos homens, para que vejam as vossas boas obras e glorifiquem o vosso Pai que está nos céus."),
    ("EPH.6.10",      "Efésios 6:10",
     "Finalmente, sede fortes no Senhor e na força do seu poder."),
    ("MAT.28.19",     "Mateus 28:19",
     "Portanto ide, fazei discípulos de todas as nações, batizando-os em nome do Pai, e do Filho, e do Espírito Santo."),
    ("PSA.34.8",      "Salmos 34:8",
     "Provai e vede que o Senhor é bom; bem-aventurado o homem que nele se refugia."),
    ("ROM.10.9",      "Romanos 10:9",
     "Se com a tua boca confessares Jesus como Senhor e em teu coração creres que Deus o ressuscitou dentre os mortos, serás salvo."),
]

# Mapeamento de nomes PT (normalizados) → código USFM
_LIVROS_PT = {
    "gênesis": "GEN", "genesis": "GEN", "gn": "GEN",
    "êxodo": "EXO", "exodo": "EXO", "ex": "EXO",
    "levítico": "LEV", "levitico": "LEV", "lv": "LEV",
    "números": "NUM", "numeros": "NUM", "nm": "NUM",
    "deuteronômio": "DEU", "deuteronomio": "DEU", "dt": "DEU",
    "josué": "JOS", "josue": "JOS", "js": "JOS",
    "juízes": "JDG", "juizes": "JDG",
    "rute": "RUT", "rt": "RUT",
    "1 samuel": "1SA", "1samuel": "1SA", "1sm": "1SA",
    "2 samuel": "2SA", "2samuel": "2SA", "2sm": "2SA",
    "1 reis": "1KI", "1reis": "1KI",
    "2 reis": "2KI", "2reis": "2KI",
    "1 crônicas": "1CH", "1 cronicas": "1CH",
    "2 crônicas": "2CH", "2 cronicas": "2CH",
    "esdras": "EZR",
    "neemias": "NEH",
    "ester": "EST",
    "jó": "JOB", "jo": "JOB",
    "salmos": "PSA", "sl": "PSA",
    "provérbios": "PRO", "proverbios": "PRO", "pv": "PRO",
    "eclesiastes": "ECC",
    "cantares": "SNG",
    "isaías": "ISA", "isaias": "ISA", "is": "ISA",
    "jeremias": "JER", "jr": "JER",
    "lamentações": "LAM", "lamentacoes": "LAM",
    "ezequiel": "EZK", "ez": "EZK",
    "daniel": "DAN", "dn": "DAN",
    "oséias": "HOS", "oseias": "HOS",
    "joel": "JOL",
    "amós": "AMO", "amos": "AMO",
    "obadias": "OBA",
    "jonas": "JON",
    "miquéias": "MIC", "miqueias": "MIC",
    "naum": "NAM",
    "habacuque": "HAB",
    "sofonias": "ZEP",
    "ageu": "HAG",
    "zacarias": "ZEC",
    "malaquias": "MAL",
    "mateus": "MAT", "mt": "MAT",
    "marcos": "MRK", "mc": "MRK",
    "lucas": "LUK", "lc": "LUK",
    "joão": "JHN", "joao": "JHN",
    "atos": "ACT", "at": "ACT",
    "romanos": "ROM", "rm": "ROM",
    "1 coríntios": "1CO", "1 corintios": "1CO", "1co": "1CO",
    "2 coríntios": "2CO", "2 corintios": "2CO", "2co": "2CO",
    "gálatas": "GAL", "galatas": "GAL", "gl": "GAL",
    "efésios": "EPH", "efesios": "EPH", "ef": "EPH",
    "filipenses": "PHP", "fp": "PHP",
    "colossenses": "COL", "cl": "COL",
    "1 tessalonicenses": "1TH", "1ts": "1TH",
    "2 tessalonicenses": "2TH", "2ts": "2TH",
    "1 timóteo": "1TI", "1 timoteo": "1TI", "1tm": "1TI",
    "2 timóteo": "2TI", "2 timoteo": "2TI", "2tm": "2TI",
    "tito": "TIT",
    "filemon": "PHM", "filemom": "PHM",
    "hebreus": "HEB", "hb": "HEB",
    "tiago": "JAS",
    "1 pedro": "1PE",
    "2 pedro": "2PE",
    "1 joão": "1JN", "1 joao": "1JN",
    "2 joão": "2JN", "2 joao": "2JN",
    "3 joão": "3JN", "3 joao": "3JN",
    "judas": "JUD",
    "apocalipse": "REV", "ap": "REV",
}


def _daily_entry():
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


def _fallback_daily():
    _, ref, text = _daily_entry()
    return {"text": text, "reference": ref}


def _scripture_get(path: str) -> dict:
    url = f"{_SCRIPTURE_URL}/{get_bible_id()}/{path}"
    req = urllib.request.Request(url, headers={
        "api-key": BIBLE_API_KEY,
        "User-Agent": "SistemaGestao/1.0",
    })
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


_PASSAGE_PARAMS = (
    "?content-type=text"
    "&include-notes=false"
    "&include-titles=false"
    "&include-chapter-numbers=false"
    "&include-verse-numbers=false"
    "&include-verse-spans=false"
)


def _fetch_daily():
    usfm_id, ref_pt, _ = _daily_entry()
    data = _scripture_get(f"passages/{usfm_id}{_PASSAGE_PARAMS}")
    text = data["data"]["content"].strip()
    return {"text": text, "reference": ref_pt}


def get_verse_of_day(callback):
    """
    Chama callback({"text": ..., "reference": ...}) com o versículo do dia.
    Ordem: cache local → API → fallback embutido.
    Chamada à API feita em background thread.
    """
    cached = _load_cache()
    if cached:
        callback(cached)
        return

    def _worker():
        try:
            verse = _fetch_daily() if (BIBLE_API_KEY and get_bible_id()) else _fallback_daily()
        except Exception:
            verse = _fallback_daily()
        _save_cache(verse)
        callback(verse)

    threading.Thread(target=_worker, daemon=True).start()


def _parse_ref(ref_str: str):
    """
    'João 3:16' → ('JHN', 'JHN.3.16', 'João 3:16')
    'Salmos 23:1-3' → ('PSA', 'PSA.23.1-PSA.23.3', 'Salmos 23:1-3')
    Retorna None se não reconhecido.
    """
    m = re.match(r'^(.+)\s+(\d+):(\d+)(?:-(\d+))?$', ref_str.strip(), re.IGNORECASE)
    if not m:
        return None
    book_raw, cap, ver_ini, ver_fim = m.group(1), m.group(2), m.group(3), m.group(4)

    book_key = book_raw.lower().strip()
    usfm = _LIVROS_PT.get(book_key)
    if not usfm:
        return None

    if ver_fim:
        passage_id = f"{usfm}.{cap}.{ver_ini}-{usfm}.{cap}.{ver_fim}"
    else:
        passage_id = f"{usfm}.{cap}.{ver_ini}"

    return usfm, passage_id, ref_str.strip()


def buscar_versiculo(referencia_pt: str, callback):
    """
    Busca versículo por referência PT sob demanda. Requer BIBLE_API_KEY + BIBLE_ID.
    callback({"text": ..., "reference": ...}) ou callback({"error": "mensagem"})
    """
    if not BIBLE_API_KEY or not get_bible_id():
        callback({"error": "Configure BIBLE_API_KEY e BIBLE_ID no config.py para buscar versículos."})
        return

    parsed = _parse_ref(referencia_pt)
    if not parsed:
        callback({"error": f"Referência não reconhecida: '{referencia_pt}'.\nExemplos: João 3:16 · Salmos 23:1 · Romanos 8:28"})
        return

    _, passage_id, ref_display = parsed

    def _worker():
        try:
            data = _scripture_get(f"passages/{passage_id}{_PASSAGE_PARAMS}")
            text = data["data"]["content"].strip()
            callback({"text": text, "reference": ref_display})
        except Exception as exc:
            callback({"error": f"Erro ao buscar versículo: {exc}"})

    threading.Thread(target=_worker, daemon=True).start()


def buscar_por_usfm(usfm: str, cap: int, ver: int, nome_livro: str, callback):
    """
    Busca versículo diretamente pelo código USFM (sem parsear texto PT).
    Mais rápido e confiável para uso com o seletor de livros.
    callback({"text": ..., "reference": ...}) ou callback({"error": "mensagem"})
    """
    if not BIBLE_API_KEY or not get_bible_id():
        callback({"error": "Configure BIBLE_API_KEY e BIBLE_ID no config.py para buscar versículos."})
        return

    passage_id  = f"{usfm}.{cap}.{ver}"
    ref_display = f"{nome_livro} {cap}:{ver}"

    def _worker():
        try:
            data = _scripture_get(f"passages/{passage_id}{_PASSAGE_PARAMS}")
            text = data["data"]["content"].strip()
            callback({"text": text, "reference": ref_display})
        except Exception as exc:
            callback({"error": f"Erro ao buscar versículo: {exc}"})

    threading.Thread(target=_worker, daemon=True).start()
