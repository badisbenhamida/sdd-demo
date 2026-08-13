"""Locale table, loaded from config/locales.yml.

That file is the only source of greeting text (plan.md design D-5, research
R-6). Nothing here supplies a greeting, not even as a last-resort default:
a code-side fallback would quietly break GRT-004, since some deployments
would answer from config and others from source with nothing to reveal
which. When the config cannot supply a usable table, this module raises
and the service reports itself unavailable instead of inventing text.
"""

from pathlib import Path
from typing import Dict, Optional

import yaml

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "locales.yml"

# The identifier is a constant; its text is not (AMB-002 ruling, design D-6).
DEFAULT_LANGUAGE = "en"


class LocaleConfigError(RuntimeError):
    """config/locales.yml cannot supply a usable locale table."""


def load_locales(path: Optional[Path] = None) -> Dict[str, str]:
    """Read and validate the locale table.

    Validation rules are data-model.md's; each maps to a way the service
    could otherwise appear healthy while serving nothing usable.
    """
    path = path or CONFIG_PATH

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise LocaleConfigError("{} not found".format(path)) from exc
    except yaml.YAMLError as exc:
        raise LocaleConfigError("{} is not valid YAML".format(path)) from exc

    locales = (raw or {}).get("locales") if isinstance(raw, dict) else None
    if not isinstance(locales, dict) or not locales:
        raise LocaleConfigError("{} defines no locales".format(path))

    for language, message in locales.items():
        # An empty message would satisfy "a greeting was returned"
        # mechanically while showing the end user nothing — the silent
        # failure GRT-005's fallback notice exists to prevent.
        if not isinstance(message, str) or not message.strip():
            raise LocaleConfigError(
                "{}: locale '{}' has no message text".format(path, language)
            )

    if DEFAULT_LANGUAGE not in locales:
        # Without it, GRT-002 and the GRT-005 fallback have no target.
        raise LocaleConfigError(
            "{}: default language '{}' is missing".format(path, DEFAULT_LANGUAGE)
        )

    return dict(locales)
