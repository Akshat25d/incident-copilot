import json
from pathlib import Path

REPORT = Path("evals/reports/ablation_dev.json")
TARGET = Path("rag/selected_config.json")


def main() -> None:
    selected = json.loads(REPORT.read_text())["selected"]
    TARGET.write_text(json.dumps(selected, indent=2) + "\n")
    print(f"froze: {selected['name']} ({selected['mode']})")
    print(f"config: {selected['config']}")
    print(f"written to {TARGET}")


if __name__ == "__main__":
    main()
