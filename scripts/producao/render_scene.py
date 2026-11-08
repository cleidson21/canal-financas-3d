"""Retired entry point for the unverified PROD-002 frame cache."""


def main(*_args):
    raise SystemExit(
        "Legacy PNG cache disabled. Use scripts/producao/render_plan.py with a plan JSON "
        "and render its --audit frames first."
    )


if __name__ == "__main__":
    main()
