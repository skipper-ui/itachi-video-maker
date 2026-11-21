import os
import shutil
import subprocess

from dotenv import load_dotenv


def main():
    load_dotenv()

    for key in ("ELEVENLABS_API_KEY", "FAL_KEY"):
        value = os.getenv(key, "")
        configured = bool(value) and not value.startswith("your_")
        print(f"{key}: {'set' if configured else 'missing (edit .env)'}")

    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise SystemExit("ffmpeg not found on PATH — install it before running.")
    version = subprocess.run(
        [ffmpeg, "-version"], capture_output=True, text=True, check=True
    ).stdout.splitlines()[0]
    print(f"ffmpeg: {version}")


if __name__ == "__main__":
    main()
