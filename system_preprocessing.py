import json
from dataclasses import asdict, dataclass
from pathlib import Path

import cv2
import numpy as np

import filter


IMAGE_PATH = Path("frames/frame_000001.jpg")
OUTPUT_ROOT = Path("preprocessing_outputs")
MODE = "full_frame"
ROI = None
SAVE_ALL_CANDIDATES = True
FRAME_STABILIZATION_ENABLED = False
PLATE_CROP_SUPER_RESOLUTION_ENABLED = False

LOW_BRIGHTNESS_THRESHOLD = 90.0
LOW_CONTRAST_THRESHOLD = 45.0
LOW_SHARPNESS_THRESHOLD = 120.0
HIGH_NOISE_THRESHOLD = 18.0


@dataclass
class QualityMetrics:
    brightness: float
    contrast: float
    sharpness: float
    noise: float
    edge_strength: float
    is_dark: bool
    is_low_contrast: bool
    is_blurry: bool
    is_noisy: bool


def load_image(image_path):
    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")
    return image


def extract_roi(image, roi):
    if roi is None:
        return image, None

    x, y, w, h = roi
    cropped = image[y : y + h, x : x + w]
    if cropped.size == 0:
        raise ValueError("ROI is outside the image bounds or empty.")
    return cropped, {"x": x, "y": y, "w": w, "h": h}


def merge_roi_back(full_image, roi_image, roi):
    if roi is None:
        return roi_image

    x, y, w, h = roi
    merged = full_image.copy()
    merged[y : y + h, x : x + w] = roi_image
    return merged


def compute_noise_score(gray_image):
    denoised = cv2.GaussianBlur(gray_image, (3, 3), 0)
    noise_residual = cv2.absdiff(gray_image, denoised)
    return float(np.std(noise_residual))


def compute_edge_strength(gray_image):
    edges = cv2.Canny(gray_image, 100, 200)
    return float(np.mean(edges))


def analyze_image(image):
    gray = filter.to_gray(image)
    brightness = float(np.mean(gray))
    contrast = float(np.std(gray))
    sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    noise = compute_noise_score(gray)
    edge_strength = compute_edge_strength(gray)

    return QualityMetrics(
        brightness=brightness,
        contrast=contrast,
        sharpness=sharpness,
        noise=noise,
        edge_strength=edge_strength,
        is_dark=brightness < LOW_BRIGHTNESS_THRESHOLD,
        is_low_contrast=contrast < LOW_CONTRAST_THRESHOLD,
        is_blurry=sharpness < LOW_SHARPNESS_THRESHOLD,
        is_noisy=noise > HIGH_NOISE_THRESHOLD,
    )


def candidate_filters(metrics, mode):
    candidates = [("original", lambda image: image.copy())]

    if metrics.is_low_contrast or metrics.is_dark:
        candidates.append(("clahe", filter.clahe_enhance))

    if metrics.is_dark:
        candidates.append(("gamma", lambda image: filter.gamma_correction(image, 1.4)))

    if metrics.is_noisy:
        if mode == "plate_crop":
            candidates.append(("nl_means", filter.nl_means_filter))
        candidates.append(("bilateral", filter.bilateral_filter))

    if metrics.is_blurry:
        candidates.append(("unsharp", filter.unsharp_mask))
        if mode == "plate_crop":
            candidates.append(("wiener", filter.apply_wiener_deconvolution))

    if not metrics.is_noisy and not metrics.is_blurry:
        candidates.append(("light_clahe", lambda image: filter.clahe_enhance(image, 1.8)))

    unique_candidates = []
    seen_names = set()
    for name, func in candidates:
        if name not in seen_names:
            unique_candidates.append((name, func))
            seen_names.add(name)
    return unique_candidates


def score_candidate(image, base_metrics):
    metrics = analyze_image(image)
    score = (
        metrics.sharpness * 0.45
        + metrics.edge_strength * 0.30
        + metrics.contrast * 0.20
        - metrics.noise * 0.15
    )

    if base_metrics.is_dark and metrics.brightness > base_metrics.brightness:
        score += 10.0
    if base_metrics.is_low_contrast and metrics.contrast > base_metrics.contrast:
        score += 10.0
    if base_metrics.is_blurry and metrics.sharpness > base_metrics.sharpness:
        score += 15.0

    return metrics, float(score)


def save_report(report_path, payload):
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8") as report_file:
        json.dump(payload, report_file, indent=2)


def pipeline_status():
    return {
        "adaptive_preprocessing": "implemented",
        "frame_stabilization": "pending"
        if not FRAME_STABILIZATION_ENABLED
        else "enabled",
        "plate_crop_super_resolution": "pending"
        if not PLATE_CROP_SUPER_RESOLUTION_ENABLED
        else "enabled",
        "note": "Super-resolution should be applied only on plate crops, not full frames.",
    }


def process_image(image_path, output_root, mode="full_frame", roi=None):
    image = load_image(image_path)
    working_region, roi_info = extract_roi(image, roi)
    base_metrics = analyze_image(working_region)

    filters_to_try = candidate_filters(base_metrics, mode)
    candidate_reports = []
    best_result = None
    best_score = float("-inf")
    best_name = None

    for filter_name, filter_func in filters_to_try:
        filtered_region = filter_func(working_region)
        if filtered_region is None:
            continue

        full_output = merge_roi_back(image, filtered_region, roi)
        metrics, score = score_candidate(filtered_region, base_metrics)

        candidate_entry = {
            "filter_name": filter_name,
            "score": score,
            "metrics": asdict(metrics),
        }
        candidate_reports.append(candidate_entry)

        if SAVE_ALL_CANDIDATES:
            candidate_path = output_root / filter_name / image_path.name
            filter.save_image(candidate_path, full_output)

        if score > best_score:
            best_score = score
            best_result = full_output
            best_name = filter_name

    if best_result is None:
        raise RuntimeError("No valid preprocessing candidates were generated.")

    best_output_path = output_root / "best" / image_path.name
    filter.save_image(best_output_path, best_result)

    report = {
        "input_image": str(image_path),
        "mode": mode,
        "roi": roi_info,
        "pipeline_status": pipeline_status(),
        "decision_summary": {
            "selected_filter": best_name,
            "candidate_count": len(candidate_reports),
            "blind_deconvolution": filter.blind_deconvolution_note(),
        },
        "base_metrics": asdict(base_metrics),
        "candidates": candidate_reports,
        "best_output_path": str(best_output_path),
    }
    save_report(output_root / "report.json", report)
    return report

def main():
    frames_dir = Path("frames")
    image_paths = sorted(frames_dir.glob("*.jpg"))

    for image_path in image_paths:
        output_root = OUTPUT_ROOT / MODE / image_path.stem
        report = process_image(image_path, output_root, mode=MODE, roi=ROI)
        print(f"{image_path.name} -> {report['decision_summary']['selected_filter']}")


if __name__ == "__main__":
    main()
