"""Local Telugu reference-voice synthesis using AI4Bharat IndicF5."""
import os
from pathlib import Path
from datetime import datetime
from uuid import uuid4

ROOT = Path(__file__).resolve().parent
os.environ.setdefault("HF_HOME", str(ROOT / "models"))
os.environ.setdefault("GRADIO_TEMP_DIR", str(ROOT / "temp"))
os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
# Use eager execution on Windows; load_voice_model remaps compiled checkpoint keys.
os.environ.setdefault("TORCHDYNAMO_DISABLE", "1")
os.environ["PATH"] = str(ROOT.parent / "production" / "tools") + os.pathsep + os.environ.get("PATH", "")

import gradio as gr
import numpy as np
import soundfile as sf
import torch
from transformers import AutoConfig, AutoModel
from huggingface_hub import hf_hub_download
from safetensors.torch import load_file

MODEL = None


def load_voice_model():
    """Load compiled-checkpoint keys into the eager Windows model, strictly."""
    repo = "ai4bharat/IndicF5"
    config = AutoConfig.from_pretrained(repo, trust_remote_code=True)
    model = AutoModel.from_config(config, trust_remote_code=True)
    weights = load_file(hf_hub_download(repo, "model.safetensors"))
    weights = {key.replace("._orig_mod.", "."): value for key, value in weights.items()}
    model.load_state_dict(weights, strict=True)
    model.eval()
    return model


def generate(reference, transcript, text, speed=1.0, steps=32):
    global MODEL
    if not reference:
        raise gr.Error("Upload or record your voice first.")
    transcript, text = (transcript or "").strip(), (text or "").strip()
    if not transcript or not text:
        raise gr.Error("Enter both the exact recording transcript and the new Telugu text.")
    if len(text) > 500:
        raise gr.Error("For this prototype, generate short passages of up to 500 characters.")
    speed, steps = float(speed), int(steps)
    if not 0.65 <= speed <= 1.15 or steps not in (32, 48, 64):
        raise gr.Error("Use speed 0.65–1.15 and 32, 48, or 64 generation steps.")
    samples, rate = sf.read(reference, dtype="float32", always_2d=True)
    duration = len(samples) / rate
    if not 3 <= duration <= 15:
        raise gr.Error("Use a recording between 3 and 15 seconds; 8–12 seconds is a good starting point. Longer clips are shortened by IndicF5 and can lose transcript alignment.")
    if not np.isfinite(samples).all() or np.max(np.abs(samples)) < 0.001:
        raise gr.Error("The recording appears silent or invalid. Please record again.")
    try:
        if MODEL is None:
            # Official IndicF5 API uses custom model code downloaded from its repository.
            MODEL = load_voice_model()
        from f5_tts.infer.utils_infer import chunk_text, infer_batch_process
        # Read WAV with SoundFile instead of torchaudio's optional TorchCodec backend.
        # Pass the complete validated reference without automatic transcript-breaking cuts.
        max_chars = max(1, int(len(transcript.encode("utf-8")) / duration * (25 - duration) * speed))
        with torch.inference_mode():
            audio, output_rate, _ = infer_batch_process(
                (torch.from_numpy(samples.T.copy()), rate), transcript,
                chunk_text(text, max_chars=max_chars), MODEL.ema_model, MODEL.vocoder,
                device=next(MODEL.parameters()).device,
                speed=speed, nfe_step=steps,
            )
        if isinstance(audio, torch.Tensor):
            audio = audio.detach().cpu().numpy()
        audio = np.asarray(audio)
        if audio.dtype == np.int16:
            audio = audio.astype(np.float32) / 32768.0
        audio = np.asarray(audio, dtype=np.float32).squeeze()
        if audio.ndim != 1 or not audio.size or not np.isfinite(audio).all():
            raise ValueError("Model returned empty or invalid audio.")
        peak = float(np.max(np.abs(audio)))
        if peak > 1:
            audio = audio / peak * 0.98
        output_dir = ROOT / "outputs"
        output_dir.mkdir(exist_ok=True)
        output = output_dir / f"telugu_{datetime.now():%Y%m%d_%H%M%S}_{uuid4().hex[:8]}.wav"
        sf.write(output, audio, output_rate, subtype="PCM_16")
        return str(output), str(output)
    except Exception as exc:
        if "401" in str(exc) or "gated" in str(exc).lower() or "403" in str(exc):
            raise gr.Error("Model access is required. Accept access on huggingface.co/ai4bharat/IndicF5, then run login.ps1 locally.") from exc
        raise gr.Error(f"Generation failed ({type(exc).__name__}): {exc}") from exc


def main():
    with gr.Blocks(title="Telugu Voice Studio") as demo:
        gr.Markdown("# Telugu Voice Studio\nGenerate Telugu speech using your own reference voice. Start with one or two sentences.")
        gr.Markdown("Record 8–12 seconds in a quiet room without music. Type exactly what you said, including any repeated words. Voice similarity and pronunciation need listening review.")
        reference = gr.Audio(sources=["upload", "microphone"], type="filepath", format="wav", label="Your voice sample")
        transcript = gr.Textbox(label="Exact words spoken in the sample", lines=3)
        text = gr.Textbox(label="New Telugu text to speak", lines=4, value="నమస్కారం. మన రామాయణ ప్రయాణానికి స్వాగతం.")
        speed = gr.Slider(0.65, 1.15, value=0.78, step=0.01, label="Speaking speed (1.0 = original pace)")
        steps = gr.Dropdown([32, 48, 64], value=48, label="Generation steps (more takes longer; compare by listening)")
        button = gr.Button("Generate speech", variant="primary")
        player = gr.Audio(label="Generated speech", type="filepath")
        download = gr.File(label="Download WAV")
        gr.Markdown("Processing runs on this computer. First use downloads model files. Output WAV files are saved in voice_cloning/outputs. Use your own voice or a voice you have permission to clone.")
        button.click(generate, [reference, transcript, text, speed, steps], [player, download], concurrency_limit=1)
    demo.queue(max_size=4).launch(server_name="127.0.0.1", server_port=7860, share=False, inbrowser=False)


if __name__ == "__main__":
    main()
