"""Slower comparison sample; retains the original render."""
import shutil
import torch
from test_voice01 import reference, transcript, text
from app import generate, ROOT

if __name__ == "__main__":
    torch.set_num_threads(4)
    torch.manual_seed(42)
    print("Generating narration: speed 0.78, 48 steps, seed 42", flush=True)
    result, _ = generate(str(reference), transcript, text, speed=0.78, steps=48)
    target = ROOT / "outputs" / "voice01_narration_v2.wav"
    if not target.exists():
        shutil.copy2(result, target)
    print("Generated:", result, flush=True)
    print("Comparison file:", target, flush=True)
