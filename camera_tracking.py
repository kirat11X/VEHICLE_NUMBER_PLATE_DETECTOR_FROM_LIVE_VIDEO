import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

import cv2

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None

try:
    from deep_sort_realtime.deepsort_tracker import DeepSort
except ImportError:
    DeepSort = None

from yolo import model as detection_model


TRACKER_BACKEND = "bytetrack"
OUTPUT_DIR = Path("/home/kirat/my_proj_dream/tracking_outputs")
BYTE_TRACKER_CONFIG = None
DEEPSORT_MAX_AGE = 30
DEEPSORT_N_INIT = 2
SAVE_ANNOTATED_FRAMES = True
SAVE_TRACK_SUMMARY = True


@dataclass
class TrackState:
    track_id: int
    class_name: str
    last_bbox_xyxy: list[int]
    last_frame_id: int
    timestamps: list[str] = field(default_factory=list)
    confidences: list[float] = field(default_factory=list)
    vehicle_bboxes: list[list[int]] = field(default_factory=list)
    plate_bboxes: list[list[int]] = field(default_factory=list)
    plate_crop_paths: list[str] = field(default_factory=list)
    source_images: list[str] = field(default_factory=list)
    best_plate_crop: Optional[str] = None
    best_plate_confidence: float = -1.0


def ensure_ultralytics():
    if YOLO is None:
        raise ImportError(
            "ultralytics is not installed. Install it first to run tracking."
        )


def ensure_deepsort():
    if DeepSort is None:
        raise ImportError(
            "deep-sort-realtime is not installed. Install it first to use DeepSORT."
        )


def load_tracking_context():
    input_dir = detection_model.choose_input_dir()
    image_paths = detection_model.get_input_images(input_dir)
    if not image_paths:
        raise FileNotFoundError(f"No JPG frames found in: {input_dir}")

    frame_metadata = detection_model.load_frame_metadata(
        detection_model.FRAME_METADATA_PATH
    )
    return input_dir, image_paths, frame_metadata


def resolve_bytetrack_config():
    if YOLO is None:
        return "bytetrack.yaml"

    ultralytics_root = Path(YOLO.__module__.split(".")[0])
    try:
        import ultralytics

        ultralytics_root = Path(ultralytics.__file__).resolve().parent
    except Exception:
        pass

    config_path = ultralytics_root / "cfg" / "trackers" / "bytetrack.yaml"
    if config_path.exists():
        return str(config_path)
    return "bytetrack.yaml"


def normalize_timestamp(image_path: Path, frame_metadata: dict):
    metadata = frame_metadata.get(image_path.name, {})
    timestamp = metadata.get("timestamp_utc") or metadata.get("video_timestamp_ms")
    frame_id = metadata.get("frame_id", detection_model.parse_frame_id(image_path))
    return frame_id, str(timestamp) if timestamp is not None else None


def draw_track_annotations(image, vehicle_bbox, track_id, class_name, plate_bbox=None):
    x1, y1, x2, y2 = vehicle_bbox
    cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 0), 2)
    cv2.putText(
        image,
        f"{class_name} #{track_id}",
        (x1, max(20, y1 - 8)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 0, 0),
        2,
        cv2.LINE_AA,
    )

    if plate_bbox is not None:
        px1, py1, px2, py2 = plate_bbox
        cv2.rectangle(image, (px1, py1), (px2, py2), (0, 165, 255), 2)


