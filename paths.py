import os
import sys

FROZEN = getattr(sys, "frozen", False)


def resource_path(*parts):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, *parts)


def save_path(filename):
    if FROZEN:
        folder = os.path.join(
            os.environ.get("APPDATA") or os.path.dirname(sys.executable), "Peak"
        )
        try:
            os.makedirs(folder, exist_ok=True)
        except OSError:
            folder = os.path.dirname(sys.executable)
        return os.path.join(folder, filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
