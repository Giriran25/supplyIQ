"""One-time script to check import health of all route and service modules."""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

modules = [
    ("app.api.routes.copilot", "copilot route"),
    ("app.api.routes.suppliers", "suppliers route"),
    ("app.services.copilot", "copilot service"),
    ("app.services.data_generator", "data_generator service"),
    ("app.streamlit_app.app", "streamlit app"),
    ("app.models.supplier", "supplier model"),
    ("app.models.inventory", "inventory model"),
    ("app.models.trainer", "trainer model"),
    ("app.models.explainability", "explainability model"),
    ("app.models.model_registry", "model_registry model"),
]

for mod_path, label in modules:
    try:
        __import__(mod_path)
        print(f"  OK: {label}")
    except Exception as e:
        print(f"  FAIL: {label} -> {type(e).__name__}: {e}")
