import sys
import platform
import traceback
from datetime import datetime
from pathlib import Path


def _log_path() -> Path:
    base = (Path(sys.executable).parent
            if getattr(sys, 'frozen', False)
            else Path(__file__).parent.parent)
    return base / "crash.log"


def _write(exc_type, exc_value, exc_tb) -> Path:
    path = _log_path()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tb_lines = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))

    with open(path, "a", encoding="utf-8") as f:
        f.write(f"\n{'=' * 60}\n")
        f.write(f"CRASH — {timestamp}\n")
        f.write(f"Python {sys.version}\n")
        f.write(f"Plataforma: {platform.system()} {platform.release()} ({platform.machine()})\n")
        f.write(f"{'=' * 60}\n")
        f.write(tb_lines)

    return path


def _show_dialog(exc_type, exc_value, log_path: Path):
    try:
        import tkinter as tk
        from tkinter import messagebox
        msg = (
            f"O aplicativo encontrou um erro inesperado e precisa fechar.\n\n"
            f"Um relatório foi salvo em:\n{log_path}\n\n"
            f"Erro: {exc_type.__name__}: {exc_value}"
        )
        existing = tk._default_root
        if existing:
            messagebox.showerror("Erro Inesperado", msg, parent=existing)
        else:
            _r = tk.Tk()
            _r.withdraw()
            messagebox.showerror("Erro Inesperado", msg, parent=_r)
            _r.destroy()
    except Exception:
        pass


def install():
    def _handler(exc_type, exc_value, exc_tb):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb)
            return
        log = _write(exc_type, exc_value, exc_tb)
        _show_dialog(exc_type, exc_value, log)
        sys.__excepthook__(exc_type, exc_value, exc_tb)

    sys.excepthook = _handler
