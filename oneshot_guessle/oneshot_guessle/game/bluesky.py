import io
import logging
from pathlib import Path
from typing import Dict, List, Sequence

import requests
from requests import HTTPError
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from PIL import Image, ImageChops, ImageDraw, ImageFont

from .functions import get_clues_rows


logger = logging.getLogger(__name__)


KEYBOARD_ROWS = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
COLOUR_MAP = {
    "success": "#538d4e",
    "warning": "#b59f3b",
    "secondary": "#3a3a3c",
    "dark": "#3a3a3c",
    "light": "#818384",
}


def _normalize_bluesky_credential(value: str) -> str:
    cleaned = (value or "").strip()
    if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in {'"', "'"}:
        cleaned = cleaned[1:-1].strip()
    return cleaned


def _get_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    # Prefer explicit TrueType sources so requested sizes actually apply.
    preferred_names = [
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
        "Arial Bold.ttf" if bold else "Arial.ttf",
        "LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf",
    ]
    preferred_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]

    pil_dir = Path(ImageFont.__file__).resolve().parent
    bundled_candidates = [
        str(pil_dir / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")),
        str(pil_dir / "fonts" / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")),
    ]

    for candidate in preferred_names + bundled_candidates + preferred_paths:
        try:
            return ImageFont.truetype(str(candidate), size)
        except Exception:
            continue

    # Pillow 10.1+ supports size on load_default and returns a scalable default font.
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        logger.warning("Falling back to legacy bitmap default font; install a TrueType font for crisp scaling.")
        return ImageFont.load_default()


def _draw_centered_text(
    draw: ImageDraw.ImageDraw,
    box: Sequence[int],
    text: str,
    font: ImageFont.ImageFont,
    fill: str,
) -> None:
    left, top, right, bottom = box
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    # Offset by bbox origin to keep glyphs visually centered.
    x = left + ((right - left) - tw) // 2 - bbox[0]
    y = top + ((bottom - top) - th) // 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=fill)


def build_daily_puzzle_image_bytes(
    puzzle_number: int,
    target_word: str,
    clues: List[str],
    game_url: str,
) -> bytes:
    # Post copy is sent as Bluesky post text; image should only show puzzle visuals.
    target_word = (target_word or "").lower().strip()
    clues = [(c or "").lower().strip() for c in clues][:5]
    while len(clues) < 5:
        clues.append("")

    _, alphabet = get_clues_rows(clues, target_word)

    width = 1200
    height = 1300
    image = Image.new("RGB", (width, height), "#121213")
    draw = ImageDraw.Draw(image)

    tile_font = _get_font(64, bold=True)
    key_font = _get_font(64, bold=True)

    cols = len(target_word)
    tile_size = 96
    tile_gap = 12
    grid_top = 170
    grid_left = (width - (cols * tile_size + (cols - 1) * tile_gap)) // 2

    # Add an empty row to indicate where the player attempt would go.
    display_rows = clues + [""]

    for row_index, clue in enumerate(display_rows):
        clue = (clue or "")[:cols].ljust(cols)
        for col_index in range(cols):
            ch = clue[col_index]
            if ch == " ":
                colour = COLOUR_MAP["secondary"]
            elif ch == target_word[col_index]:
                colour = COLOUR_MAP["success"]
            elif ch in target_word:
                colour = COLOUR_MAP["warning"]
            else:
                colour = COLOUR_MAP["secondary"]

            x0 = grid_left + col_index * (tile_size + tile_gap)
            y0 = grid_top + row_index * (tile_size + tile_gap)
            box = (x0, y0, x0 + tile_size, y0 + tile_size)
            draw.rounded_rectangle(box, radius=10, fill=colour)
            _draw_centered_text(draw, box, ch.upper(), tile_font, "#ffffff")

    keyboard_top = grid_top + (len(display_rows) * tile_size) + ((len(display_rows) - 1) * tile_gap) + 28
    key_h = 82
    key_gap = 10
    left_margin = 80

    for row_idx, row_letters in enumerate(KEYBOARD_ROWS):
        key_w = 92
        row_width = len(row_letters) * key_w + (len(row_letters) - 1) * key_gap
        row_left = left_margin + (width - 2 * left_margin - row_width) // 2
        y0 = keyboard_top + row_idx * (key_h + 16)

        for i, letter in enumerate(row_letters):
            alpha_info = alphabet.get(ord(letter.lower()) - 97, {})
            alpha_colour = alpha_info.get("colour", "light")
            fill = COLOUR_MAP.get(alpha_colour, COLOUR_MAP["light"])
            x0 = row_left + i * (key_w + key_gap)
            box = (x0, y0, x0 + key_w, y0 + key_h)
            draw.rounded_rectangle(box, radius=9, fill=fill)
            _draw_centered_text(draw, box, letter, key_font, "#ffffff")

    # Safe auto-crop: trim extra background while keeping a small border.
    bg = Image.new("RGB", image.size, "#121213")
    diff = ImageChops.difference(image, bg)
    bbox = diff.getbbox()
    if bbox is not None:
        pad = 24
        left = max(0, bbox[0] - pad)
        top = max(0, bbox[1] - pad)
        right = min(image.width, bbox[2] + pad)
        bottom = min(image.height, bbox[3] + pad)
        if right > left and bottom > top:
            image = image.crop((left, top, right, bottom))

    out = io.BytesIO()
    image.save(out, format="PNG")
    return out.getvalue()


def _create_session(service_url: str, handle: str, app_password: str) -> Dict[str, str]:
    response = requests.post(
        f"{service_url}/xrpc/com.atproto.server.createSession",
        json={"identifier": handle, "password": app_password},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    return {
        "access_jwt": data["accessJwt"],
        "did": data["did"],
    }


def _upload_blob(service_url: str, access_jwt: str, image_bytes: bytes) -> Dict:
    response = requests.post(
        f"{service_url}/xrpc/com.atproto.repo.uploadBlob",
        data=image_bytes,
        headers={
            "Authorization": f"Bearer {access_jwt}",
            "Content-Type": "image/png",
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json()["blob"]


def _create_post(service_url: str, access_jwt: str, did: str, text: str, image_blob: Dict) -> None:
    payload = {
        "repo": did,
        "collection": "app.bsky.feed.post",
        "record": {
            "$type": "app.bsky.feed.post",
            "text": text,
            "createdAt": timezone.now().isoformat(),
            "embed": {
                "$type": "app.bsky.embed.images",
                "images": [
                    {
                        "alt": "Oneshot Guessle daily clues and keyboard colour hints",
                        "image": image_blob,
                    }
                ],
            },
        },
    }
    response = requests.post(
        f"{service_url}/xrpc/com.atproto.repo.createRecord",
        json=payload,
        headers={"Authorization": f"Bearer {access_jwt}"},
        timeout=10,
    )
    response.raise_for_status()


def build_daily_main_post_text(puzzle_number: int, target_word: str, game_url: str) -> str:
    text = (f"#oneshotguessle{puzzle_number}\n🧩5 Clues\n🎯1 💉 to guess the daily word\nChallenge yourself and your friends.\noneshotguessle.com #osg{puzzle_number} #Wordle #puzzle #braingames #wordporn #wordgames"
        # f"Oneshot Guessle #{puzzle_number} is live. "
        # f"Guess the hidden {len(target_word)}-letter word in one shot. "
        # "Use the clue colors to solve it. "
        # f"Play now: {game_url}"
    )
    return text[:290]


def post_daily_main_puzzle_to_bluesky(puzzle_number: int, target_word: str, clues: List[str]) -> bool:
    enabled = bool(getattr(settings, "BLUESKY_DAILY_POST_ENABLED", False))
    if not enabled:
        return False

    handle = _normalize_bluesky_credential(getattr(settings, "BLUESKY_HANDLE", ""))
    app_password = _normalize_bluesky_credential(getattr(settings, "BLUESKY_APP_PASSWORD", ""))
    service_url = getattr(settings, "BLUESKY_SERVICE_URL", "https://bsky.social").rstrip("/")
    game_url = getattr(settings, "BLUESKY_MAIN_GAME_URL", "https://oneshotguessle.com")

    if not handle or not app_password:
        logger.warning("Bluesky daily post enabled but credentials are missing.")
        return False

    day_key = timezone.localdate().isoformat()
    success_key = f"bsky:daily-main-posted:{day_key}"
    lock_key = f"bsky:daily-main-posting-lock:{day_key}"

    if cache.get(success_key):
        return False
    if not cache.add(lock_key, True, timeout=300):
        return False

    try:
        image_bytes = build_daily_puzzle_image_bytes(
            puzzle_number=puzzle_number,
            target_word=target_word,
            clues=clues,
            game_url=game_url,
        )
        text = build_daily_main_post_text(
            puzzle_number=puzzle_number,
            target_word=target_word,
            game_url=game_url,
        )

        session_data = _create_session(service_url, handle, app_password)
        blob = _upload_blob(service_url, session_data["access_jwt"], image_bytes)
        _create_post(service_url, session_data["access_jwt"], session_data["did"], text, blob)
        cache.set(success_key, True, timeout=7 * 24 * 3600)
        logger.info("Posted daily main puzzle #%s to Bluesky.", puzzle_number)
        return True
    except HTTPError as exc:
        response = getattr(exc, "response", None)
        status = getattr(response, "status_code", "unknown")
        body = ""
        if response is not None:
            try:
                body = (response.text or "")[:400]
            except Exception:
                body = ""
        logger.error(
            "Failed to post daily main puzzle to Bluesky (HTTP %s). Response body (truncated): %s",
            status,
            body,
            exc_info=True,
        )
        return False
    except Exception:
        logger.exception("Failed to post daily main puzzle to Bluesky.")
        return False
    finally:
        cache.delete(lock_key)
