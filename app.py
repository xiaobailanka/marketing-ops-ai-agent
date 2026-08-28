"""Marketing Operations Workspace 统一入口。"""

from __future__ import annotations

from src.ui.layout import configure_app, finish_app_shell
from src.ui.navigation import build_navigation


configure_app()
navigation = build_navigation()
finish_app_shell()
navigation.run()
