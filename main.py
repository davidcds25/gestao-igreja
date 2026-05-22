import sys
from pathlib import Path

# Quando rodando como .exe, garante que config.py ao lado do executável seja importável
if getattr(sys, 'frozen', False):
    _exe_dir = str(Path(sys.executable).parent)
    if _exe_dir not in sys.path:
        sys.path.insert(0, _exe_dir)

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
    from core.database import init_database
    from views.login import LoginWindow
    init_database()
    LoginWindow(root)


if __name__ == "__main__":
    main()
