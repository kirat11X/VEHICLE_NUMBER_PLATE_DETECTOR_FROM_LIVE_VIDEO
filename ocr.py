import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from rapidfuzz import fuzz
import filter

try:
    import torch
except ImportError:
    torch = None

try:
    import easyocr
except ImportError:
    easyocr = None

try:
    from paddleocr import PaddleOCR
except ImportError:
    PaddleOCR = None


PROJECT_ROOT = Path("/home/kirat/my_proj_dream")
PLATE_SUMMARY_PATH = PROJECT_ROOT / "final_resolution_outputs" / "plate_resolution_summary.json"
TRACKED_FRAMES_PATH = PROJECT_ROOT / "tracking_outputs" / "tracked_frames.json"
OCR_OUTPUT_DIR = PROJECT_ROOT / "ocr_outputs"
INDIAN_PLATE_REGEX = re.compile(r"^[A-Z]{2}[0-9]{2}[A-Z]{1,3}[0-9]{4}$")
ALLOWLIST = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
TIGHT_MARGIN_RATIO = 0.04
MIN_OCR_PLATE_WIDTH = 80
OCR_MIN_CONFIDENCE = 0.45
TOP_CROPS_PER_TRACK = 5
TARGET_OCR_WIDTH = 240

LETTER_CONFUSIONS = {
    "0": ["O", "D"],
    "1": ["L"],
    "2": ["Z"],
    "5": ["S"],
    "6": ["G"],
    "8": ["B"],
}

DIGIT_CONFUSIONS = {
    "O": ["0"],
    "D": ["0"],
    "Q": ["0"],
    "I": ["1"],
    "L": ["1"],
    "Z": ["2"],
    "S": ["5"],
    "B": ["8"],
    "G": ["6"],
}

PARTIAL_CONFUSIONS = {
    **LETTER_CONFUSIONS,
    **DIGIT_CONFUSIONS,
}


@dataclass
class OCRVote:
    raw_text: str
    normalized_text: str
    corrected_text: str | None
    confidence: float
    source_stage: str
    grammar_valid: bool
    frame_id: int
    sharpness: float


@dataclass
class CropCandidate:
    track_id: int
    frame_id: int
    timestamp: str | None
    source_image: str
    bbox_xyxy: list[int]
    crop_width: int
    crop_height: int
    sharpness: float
    detector_confidence: float
    crop_path: str | None


def load_plate_summary():
    if not PLATE_SUMMARY_PATH.exists():
        raise FileNotFoundError(
            f"Missing plate summary: {PLATE_SUMMARY_PATH}. Run final_resolution first."
        )
    with PLATE_SUMMARY_PATH.open("r", encoding="utf-8") as summary_file:
        return json.load(summary_file)


def load_tracked_frames():
    if not TRACKED_FRAMES_PATH.exists():
        raise FileNotFoundError(
            f"Missing tracked frame data: {TRACKED_FRAMES_PATH}. Run camera_tracking first."
        )
    with TRACKED_FRAMES_PATH.open("r", encoding="utf-8") as tracked_file:
        return json.load(tracked_file)


def choose_ocr_engine():
    if easyocr is not None:
        return "easyocr"
    if PaddleOCR is not None:
        return "paddleocr"
    return None


def gpu_runtime_info():
    info = {
        "torch_available": torch is not None,
        "cuda_available": False,
        "device_name": None,
    }
    if torch is None:
        return info

    try:
        info["cuda_available"] = torch.cuda.is_available()
        if info["cuda_available"]:
            info["device_name"] = torch.cuda.get_device_name(0)
    except Exception:
        info["cuda_available"] = False
        info["device_name"] = None
    return info


def build_ocr_reader(engine_name):
    runtime = gpu_runtime_info()
    if engine_name == "easyocr":
        return easyocr.Reader(["en"], gpu=runtime["cuda_available"])
    if engine_name == "paddleocr":
        return PaddleOCR(
            use_angle_cls=False,
            lang="en",
            show_log=False,
            use_gpu=runtime["cuda_available"],
        )
    return None


def normalize_text(text: str):
    return re.sub(r"[^A-Z0-9]", "", text.upper())


def valid_indian_plate(text: str):
    return bool(INDIAN_PLATE_REGEX.fullmatch(text))


