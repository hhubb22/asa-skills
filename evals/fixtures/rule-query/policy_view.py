"""Synthetic evaluation fixture with an intentional observation fallback defect."""


def render_rule(configured: str, observed: str | None, error: str | None = None) -> dict:
    return {
        "configured_action": configured,
        "observed_action": observed or configured,
        "reason": error,
    }
