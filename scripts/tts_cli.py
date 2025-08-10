#!/usr/bin/env python3
import argparse
import os
import sys

from kittentts import KittenTTS


def parse_args():
    parser = argparse.ArgumentParser(description="Synthesize speech with KittenTTS (Docker-friendly).\nExamples:\n  tts -t 'Hello' -o /data/out.wav\n  tts -t 'Hi' --voice expr-voice-5-f --speed 1.1 -o /data/out.wav\n", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-t", "--text", help="Text to synthesize")
    parser.add_argument("-o", "--output", help="Output WAV path (e.g. /data/out.wav)")
    parser.add_argument("--voice", default="expr-voice-5-m", help="Voice to use")
    parser.add_argument("--speed", type=float, default=1.0, help="Speech speed (1.0 = normal)")
    parser.add_argument("--repo", default="KittenML/kitten-tts-nano-0.1", help="Hugging Face model repo id")
    parser.add_argument("--cache-dir", default=None, help="Optional cache dir (inside container)")
    parser.add_argument("--list-voices", action="store_true", help="List available voices and exit")
    return parser.parse_args()


def main():
    args = parse_args()

    # Initialize model (will download from HF on first run)
    model = KittenTTS(model_name=args.repo, cache_dir=args.cache_dir)

    if args.list_voices:
        for v in model.available_voices:
            print(v)
        return 0

    if not args.text or not args.output:
        print("Error: --text and --output are required unless --list-voices is used.", file=sys.stderr)
        return 2

    # Resolve output path: relative paths are written under /data
    output_arg = args.output
    if not os.path.isabs(output_arg):
        normalized = output_arg.lstrip("./\\")
        output_path = os.path.join("/data", normalized)
    else:
        output_path = output_arg

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    # Synthesize and save file
    model.generate_to_file(args.text, output_path, voice=args.voice, speed=args.speed, sample_rate=24000)
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    sys.exit(main())