def laplacian_sharpness(image):
    gray = filter.to_gray(image)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def tighten_plate_bbox(bbox_xyxy, image_shape, margin_ratio=TIGHT_MARGIN_RATIO):
    x1, y1, x2, y2 = bbox_xyxy
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)
    pad_x = int(width * margin_ratio)
    pad_y = int(height * margin_ratio)

    tightened = [
        max(0, x1 - pad_x),
        max(0, y1 - pad_y),
        min(image_shape[1], x2 + pad_x),
        min(image_shape[0], y2 + pad_y),
    ]
    return tightened


def crop_plate_from_frame(image_path: Path, bbox_xyxy, already_tight: bool = False):
    image = cv2.imread(str(image_path))
    if image is None:
        return None, None

    tightened_bbox = (
        bbox_xyxy if already_tight else tighten_plate_bbox(bbox_xyxy, image.shape)
    )
    x1, y1, x2, y2 = tightened_bbox
    crop = image[y1:y2, x1:x2]
    if crop.size == 0:
        return None, None
    return crop, tightened_bbox


def deskew_plate_crop(image):
    gray = filter.to_gray(image)
    edges = cv2.Canny(gray, 50, 150)
    coords = cv2.findNonZero(edges)
    if coords is None or len(coords) < 20:
        return image

    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = 90 + angle
    if abs(angle) < 1.0:
        return image

    center = (image.shape[1] // 2, image.shape[0] // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(
        image,
        matrix,
        (image.shape[1], image.shape[0]),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE,
    )


def enhance_for_ocr(image):
    current_width = max(image.shape[1], 1)
    scale = max(1.0, min(TARGET_OCR_WIDTH / current_width, 4.0))
    resized = cv2.resize(
        image,
        None,
        fx=scale,
        fy=scale,
        interpolation=cv2.INTER_CUBIC,
    )
    deskewed = deskew_plate_crop(resized)
    clahe = filter.clahe_enhance(deskewed, clip_limit=2.0, tile_grid_size=(8, 8))
    final = filter.unsharp_mask(clahe, sigma=1.0, strength=0.8)
    return {
        "tight_original": image,
        "deskewed_final": final,
    }


def save_debug_crop(track_id: int, frame_id: int, stage_name: str, image):
    debug_dir = OCR_OUTPUT_DIR / "debug_crops" / f"track_{track_id:04d}" / stage_name
    debug_dir.mkdir(parents=True, exist_ok=True)
    output_path = debug_dir / f"frame_{frame_id:06d}.jpg"
    cv2.imwrite(str(output_path), image)
    return str(output_path)


def build_track_candidates(track_id: int, tracked_frames: list[dict]):
    candidates = []
    for record in tracked_frames:
        if record["track_id"] != track_id or not record.get("plate_bbox_xyxy"):
            continue

        source_image = Path(record["source_image"])
        crop, tightened_bbox = crop_plate_from_frame(source_image, record["plate_bbox_xyxy"])
        if crop is None:
            continue

        height, width = crop.shape[:2]
        if width < MIN_OCR_PLATE_WIDTH:
            continue

        candidates.append(
            CropCandidate(
                track_id=track_id,
                frame_id=record["frame_id"],
                timestamp=record.get("timestamp"),
                source_image=record["source_image"],
                bbox_xyxy=tightened_bbox,
                crop_width=width,
                crop_height=height,
                sharpness=laplacian_sharpness(crop),
                detector_confidence=float(record.get("confidence", 0.0)),
                crop_path=None,
            )
        )

    candidates.sort(
        key=lambda candidate: (
            candidate.sharpness,
            candidate.crop_width,
            candidate.detector_confidence,
        ),
        reverse=True,
    )
    return candidates[:TOP_CROPS_PER_TRACK]


def generate_position_patterns(length: int):
    patterns = []
    for middle_letters in range(1, 4):
        expected_length = 2 + 2 + middle_letters + 4
        if length == expected_length:
            patterns.append(
                ["L", "L", "D", "D"] + (["L"] * middle_letters) + (["D"] * 4)
            )
    return patterns


def expand_char_for_slot(char: str, slot_type: str):
    options = {char}
    if slot_type == "L":
        options.update(LETTER_CONFUSIONS.get(char, []))
        return {option for option in options if option.isalpha()}
    options.update(DIGIT_CONFUSIONS.get(char, []))
    return {option for option in options if option.isdigit()}


def generate_variants(text: str, max_variants: int = 64):
    normalized = normalize_text(text)
    patterns = generate_position_patterns(len(normalized))
    if not patterns:
        return []

    all_variants = set()
    for pattern in patterns:
        candidates = [""]
        for char, slot_type in zip(normalized, pattern):
            expanded = expand_char_for_slot(char, slot_type) or {char}
            next_candidates = []
            for prefix in candidates:
                for option in sorted(expanded):
                    next_candidates.append(prefix + option)
            candidates = next_candidates[:max_variants]
        all_variants.update(candidate for candidate in candidates if valid_indian_plate(candidate))

    return sorted(all_variants)


