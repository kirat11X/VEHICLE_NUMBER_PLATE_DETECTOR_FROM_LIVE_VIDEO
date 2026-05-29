import shutil
from pathlib import Path

from system_preprocessing import MODE, OUTPUT_ROOT


FILTER_GROUPS = ["best", "clahe", "gamma", "original", "unsharp"]
COMBINED_DIRNAME = "combined"


def combine_filter_outputs(output_root=OUTPUT_ROOT, mode=MODE, filter_groups=None):
    filter_groups = filter_groups or FILTER_GROUPS
    mode_root = Path(output_root) / mode
    combined_root = Path(output_root) / COMBINED_DIRNAME / mode

    if not mode_root.exists():
        raise FileNotFoundError(f"Could not find preprocessing output folder: {mode_root}")

    copied_counts = {filter_name: 0 for filter_name in filter_groups}

    for frame_dir in sorted(path for path in mode_root.iterdir() if path.is_dir()):
        for filter_name in filter_groups:
            source_dir = frame_dir / filter_name
            if not source_dir.exists():
                continue

            destination_dir = combined_root / filter_name
            destination_dir.mkdir(parents=True, exist_ok=True)

            for image_path in sorted(source_dir.glob("*")):
                if not image_path.is_file():
                    continue
                destination_path = destination_dir / image_path.name
                shutil.copy2(image_path, destination_path)
                copied_counts[filter_name] += 1

    return combined_root, copied_counts


def main():
    combined_root, copied_counts = combine_filter_outputs()
    print(f"Combined outputs saved under: {combined_root}")
    for filter_name, copied_count in copied_counts.items():
        print(f"{filter_name}: {copied_count} files")


if __name__ == "__main__":
    main()
