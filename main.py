import sys
import os
from pathlib import Path

# Quando rodando como .exe, garante que config.py ao lado do executável seja importável
if getattr(sys, 'frozen', False):
    _exe_dir = str(Path(sys.executable).parent)
    if _exe_dir not in sys.path:
        sys.path.insert(0, _exe_dir)

    # Ajuda python-vlc a achar a libvlc.dll nas pastas padrão do Windows
    # (necessário quando o PATH não está configurado ou o VLC foi recém-instalado)
    for _vlc_dir in (
        r"C:\Program Files\VideoLAN\VLC",
        r"C:\Program Files (x86)\VideoLAN\VLC",
    ):
        if os.path.isfile(os.path.join(_vlc_dir, "libvlc.dll")):
            os.environ.setdefault("PYTHON_VLC_LIB_PATH",
                                  os.path.join(_vlc_dir, "libvlc.dll"))
            # Adiciona ao PATH para que o VLC carregue seus plugins corretamente
            os.environ["PATH"] = _vlc_dir + os.pathsep + os.environ.get("PATH", "")
            break

from core.crash_logger import install as _install_crash_handler
_install_crash_handler()


def _config_exists() -> bool:
    try:
        import config  # noqa: F401
        return True
    except ImportError:
        return False


def main():
    import tkinter as tk

    root = tk.Tk()

    # Captura exceções em callbacks tkinter no mesmo log
    def _tk_error(exc, val, tb):
        import sys
        sys.excepthook(type(val), val, tb)

    root.report_callback_exception = _tk_error

    if not _config_exists():
        from views.setup import SetupWizard

        def _after_setup():
            _launch(root)

        SetupWizard(root, on_complete=_after_setup)
    else:
        _launch(root)

    root.mainloop()


def _launch(root):
    # Aplica o tema salvo ANTES de qualquer módulo de UI ser importado,
    # pois tokens.COLORS é mutado em-place e todos os imports posteriores
    # já enxergam as cores corretas.
    import json
    from pathlib import Path
    _prefs_file = Path(__file__).parent / "user_prefs.json"
    try:
        _theme = json.loads(_prefs_file.read_text(encoding="utf-8")).get("theme", "dark")
    except Exception:
        _theme = "dark"
    from design.ui.tokens import set_theme
    set_theme(_theme)

    from core.database import init_database
    from core.assets import aplicar_icone_janela
    from views.login import LoginWindow
    init_database()
    aplicar_icone_janela(root)
    LoginWindow(root)


if __name__ == "__main__":
    main()
