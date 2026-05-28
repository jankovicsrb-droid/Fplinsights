"""CLI entry: `python -m scripts.update`."""
from fpl_insights.pipeline.update import update_fpl_data


if __name__ == "__main__":
    update_fpl_data()