def generate_fragment_variants(text: str, max_variants: int = 32):
    normalized = normalize_text(text)
    if not normalized:
        return []

    candidates = [""]
    for char in normalized:
        expanded = {char}
        expanded.update(PARTIAL_CONFUSIONS.get(char, []))
        next_candidates = []
        for prefix in candidates:
            for option in sorted(expanded):
                next_candidates.append(prefix + option)
        candidates = next_candidates[:max_variants]

    return sorted(set(candidate for candidate in candidates if candidate))


def score_variant(raw_text: str, variant: str, confidence: float):
    similarity = fuzz.ratio(normalize_text(raw_text), variant) / 100.0
    return (confidence * 0.65) + (similarity * 0.35)


def correct_plate_text(text: str, confidence: float):
    normalized = normalize_text(text)
    if valid_indian_plate(normalized):
        return normalized, [normalized]

    variants = generate_variants(normalized)
    if not variants:
        fragment_variants = generate_fragment_variants(normalized)
        if not fragment_variants:
            return normalized if normalized else None, []
        best_fragment = max(
            fragment_variants,
            key=lambda variant: score_variant(normalized, variant, confidence),
        )
        return best_fragment, fragment_variants

    best_variant = max(variants, key=lambda variant: score_variant(normalized, variant, confidence))
    return best_variant, variants


def read_with_easyocr(reader, image_path: Path):
    results = reader.readtext(str(image_path), detail=1, paragraph=False, allowlist=ALLOWLIST)
    votes = []
    for _, text, confidence in results:
        votes.append((text, float(confidence)))
    return votes


def read_with_paddleocr(reader, image_path: Path):
    predictions = reader.ocr(str(image_path), cls=False)
    votes = []
    for line_group in predictions or []:
        for line in line_group or []:
            text, confidence = line[1]
            votes.append((text, float(confidence)))
    return votes


def extract_votes(reader, engine_name, image_path: Path):
    if engine_name == "easyocr":
        return read_with_easyocr(reader, image_path)
    if engine_name == "paddleocr":
        return read_with_paddleocr(reader, image_path)
    return []


def vote_best_full_plate(ocr_votes: list[OCRVote]):
    full_votes = [vote for vote in ocr_votes if vote.corrected_text and valid_indian_plate(vote.corrected_text)]
    if not full_votes:
        return None, []

    weighted = defaultdict(float)
    for vote in full_votes:
        weighted[vote.corrected_text] += vote.confidence
    best_text = max(weighted, key=weighted.get)
    return best_text, sorted(weighted, key=weighted.get, reverse=True)


def vote_best_fragment(ocr_votes: list[OCRVote]):
    fragment_groups = defaultdict(list)
    for vote in ocr_votes:
        candidate = vote.corrected_text or vote.normalized_text
        if candidate:
            fragment_groups[len(candidate)].append((candidate, vote.confidence))

    if not fragment_groups:
        return None

    best_length = max(
        fragment_groups,
        key=lambda length: sum(weight for _, weight in fragment_groups[length]),
    )
    position_scores = [defaultdict(float) for _ in range(best_length)]
    for fragment, confidence in fragment_groups[best_length]:
        for index, char in enumerate(fragment[:best_length]):
            position_scores[index][char] += confidence

    return "".join(
        max(position_score, key=position_score.get) if position_score else ""
        for position_score in position_scores
    )


