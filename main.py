"""
Arquivo principal do aplicativo
Ponto de entrada da aplicação
"""

import sys
from core.database import init_database
from views.login import main

if __name__ == "__main__":
    init_database()
    main()
