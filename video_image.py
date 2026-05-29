import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import ffmpeg

INPUT_VIDEO = "/home/kirat/my_proj_dream/Bangalore City Drive _ Exploring the Streets with My Dashcam 🚗1005 day_1080p.mp4"
OUTPUT_DIR = Path("frames")
OUTPUT_FORMAT = "jpg"  # Supported: jpg, png, webp
OUTPUT_PATTERN = f"frame_%06d.{OUTPUT_FORMAT}"
TARGET_FPS = 5
METADATA_JSON = "frame_metadata.json"
METADATA_TXT = "frame_metadata.txt"

# JPEG quality scale: 1 (best) .. 31 (worst)
JPEG_QUALITY = 2
PNG_COMPRESSION_LEVEL = 2
WEBP_LOSSLESS = True
WEBP_QUALITY = 95

# Keep output dimensions aligned with source dimensions.
FORCE_SOURCE_RESOLUTION = True
FORCE_PIXEL_FORMAT = True
JPEG_PIXEL_FORMAT = "yuvj420p"

# Keyframe-only mode can produce sharper frames but non-uniform timestamps.
EXTRACT_KEYFRAMES_ONLY = False


def parse_fraction(value):
    if not value:
        return 0.0
    if "/" in value:
        numerator, denominator = value.split("/", 1)
        denominator_value = float(denominator)
        if denominator_value == 0:
            return 0.0
        return float(numerator) / denominator_value
    return float(value)


def load_video_metadata(input_video):
    probe = ffmpeg.probe(input_video)
    video_stream = next(
        (
            stream
            for stream in probe.get("streams", [])
            if stream.get("codec_type") == "video"
        ),
        None,
    )
    if video_stream is None:
        raise ValueError("No video stream found in the input file.")

    source_fps = parse_fraction(video_stream.get("avg_frame_rate", "0/0"))
    if source_fps <= 0:
        source_fps = parse_fraction(video_stream.get("r_frame_rate", "0/0"))
    if source_fps <= 0:
        raise ValueError("Could not determine source FPS from the input video.")

    creation_time = (
        video_stream.get("tags", {}).get("creation_time")
        or probe.get("format", {}).get("tags", {}).get("creation_time")
    )
    bit_rate = video_stream.get("bit_rate") or probe.get("format", {}).get("bit_rate")

    return {
        "width": int(video_stream["width"]),
        "height": int(video_stream["height"]),
        "source_fps": source_fps,
        "creation_time": creation_time,
        "bit_rate": int(bit_rate) if bit_rate else None,
    }


def build_video_filter(video_info):
    filters = []
    if EXTRACT_KEYFRAMES_ONLY:
        filters.append("select='eq(pict_type\\,I)'")
    else:
        filters.append(f"fps={TARGET_FPS}")

    if FORCE_SOURCE_RESOLUTION:
        filters.append(
            f"scale={video_info['width']}:{video_info['height']}:flags=lanczos"
        )

    return ",".join(filters)


def build_output_kwargs(video_info):
    output_kwargs = {"vf": build_video_filter(video_info)}

    if OUTPUT_FORMAT == "jpg":
        output_kwargs["q:v"] = JPEG_QUALITY
        if FORCE_PIXEL_FORMAT:
            output_kwargs["pix_fmt"] = JPEG_PIXEL_FORMAT
    elif OUTPUT_FORMAT == "png":
        output_kwargs["compression_level"] = PNG_COMPRESSION_LEVEL
        if FORCE_PIXEL_FORMAT:
            output_kwargs["pix_fmt"] = "rgb24"
    elif OUTPUT_FORMAT == "webp":
        output_kwargs["lossless"] = 1 if WEBP_LOSSLESS else 0
        if not WEBP_LOSSLESS:
            output_kwargs["q:v"] = WEBP_QUALITY
        if FORCE_PIXEL_FORMAT:
            output_kwargs["pix_fmt"] = "yuv420p"
    else:
        raise ValueError("OUTPUT_FORMAT must be one of: jpg, png, webp")

    if EXTRACT_KEYFRAMES_ONLY:
        output_kwargs["vsync"] = "vfr"

    return output_kwargs


def parse_creation_time(creation_time):
    if not creation_time:
        return None
    normalized = creation_time.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def build_frame_records(frame_files, video_info):
    base_utc = parse_creation_time(video_info["creation_time"])
    records = []

    for index, frame_path in enumerate(frame_files, start=1):
        video_timestamp_ms = (
            round(((index - 1) / TARGET_FPS) * 1000, 3)
            if not EXTRACT_KEYFRAMES_ONLY
            else None
        )
        frame_record = {
            "frame_id": index,
            "filename": frame_path.name,
            "image_path": str(frame_path),
            "video_timestamp_ms": video_timestamp_ms,
            "video_timestamp_seconds": (
                round(video_timestamp_ms / 1000, 3)
                if video_timestamp_ms is not None
                else None
            ),
            "timestamp_utc": None,
            "source": INPUT_VIDEO,
            "target_fps": TARGET_FPS,
            "source_fps": video_info["source_fps"],
            "width": video_info["width"],
            "height": video_info["height"],
        }
        if base_utc is not None and video_timestamp_ms is not None:
            frame_record["timestamp_utc"] = (
                base_utc + timedelta(milliseconds=video_timestamp_ms)
            ).isoformat(timespec="milliseconds")
        records.append(frame_record)

    return records


def write_metadata(records, video_info):
    json_path = OUTPUT_DIR / METADATA_JSON
    txt_path = OUTPUT_DIR / METADATA_TXT
    source_creation_time = parse_creation_time(video_info["creation_time"])

    payload = {
        "input_video": INPUT_VIDEO,
        "output_dir": str(OUTPUT_DIR),
        "output_pattern": OUTPUT_PATTERN,
        "output_format": OUTPUT_FORMAT,
        "target_fps": TARGET_FPS,
        "extract_keyframes_only": EXTRACT_KEYFRAMES_ONLY,
        "jpeg_quality": JPEG_QUALITY if OUTPUT_FORMAT == "jpg" else None,
        "force_source_resolution": FORCE_SOURCE_RESOLUTION,
        "force_pixel_format": FORCE_PIXEL_FORMAT,
        "pixel_format": JPEG_PIXEL_FORMAT if OUTPUT_FORMAT == "jpg" else None,
        "source_fps": video_info["source_fps"],
        "source_bit_rate": video_info["bit_rate"],
        "width": video_info["width"],
        "height": video_info["height"],
        "source_creation_time_utc": source_creation_time.isoformat(
            timespec="milliseconds"
        )
        if source_creation_time is not None
        else None,
        "frame_count": len(records),
        "frames": records,
    }

    with json_path.open("w", encoding="utf-8") as json_file:
        json.dump(payload, json_file, indent=2)

    with txt_path.open("w", encoding="utf-8") as txt_file:
        for record in records:
            txt_file.write(
                "frame_id={frame_id}, filename={filename}, "
                "video_timestamp_ms={video_timestamp_ms}, timestamp_utc={timestamp_utc}\n".format(
                    **record
                )
            )


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    video_info = load_video_metadata(INPUT_VIDEO)

    ffmpeg.input(INPUT_VIDEO).output(
        str(OUTPUT_DIR / OUTPUT_PATTERN), **build_output_kwargs(video_info)
    ).run()

    frame_files = sorted(OUTPUT_DIR.glob(f"frame_*.{OUTPUT_FORMAT}"))
    frame_records = build_frame_records(frame_files, video_info)
    write_metadata(frame_records, video_info)


if __name__ == "__main__":
    main()
