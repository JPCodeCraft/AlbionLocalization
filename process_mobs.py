import argparse
import json
from contextlib import contextmanager
from pathlib import Path
from typing import Any, BinaryIO, Dict, Iterator, List
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


DEFAULT_SOURCE = "https://raw.githubusercontent.com/ao-data/ao-bin-dumps/refs/heads/master/mobs.xml"
DEFAULT_OUTPUT = "processed_mobs.json"
DEFAULT_LOCALIZATION = "localization.json"
DEFAULT_LANGUAGE = "EN-US"
DEFAULT_MOB_ID_OFFSET = 15


@contextmanager
def open_xml_source(source: str) -> Iterator[BinaryIO]:
    parsed = urlparse(source)

    if parsed.scheme in {"http", "https"}:
        request = Request(source, headers={"User-Agent": "AlbionLocalization/1.0"})
        with urlopen(request, timeout=60) as response:
            yield response
        return

    with Path(source).open("rb") as file:
        yield file


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def ensure_array(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def load_localization(language: str, localization_path: str = DEFAULT_LOCALIZATION) -> Dict[str, Any]:
    with Path(localization_path).open("r", encoding="utf-8-sig") as file:
        data = json.load(file)

    entries = ensure_array(data.get("tmx", {}).get("body", {}).get("tu"))
    localization = {}

    for entry in entries:
        if not isinstance(entry, dict):
            continue

        tuid = entry.get("@tuid")
        if not tuid:
            continue

        for tuv in ensure_array(entry.get("tuv")):
            if not isinstance(tuv, dict):
                continue
            if tuv.get("@xml:lang") == language and "seg" in tuv:
                localization[tuid] = tuv["seg"]
                break

    return localization


def get_localized_name(
    localization: Dict[str, Any],
    unique_name: str,
    name_loca_tag: str | None,
) -> Any:
    candidates = []

    if name_loca_tag:
        candidates.append(name_loca_tag)
        if not name_loca_tag.startswith("@"):
            candidates.append(f"@{name_loca_tag}")

    candidates.extend([
        f"@MOB_{unique_name}",
        f"@{unique_name}",
    ])

    for candidate in candidates:
        if candidate in localization:
            return localization[candidate]

    return None


def process_mobs(
    source: str,
    mob_id_offset: int = DEFAULT_MOB_ID_OFFSET,
    localization: Dict[str, Any] | None = None,
) -> List[Dict[str, Any]]:
    mobs = []

    with open_xml_source(source) as xml_file:
        for _, elem in ET.iterparse(xml_file, events=("end",)):
            if local_name(elem.tag) != "Mob":
                continue

            mob_id = len(mobs) + 1 + mob_id_offset
            unique_name = elem.attrib.get("uniquename")
            if unique_name is None:
                raise ValueError(f"Mob #{mob_id} is missing the 'uniquename' attribute")

            mob = {
                "mobId": mob_id,
                "uniqueName": unique_name,
            }
            if localization is not None:
                mob["en"] = get_localized_name(
                    localization,
                    unique_name,
                    elem.attrib.get("namelocatag"),
                )

            mobs.append(mob)
            elem.clear()

    return mobs


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate mob IDs and unique names from Albion Online mobs.xml."
    )
    parser.add_argument(
        "source",
        nargs="?",
        default=DEFAULT_SOURCE,
        help=f"mobs.xml URL or local path. Defaults to {DEFAULT_SOURCE}",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Output JSON path. Defaults to {DEFAULT_OUTPUT}",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Write indented JSON instead of compact JSON.",
    )
    parser.add_argument(
        "--mob-id-offset",
        type=int,
        default=DEFAULT_MOB_ID_OFFSET,
        help=f"Value to add to each sequential mob ID. Defaults to {DEFAULT_MOB_ID_OFFSET}.",
    )
    parser.add_argument(
        "--localization",
        default=DEFAULT_LOCALIZATION,
        help=f"localization.json path used for EN values. Defaults to {DEFAULT_LOCALIZATION}.",
    )
    parser.add_argument(
        "--language",
        default=DEFAULT_LANGUAGE,
        help=f"Localization language to export. Defaults to {DEFAULT_LANGUAGE}.",
    )
    args = parser.parse_args()

    localization = load_localization(args.language, args.localization)
    mobs = process_mobs(args.source, args.mob_id_offset, localization)
    with Path(args.output).open("w", encoding="utf-8") as file:
        if args.pretty:
            json.dump(mobs, file, ensure_ascii=False, indent=2)
        else:
            json.dump(mobs, file, ensure_ascii=False, separators=(",", ":"))

    print(f"Wrote {len(mobs)} mobs to {args.output}")


if __name__ == "__main__":
    main()