def update_track_state(
    tracks_by_id: dict[int, TrackState],
    track_id: int,
    class_name: str,
    vehicle_bbox: list[int],
    frame_id: int,
    timestamp: Optional[str],
    source_image: str,
    confidence: float,
    plate_record: Optional[dict],
):
    track_state = tracks_by_id.get(track_id)
    if track_state is None:
        track_state = TrackState(
            track_id=track_id,
            class_name=class_name,
            last_bbox_xyxy=vehicle_bbox,
            last_frame_id=frame_id,
        )
        tracks_by_id[track_id] = track_state

    track_state.class_name = class_name
    track_state.last_bbox_xyxy = vehicle_bbox
    track_state.last_frame_id = frame_id
    track_state.timestamps.append(timestamp)
    track_state.confidences.append(confidence)
    track_state.vehicle_bboxes.append(vehicle_bbox)
    track_state.source_images.append(source_image)

    if plate_record is not None:
        track_state.plate_bboxes.append(plate_record["bbox_xyxy"])
        if plate_record.get("crop_path"):
            track_state.plate_crop_paths.append(plate_record["crop_path"])
        if plate_record["confidence"] > track_state.best_plate_confidence:
            track_state.best_plate_confidence = plate_record["confidence"]
            track_state.best_plate_crop = plate_record.get("crop_path")

    return track_state


def select_best_plate(plate_model, frame_image, vehicle_bbox, frame_output_dir, track_id):
    vehicle_crop = detection_model.crop_region(frame_image, vehicle_bbox)
    if vehicle_crop.size == 0:
        return None

    boxes = detection_model.run_inference(
        plate_model, vehicle_crop, detection_model.PLATE_CONFIDENCE
    )
    detections = detection_model.extract_boxes(boxes, plate_model.names)
    if not detections:
        return None

    best_plate = max(detections, key=lambda detection: detection["confidence"])
    px1, py1, px2, py2 = best_plate["bbox_xyxy"]
    absolute_bbox = [
        vehicle_bbox[0] + px1,
        vehicle_bbox[1] + py1,
        vehicle_bbox[0] + px2,
        vehicle_bbox[1] + py2,
    ]
    plate_crop = detection_model.crop_region(frame_image, absolute_bbox)
    crop_path = None
    if plate_crop.size != 0:
        crop_path = frame_output_dir / "plate_crops" / f"track_{track_id:04d}.jpg"
        crop_path.parent.mkdir(parents=True, exist_ok=True)
        detection_model.save_crop(crop_path, plate_crop)

    return {
        "bbox_xyxy": absolute_bbox,
        "confidence": best_plate["confidence"],
        "crop_path": str(crop_path) if crop_path else None,
    }


def save_annotated_frame(output_dir: Path, image_path: Path, annotated_image):
    output_path = output_dir / "annotated_frames" / image_path.name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), annotated_image)


def finalize_outputs(output_dir: Path, tracks_by_id: dict[int, TrackState], tracked_frames):
    output_dir.mkdir(parents=True, exist_ok=True)

    with (output_dir / "tracked_frames.json").open("w", encoding="utf-8") as tracked_file:
        json.dump(tracked_frames, tracked_file, indent=2)

    if SAVE_TRACK_SUMMARY:
        with (output_dir / "track_summary.json").open("w", encoding="utf-8") as summary_file:
            json.dump(
                [asdict(track) for track in tracks_by_id.values()],
                summary_file,
                indent=2,
            )


def load_detection_records():
    detections_path = detection_model.OUTPUT_DIR / "detections.json"
    if not detections_path.exists():
        raise FileNotFoundError(
            f"Detection report not found: {detections_path}. Run yolo/model.py first."
        )
    with detections_path.open("r", encoding="utf-8") as detections_file:
        return json.load(detections_file)


def intersection_over_union(box_a, box_b):
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)

    inter_w = max(0, inter_x2 - inter_x1)
    inter_h = max(0, inter_y2 - inter_y1)
    inter_area = inter_w * inter_h

    area_a = max(0, ax2 - ax1) * max(0, ay2 - ay1)
    area_b = max(0, bx2 - bx1) * max(0, by2 - by1)
    union_area = area_a + area_b - inter_area
    if union_area <= 0:
        return 0.0
    return inter_area / union_area


def group_records_by_frame(detection_records):
    frames = {}
    for record in detection_records:
        frames.setdefault(record["frame_id"], []).append(record)
    return dict(sorted(frames.items()))


