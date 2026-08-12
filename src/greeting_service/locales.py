"""Locale catalogue, loaded exclusively from config/locales.yml.

One immutable in-memory catalogue, read once at startup and returned verbatim
(plan.md decision D4). Re-reading per request could serve two callers different
text within one deployment, which would breach GRT-002.

Loading failures abort startup (decision D3) so a broken catalogue never reaches
traffic.
"""

from pathlib import Path
from types import MappingProxyType
from typing import Mapping

import yaml

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "locales.yml"


class LocaleConfigError(RuntimeError):
    """Raised when config/locales.yml cannot be used as a catalogue."""


def load_catalogue(path: Path | None = None) -> Mapping[str, str]:
    """Load and validate the catalogue. Raises LocaleConfigError on any problem."""
    source = Path(path) if path is not None else CONFIG_PATH

    try:
        raw = yaml.safe_load(source.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise LocaleConfigError(f"{source} not found") from exc
    except yaml.YAMLError as exc:
        raise LocaleConfigError(f"{source} is not valid YAML: {exc}") from exc

    if not isinstance(raw, dict) or not raw:
        raise LocaleConfigError(f"{source} must contain a non-empty mapping")

    for language, greeting in raw.items():
        if not isinstance(language, str) or not language:
            raise LocaleConfigError(f"{source} has a non-string language key: {language!r}")
        if not isinstance(greeting, str) or not greeting.strip():
            raise LocaleConfigError(f"{source} has empty greeting text for {language!r}")

    # Immutable: nothing downstream may mutate the catalogue and cause one
    # caller to see different text from another (GRT-002).
    return MappingProxyType(dict(raw))
