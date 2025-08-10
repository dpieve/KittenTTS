#!/usr/bin/env python3
import argparse
import os
import sys

from kittentts import KittenTTS


def parse_args():
    parser = argparse.ArgumentParser(description="Synthesize speech with KittenTTS (Docker-friendly).\nExamples:\n  tts -t 'Hello' -o /data/out.wav\n  tts -t 'Hi' --voice expr-voice-5-f --speed 1.1 -o /data/out.wav\n", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-t", "--text", required=True, help="Text to synthesize")
    parser.add_argument("-o", "--output", required=True, help="Output WAV path (e.g. /data/out.wav)")
    parser.add_argument("--voice", default="expr-voice-5-m", help="Voice to use")
    parser.add_argument("--speed", type=float, default=1.0, help="Speech speed (1.0 = normal)")
    parser.add_argument("--repo", default="KittenML/kitten-tts-nano-0.1", help="Hugging Face model repo id")
    parser.add_argument("--cache-dir", default=None, help="Optional cache dir (inside container)")
    return parser.parse_args()


def main():
    args = parse_args()

    # Ensure output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)

    # Initialize model (will download from HF on first run)
    model = KittenTTS(model_name=args.repo, cache_dir=args.cache_dir)

    # Synthesize and save file
    model.generate_to_file(args.text, args.output, voice=args.voice, speed=args.speed, sample_rate=24000)
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    sys.exit(main())
