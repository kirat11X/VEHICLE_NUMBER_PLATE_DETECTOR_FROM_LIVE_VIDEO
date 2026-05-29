import argparse
import runpy
import time
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path("/home/kirat/my_proj_dream")


@dataclass
class PipelineStep:
    key: str
    title: str
    description: str
    script_path: Path
    enabled: bool = True


# This pipeline intentionally wraps your existing stage files instead of rewriting
# them into one giant script. That keeps each module isolated and easier to extend.
PIPELINE_STEPS = [
    PipelineStep(
        key="frame_extraction",
        title="Frame Extraction",
        description="Reads the source video and extracts timestamped frames into frames/.",
        script_path=PROJECT_ROOT / "video_image.py",
    ),
    PipelineStep(
        key="preprocessing",
        title="Adaptive Frame Preprocessing",
        description="Scores each frame and saves the best preprocessing result per frame.",
        script_path=PROJECT_ROOT / "system_preprocessing.py",
    ),
    PipelineStep(
        key="combine_preprocessing",
        title="Combine Preprocessed Outputs",
        description="Groups per-frame preprocessing outputs into filter-wise folders such as best/ and clahe/.",
        script_path=PROJECT_ROOT / "combine_folders.py",
    ),
    PipelineStep(
        key="detection",
        title="Vehicle And Plate Detection",
        description="Runs the two-stage detector: vehicles first, plates inside vehicles second.",
        script_path=PROJECT_ROOT / "yolo" / "model.py",
    ),
    PipelineStep(
        key="tracking",
        title="Vehicle Tracking",
        description="Assigns persistent vehicle identities across frames and links plate crops to tracks.",
        script_path=PROJECT_ROOT / "camera_tracking.py",
    ),
    PipelineStep(
        key="plate_enhancement",
        title="Plate Crop Enhancement",
        description="Selects the best tracked plate crop and applies resize, CLAHE, and mild sharpening.",
        script_path=PROJECT_ROOT / "final_resolution",
    ),
    PipelineStep(
        key="ocr",
        title="OCR And Grammar Correction",
        description="Runs OCR on tight plate crops and applies Indian plate grammar correction and voting.",
        script_path=PROJECT_ROOT / "ocr.py",
    ),
]


def list_steps():
    for index, step in enumerate(PIPELINE_STEPS, start=1):
        status = "enabled" if step.enabled else "disabled"
        print(f"{index}. {step.key} [{status}]")
        print(f"   {step.title}")
        print(f"   {step.description}")
        print(f"   script: {step.script_path}")


def resolve_steps(only=None, start_at=None, stop_after=None):
    selected = [step for step in PIPELINE_STEPS if step.enabled]

    if only:
        lookup = {step.key: step for step in PIPELINE_STEPS}
        missing = [key for key in only if key not in lookup]
        if missing:
            raise ValueError(f"Unknown pipeline step(s): {', '.join(missing)}")
        return [lookup[key] for key in only if lookup[key].enabled]

    if start_at:
        start_index = next(
            (index for index, step in enumerate(selected) if step.key == start_at),
            None,
        )
        if start_index is None:
            raise ValueError(f"Unknown start step: {start_at}")
        selected = selected[start_index:]

    if stop_after:
        stop_index = next(
            (index for index, step in enumerate(selected) if step.key == stop_after),
            None,
        )
        if stop_index is None:
            raise ValueError(f"Unknown stop step: {stop_after}")
        selected = selected[: stop_index + 1]

    return selected


def execute_step(step: PipelineStep):
    if not step.script_path.exists():
        raise FileNotFoundError(f"Step script not found: {step.script_path}")

    print(f"\n=== {step.title} ===")
    print(step.description)
    started_at = time.time()

    # run_path lets us execute each existing script as its own stage entrypoint.
    # This keeps the pipeline expandable: future steps can just add a new file and a new PipelineStep.
    runpy.run_path(str(step.script_path), run_name="__main__")

    elapsed = time.time() - started_at
    print(f"Completed {step.key} in {elapsed:.2f}s")


def main():
    parser = argparse.ArgumentParser(
        description="Run the ANPR project pipeline step by step using the existing stage files."
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all pipeline steps and exit.",
    )
    parser.add_argument(
        "--only",
        nargs="+",
        help="Run only the specified step keys, in the order given.",
    )
    parser.add_argument(
        "--start-at",
        help="Start running from this step key.",
    )
    parser.add_argument(
        "--stop-after",
        help="Stop after this step key.",
    )
    args = parser.parse_args()

    if args.list:
        list_steps()
        return

    steps_to_run = resolve_steps(
        only=args.only,
        start_at=args.start_at,
        stop_after=args.stop_after,
    )

    if not steps_to_run:
        print("No enabled steps selected.")
        return

    print("ANPR Pipeline")
    print(f"Project root: {PROJECT_ROOT}")
    print("Steps to run:")
    for step in steps_to_run:
        print(f"- {step.key}: {step.title}")

    for step in steps_to_run:
        execute_step(step)

    print("\nPipeline finished.")


if __name__ == "__main__":
    main()