def split_vehicle_and_plate_records(frame_records):
    vehicle_records = []
    plate_records_by_vehicle = {}
    for record in frame_records:
        if record["detection_stage"] == "vehicle":
            vehicle_records.append(record)
        elif record["detection_stage"] == "plate":
            parent_key = record.get("parent_vehicle_id")
            vehicle_key = record.get("vehicle_id")
            if parent_key:
                plate_records_by_vehicle.setdefault(parent_key, []).append(record)
            if vehicle_key and vehicle_key != parent_key:
                plate_records_by_vehicle.setdefault(vehicle_key, []).append(record)
    return vehicle_records, plate_records_by_vehicle


def choose_best_iou_track(active_tracks, detection_bbox):
    best_track = None
    best_iou = 0.0
    for track in active_tracks.values():
        iou = intersection_over_union(track.last_bbox_xyxy, detection_bbox)
        if iou > best_iou:
            best_iou = iou
            best_track = track
    if best_iou < 0.30:
        return None
    return best_track


def run_simple_tracking():
    detection_records = load_detection_records()
    records_by_frame = group_records_by_frame(detection_records)

    tracks_by_id = {}
    tracked_frames = []
    active_tracks = {}
    next_track_id = 1

    for frame_id, frame_records in records_by_frame.items():
        vehicle_records, plate_records_by_vehicle = split_vehicle_and_plate_records(
            frame_records
        )
        matched_track_ids = set()
        annotated = None
        image_path = None

        for vehicle_record in vehicle_records:
            image_path = Path(vehicle_record["source_image"])
            if annotated is None and image_path.exists():
                frame_image = cv2.imread(str(image_path))
                annotated = frame_image.copy() if frame_image is not None else None

            matched_track = choose_best_iou_track(
                {
                    track_id: track
                    for track_id, track in active_tracks.items()
                    if track_id not in matched_track_ids
                },
                vehicle_record["bbox_xyxy"],
            )
            if matched_track is None:
                matched_track = TrackState(
                    track_id=next_track_id,
                    class_name=vehicle_record["class_name"],
                    last_bbox_xyxy=vehicle_record["bbox_xyxy"],
                    last_frame_id=frame_id,
                )
                active_tracks[next_track_id] = matched_track
                next_track_id += 1

            matched_track_ids.add(matched_track.track_id)
            associated_plates = plate_records_by_vehicle.get(
                vehicle_record.get("vehicle_id"), []
            )
            best_plate = (
                max(associated_plates, key=lambda record: record["confidence"])
                if associated_plates
                else None
            )

            update_track_state(
                tracks_by_id=tracks_by_id,
                track_id=matched_track.track_id,
                class_name=vehicle_record["class_name"],
                vehicle_bbox=vehicle_record["bbox_xyxy"],
                frame_id=frame_id,
                timestamp=vehicle_record["timestamp"],
                source_image=vehicle_record["source_image"],
                confidence=vehicle_record["confidence"],
                plate_record=best_plate,
            )

            tracked_frames.append(
                {
                    "frame_id": frame_id,
                    "timestamp": vehicle_record["timestamp"],
                    "source_image": vehicle_record["source_image"],
                    "track_id": matched_track.track_id,
                    "class_name": vehicle_record["class_name"],
                    "confidence": vehicle_record["confidence"],
                    "bbox_xyxy": vehicle_record["bbox_xyxy"],
                    "plate_bbox_xyxy": best_plate["bbox_xyxy"] if best_plate else None,
                    "tracker_backend": "simple_iou",
                }
            )

            if annotated is not None:
                draw_track_annotations(
                    annotated,
                    vehicle_record["bbox_xyxy"],
                    matched_track.track_id,
                    vehicle_record["class_name"],
                    best_plate["bbox_xyxy"] if best_plate else None,
                )

        stale_track_ids = []
        for track_id, track in active_tracks.items():
            if track_id in matched_track_ids:
                continue
            if frame_id - track.last_frame_id > 5:
                stale_track_ids.append(track_id)
        for track_id in stale_track_ids:
            del active_tracks[track_id]

        if annotated is not None and image_path is not None and SAVE_ANNOTATED_FRAMES:
            save_annotated_frame(OUTPUT_DIR, image_path, annotated)

    finalize_outputs(OUTPUT_DIR, tracks_by_id, tracked_frames)