def process_track_ocr(track_summary: dict, tracked_frames: list[dict], reader, engine_name):
    track_id = track_summary["track_id"]
    candidates = build_track_candidates(track_id, tracked_frames)
    if not candidates:
        return {
            "track_id": track_id,
            "status": "skipped",
            "reason": "No sufficiently large tight plate crops were found for this track.",
            "selected_crops": [],
        }

    ocr_votes = []
    all_variants = set()
    selected_crops = []

    for candidate in candidates:
        source_image = Path(candidate.source_image)
        crop, _ = crop_plate_from_frame(
            source_image, candidate.bbox_xyxy, already_tight=True
        )
        if crop is None:
            continue

        stage_images = enhance_for_ocr(crop)
        stage_paths = {}
        for stage_name, image in stage_images.items():
            stage_paths[stage_name] = save_debug_crop(
                track_id, candidate.frame_id, stage_name, image
            )

            for raw_text, confidence in extract_votes(
                reader, engine_name, Path(stage_paths[stage_name])
            ):
                if confidence < OCR_MIN_CONFIDENCE:
                    continue

                normalized = normalize_text(raw_text)
                corrected, variants = correct_plate_text(raw_text, confidence)
                all_variants.update(variants)
                grammar_valid = corrected is not None and valid_indian_plate(corrected)
                ocr_votes.append(
                    OCRVote(
                        raw_text=raw_text,
                        normalized_text=normalized,
                        corrected_text=corrected,
                        confidence=confidence,
                        source_stage=stage_name,
                        grammar_valid=grammar_valid,
                        frame_id=candidate.frame_id,
                        sharpness=candidate.sharpness,
                    )
                )

        selected_crops.append(
            {
                "frame_id": candidate.frame_id,
                "timestamp": candidate.timestamp,
                "source_image": candidate.source_image,
                "tight_plate_bbox_xyxy": candidate.bbox_xyxy,
                "crop_width": candidate.crop_width,
                "crop_height": candidate.crop_height,
                "sharpness": candidate.sharpness,
                "detector_confidence": candidate.detector_confidence,
                "debug_stage_paths": stage_paths,
            }
        )

    if not ocr_votes:
        return {
            "track_id": track_id,
            "status": "no_text_detected",
            "plate_text_candidate": None,
            "confidence": 0.0,
            "ocr_votes": [],
            "variants": [],
            "selected_crops": selected_crops,
        }

    best_full_plate, ranked_full_variants = vote_best_full_plate(ocr_votes)
    fragment_candidate = vote_best_fragment(ocr_votes)
    final_candidate = best_full_plate or fragment_candidate
    agreeing_votes = []
    for vote in ocr_votes:
        candidate_text = vote.corrected_text or vote.normalized_text
        if candidate_text == final_candidate:
            agreeing_votes.append(vote.confidence)
    final_confidence = (
        sum(agreeing_votes) / len(agreeing_votes)
        if agreeing_votes
        else 0.0
    )

    return {
        "track_id": track_id,
        "status": "processed",
        "plate_text_candidate": final_candidate,
        "confidence": final_confidence,
        "strict_regex_match": valid_indian_plate(final_candidate) if final_candidate else False,
        "ocr_votes": [
            {
                "raw_text": vote.raw_text,
                "normalized_text": vote.normalized_text,
                "corrected_text": vote.corrected_text,
                "confidence": vote.confidence,
                "source_stage": vote.source_stage,
                "grammar_valid": vote.grammar_valid,
                "frame_id": vote.frame_id,
                "sharpness": vote.sharpness,
            }
            for vote in ocr_votes
        ],
        "variants": sorted(all_variants),
        "ranked_full_variants": ranked_full_variants,
        "fragment_candidate": fragment_candidate,
        "selected_crops": selected_crops,
    }


def main():
    OCR_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    plate_summary = load_plate_summary()
    tracked_frames = load_tracked_frames()
    engine_name = choose_ocr_engine()
    runtime = gpu_runtime_info()

    if engine_name is None:
        output = {
            "status": "no_ocr_engine",
            "message": "Install EasyOCR or PaddleOCR to run OCR.",
            "gpu_runtime": runtime,
            "results": [],
        }
    else:
        reader = build_ocr_reader(engine_name)
        results = [
            process_track_ocr(track_summary, tracked_frames, reader, engine_name)
            for track_summary in plate_summary
        ]
        output = {
            "status": "processed",
            "ocr_engine": engine_name,
            "gpu_runtime": runtime,
            "indian_plate_regex": INDIAN_PLATE_REGEX.pattern,
            "ocr_min_confidence": OCR_MIN_CONFIDENCE,
            "tight_margin_ratio": TIGHT_MARGIN_RATIO,
            "min_ocr_plate_width": MIN_OCR_PLATE_WIDTH,
            "results": results,
        }

    output_path = OCR_OUTPUT_DIR / "ocr_results.json"
    with output_path.open("w", encoding="utf-8") as output_file:
        json.dump(output, output_file, indent=2)

    print(f"OCR results saved to: {output_path}")
    print(f"OCR engine: {engine_name or 'not available'}")
    print(
        "CUDA for OCR: "
        f"{'enabled' if runtime['cuda_available'] else 'not available'}"
        + (f" ({runtime['device_name']})" if runtime["device_name"] else "")
    )


if __name__ == "__main__":
    main()
