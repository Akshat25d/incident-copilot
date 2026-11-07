import pathlib
import sys

MARKER_START = "=== FILE: "
MARKER_END = " ==="


def split(text: str) -> int:
    files: dict[str, list[str]] = {}
    current = None
    for line in text.splitlines():
        if line.startswith(MARKER_START) and line.endswith(MARKER_END):
            current = line[len(MARKER_START) : -len(MARKER_END)].strip()
            files[current] = []
        elif current is not None:
            files[current].append(line)
    for name, lines in files.items():
        path = pathlib.Path(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines).strip() + "\n")
    return len(files)


if __name__ == "__main__":
    print(f"wrote {split(pathlib.Path(sys.argv[1]).read_text())} files")