def run_bytetrack_tracking():
    ensure_ultralytics()
    _, _, frame_metadata = load_tracking_context()

    vehicle_model = detection_model.load_model(detection_model.VEHICLE_MODEL_PATH)
    plate_model = detection_model.load_model(detection_model.PLATE_MODEL_PATH)

    tracks_by_id = {}
    tracked_frames = []

    results = vehicle_model.track(
        source=str(detection_model.choose_input_dir()),
        stream=True,
        persist=True,
        conf=detection_model.VEHICLE_CONFIDENCE,
        tracker=resolve_bytetrack_config(),
        verbose=False,
    )

    for result in results:
        image_path = Path(result.path)
        frame_image = result.orig_img
        annotated = frame_image.copy()
        frame_output_dir = OUTPUT_DIR / image_path.stem
        frame_id, timestamp = normalize_timestamp(image_path, frame_metadata)

        if result.boxes is None or result.boxes.id is None:
            if SAVE_ANNOTATED_FRAMES:
                save_annotated_frame(OUTPUT_DIR, image_path, annotated)
            continue

        for box, track_id_tensor, class_tensor, conf_tensor in zip(
            result.boxes.xyxy,
            result.boxes.id,
            result.boxes.cls,
            result.boxes.conf,
        ):
            track_id = int(track_id_tensor.item())
            class_name = result.names[int(class_tensor.item())]
            if class_name.lower() not in detection_model.VEHICLE_CLASSES:
                continue

            vehicle_bbox = [int(value) for value in box.tolist()]
            frame_output_dir.mkdir(parents=True, exist_ok=True)
            plate_record = select_best_plate(
                plate_model, frame_image, vehicle_bbox, frame_output_dir, track_id
            )
            update_track_state(
                tracks_by_id=tracks_by_id,
                track_id=track_id,
                class_name=class_name,
                vehicle_bbox=vehicle_bbox,
                frame_id=frame_id,
                timestamp=timestamp,
                source_image=str(image_path),
                confidence=float(conf_tensor.item()),
                plate_record=plate_record,
            )

            tracked_frames.append(
                {
                    "frame_id": frame_id,
                    "timestamp": timestamp,
                    "source_image": str(image_path),
                    "track_id": track_id,
                    "class_name": class_name,
                    "confidence": float(conf_tensor.item()),
                    "bbox_xyxy": vehicle_bbox,
                    "plate_bbox_xyxy": plate_record["bbox_xyxy"] if plate_record else None,
                    "tracker_backend": "bytetrack",
                }
            )
            draw_track_annotations(
                annotated,
                vehicle_bbox,
                track_id,
                class_name,
                plate_record["bbox_xyxy"] if plate_record else None,
            )

        if SAVE_ANNOTATED_FRAMES:
            save_annotated_frame(OUTPUT_DIR, image_path, annotated)

    finalize_outputs(OUTPUT_DIR, tracks_by_id, tracked_frames)


