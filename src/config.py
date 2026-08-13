"""Locale catalog loading — the only module in src/ that touches the disk.

All greeting content comes from config/locales.yml and nowhere else. There is
deliberately no fallback string anywhere in this package: a safety-net literal
would satisfy the greeting tests while silently breaking the config-exclusivity
constraint and masking the very state the health signal exists to expose
(specs/001-greeting-service/research.md R-4).

A load failure is captured, not raised. The service must be able to start and
report that it cannot greet — a crash would leave nothing running to report it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "locales.yml"


@dataclass(frozen=True)
class LocaleCatalog:
    """The whole of the service's data, built once at startup.

    `greetings` and `display_names` are keyed by the NORMALISED (lowercased)
    locale. Folding happens here and only here, so no call site can
    reintroduce case sensitivity by forgetting to fold.
    """

    default: str = ""
    greetings: dict[str, str] = field(default_factory=dict)
    display_names: dict[str, str] = field(default_factory=dict)
    loaded: bool = False
    error: str | None = None

    @property
    def default_display(self) -> str:
        """The default locale in its configured spelling."""
        return self.display_names.get(self.default, self.default)


def _failed(reason: str) -> LocaleCatalog:
    return LocaleCatalog(loaded=False, error=reason)


def load_catalog(path: Path = CONFIG_PATH) -> LocaleCatalog:
    """Build the catalog from `path`, or return a not-loaded catalog saying why.

    Validation follows specs/001-greeting-service/data-model.md. Every failure
    path yields the same observable outcome — `loaded=False` — because the
    service's behaviour does not vary by which way the config was wrong.
    """
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return _failed(f"{path.name} not found")
    except OSError as exc:
        return _failed(f"{path.name} unreadable: {exc}")
    except yaml.YAMLError as exc:
        return _failed(f"{path.name} is not valid YAML: {exc}")

    if not isinstance(raw, dict):
        return _failed(f"{path.name} must contain a mapping at the top level")

    entries = raw.get("locales")
    if not isinstance(entries, dict) or not entries:
        return _failed(f"{path.name} must define a non-empty 'locales' mapping")

    greetings: dict[str, str] = {}
    display_names: dict[str, str] = {}
    for name, text in entries.items():
        # A configured locale with no text behind it is not supported. Dropping
        # it here is what makes requests for it fall back (GRT-005) instead of
        # returning an empty greeting.
        if not isinstance(name, str) or not isinstance(text, str) or not text:
            continue
        key = name.lower()
        greetings[key] = text
        display_names[key] = name

    if not greetings:
        return _failed(f"{path.name} defines no locale with greeting text")

    default = raw.get("default")
    if not isinstance(default, str) or not default:
        return _failed(f"{path.name} must define a 'default' locale")

    default_key = default.lower()
    if default_key not in greetings:
        # Half-working is worse than unhealthy: with an absent default, both
        # the no-preference path and the fallback path would resolve to
        # nothing at request time.
        return _failed(
            f"default locale '{default}' is not among the configured locales"
        )

    return LocaleCatalog(
        default=default_key,
        greetings=greetings,
        display_names=display_names,
        loaded=True,
    )
