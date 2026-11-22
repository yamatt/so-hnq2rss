import html
import json
from datetime import UTC, datetime
from pathlib import Path

import click
from feedgen.feed import FeedGenerator


@click.command()
@click.argument(
    "json_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.argument(
    "output_path",
    default="public/feed.xml",
    type=click.Path(dir_okay=False, path_type=Path),
    help="Output path for the generated RSS XML file.",
)
def build_feed(json_path: Path, output_path: Path) -> None:
    """Convert a Stack Exchange Hot Network Questions JSON file into an RSS feed."""
    questions = json.loads(json_path.read_text(encoding="utf-8"))

    fg = FeedGenerator()
    fg.title("Stack Exchange Hot Network Questions")
    fg.link(href="https://stackexchange.com/questions", rel="alternate")
    fg.description("Daily digest of Hot Network Questions across Stack Exchange")
    fg.language("en")
    fg.lastBuildDate(datetime.now(UTC))

    for q in questions:
        link = f"https://{q['site']}/q/{q['question_id']}"
        tags = ", ".join(q.get("tags", []))

        # Preserve Stack Exchange's native hotness order
        fe = fg.add_entry(order="append")
        fe.id(link)
        fe.title(f"[{q['site']}] {q['title']}")
        fe.link(href=link)
        fe.description(f"Site: {q['site']} | Tags: {tags}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fg.rss_file(str(output_path))
    click.echo(f"Generated RSS feed with {len(questions)} items at {output_path}")


if __name__ == "__main__":
    build_feed()