def run_deepsort_tracking():
    ensure_ultralytics()
    ensure_deepsort()

    _, image_paths, frame_metadata = load_tracking_context()
    vehicle_model = detection_model.load_model(detection_model.VEHICLE_MODEL_PATH)
    plate_model = detection_model.load_model(detection_model.PLATE_MODEL_PATH)
    tracker = DeepSort(max_age=DEEPSORT_MAX_AGE, n_init=DEEPSORT_N_INIT)

    tracks_by_id = {}
    tracked_frames = []

    def best_detection_confidence(tracked_bbox, detections):
        best_iou = 0.0
        best_confidence = 0.0
        best_class_name = "vehicle"
        for detection in detections:
            iou = intersection_over_union(tracked_bbox, detection["bbox_xyxy"])
            if iou > best_iou:
                best_iou = iou
                best_confidence = detection["confidence"]
                best_class_name = detection["class_name"]
        return best_confidence, best_class_name

    for image_path in image_paths:
        frame_image = cv2.imread(str(image_path))
        if frame_image is None:
            continue

        annotated = frame_image.copy()
        frame_output_dir = OUTPUT_DIR / image_path.stem
        frame_id, timestamp = normalize_timestamp(image_path, frame_metadata)

        boxes = detection_model.run_inference(
            vehicle_model, frame_image, detection_model.VEHICLE_CONFIDENCE
        )
        detections = detection_model.filter_vehicle_detections(
            detection_model.extract_boxes(boxes, vehicle_model.names),
            frame_image.shape[1],
            frame_image.shape[0],
        )

        raw_detections = []
        for detection in detections:
            x1, y1, x2, y2 = detection["bbox_xyxy"]
            raw_detections.append(
                (
                    [x1, y1, x2 - x1, y2 - y1],
                    detection["confidence"],
                    detection["class_name"],
                )
            )

        tracks = tracker.update_tracks(raw_detections, frame=frame_image)
        for track in tracks:
            if not track.is_confirmed():
                continue

            track_id = int(track.track_id)
            ltrb = [int(value) for value in track.to_ltrb()]
            matched_confidence, matched_class_name = best_detection_confidence(
                ltrb, detections
            )
            class_name = track.get_det_class() or matched_class_name or "vehicle"
            frame_output_dir.mkdir(parents=True, exist_ok=True)
            plate_record = select_best_plate(
                plate_model, frame_image, ltrb, frame_output_dir, track_id
            )

            update_track_state(
                tracks_by_id=tracks_by_id,
                track_id=track_id,
                class_name=class_name,
                vehicle_bbox=ltrb,
                frame_id=frame_id,
                timestamp=timestamp,
                source_image=str(image_path),
                confidence=matched_confidence,
                plate_record=plate_record,
            )

            tracked_frames.append(
                {
                    "frame_id": frame_id,
                    "timestamp": timestamp,
                    "source_image": str(image_path),
                    "track_id": track_id,
                    "class_name": class_name,
                    "confidence": matched_confidence,
                    "bbox_xyxy": ltrb,
                    "plate_bbox_xyxy": plate_record["bbox_xyxy"] if plate_record else None,
                    "tracker_backend": "deepsort",
                }
            )
            draw_track_annotations(
                annotated,
                ltrb,
                track_id,
                class_name,
                plate_record["bbox_xyxy"] if plate_record else None,
            )

        if SAVE_ANNOTATED_FRAMES:
            save_annotated_frame(OUTPUT_DIR, image_path, annotated)

    finalize_outputs(OUTPUT_DIR, tracks_by_id, tracked_frames)


def run_tracking(tracker_backend: str = TRACKER_BACKEND):
    if tracker_backend == "bytetrack":
        try:
            run_bytetrack_tracking()
        except ModuleNotFoundError as exc:
            if exc.name == "lap":
                print(
                    "ByteTrack dependency 'lap' is missing. Falling back to simple IoU tracking."
                )
                run_simple_tracking()
            else:
                raise
    elif tracker_backend == "deepsort":
        try:
            run_deepsort_tracking()
        except ImportError:
            print(
                "DeepSORT dependency is missing. Falling back to simple IoU tracking."
            )
            run_simple_tracking()
    else:
        raise ValueError(
            f"Unsupported tracker backend: {tracker_backend}. Use 'bytetrack' or 'deepsort'."
        )

    print(f"Tracked frames saved to: {OUTPUT_DIR / 'tracked_frames.json'}")
    print(f"Track summary saved to: {OUTPUT_DIR / 'track_summary.json'}")
    print(f"Annotated frames saved under: {OUTPUT_DIR / 'annotated_frames'}")


def main():
    run_tracking()


if __name__ == "__main__":
    main()
