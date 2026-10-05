# Local Telugu voice cloning prototype

Uses AI4Bharat IndicF5 reference-conditioned speech synthesis. Supply your recording, its exact transcript, and new Telugu text. No training run or paid speech API is required. Similarity is approximate, and Telugu/Sanskrit pronunciation should be reviewed before using narration.

## Windows setup

From the project root, run in PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\voice_cloning\setup.ps1
```

This downloads a separate Python 3.10 and model dependencies into this folder, with a build cache in the Windows temporary directory. It leaves the existing production Python unchanged. Internet and several GB of disk space are required. The default PyTorch installation may be CPU-only; NVIDIA acceleration requires a compatible CUDA-enabled PyTorch build. CPU generation can be slow. Hardware compatibility has not yet been verified on this computer.

1. Sign into https://huggingface.co/ai4bharat/IndicF5 and accept/request access. The publisher requires accepting its conditions and sharing contact information.
2. Create a Hugging Face read token with access to this model. Keep it private.
3. Run the following locally and enter the token in the login prompt:

```powershell
powershell -ExecutionPolicy Bypass -File .\voice_cloning\login.ps1
powershell -ExecutionPolicy Bypass -File .\voice_cloning\run.ps1
```

Open http://127.0.0.1:7860. Upload or record a clear 8–12 second clip of your voice, type its exact transcript, enter a short Telugu passage, and click **Generate speech**. Download the WAV or find it in `outputs/`. The prototype limits each request to 500 characters; generate long narrations in separate passages. Stop with Ctrl+C in PowerShell.

## Local processing and downloads

The interface listens only on localhost and does not create a public Gradio share link. Audio inference runs locally. Initial model loading downloads weights and the publisher's custom Python code (`trust_remote_code=True`, as required by its documented API). This code and dependencies must be trusted. Once all model/vocoder assets are cached, offline use can be attempted with `HF_HUB_OFFLINE=1`; it has not yet been verified. Downloads are not speech-service calls.

Recordings may remain in `temp/`; generated audio remains in `outputs/`. The login token is stored under `models/`. These folders are ignored by Git but this entire project is inside OneDrive, so OneDrive may still sync them. Move the project outside synced storage if that is unwanted.

## Status and troubleshooting

This is an initial integration based on the official API, not a trained custom model. End-to-end inference and voice quality require model access and your reference recording. A 401/403 error means the Hugging Face account/token lacks access. If generation runs out of memory, close other GPU applications and shorten the passage. A missing FFmpeg error can be resolved by adding FFmpeg to PATH; the app already checks this project's `production/tools` directory.

Verified on this machine: isolated Python 3.10 environment installation, app/audio/inference-library imports, HTTP 200 from the local interface, authenticated model download, and strict checkpoint loading. PyTorch reports CUDA unavailable, so this installation currently runs on CPU. Installed versions are recorded in `requirements-installed.txt`. Offline operation and voice quality still require verification.

Windows compatibility: eager execution avoids requiring a native compiler. The loader removes compiled-module prefixes from checkpoint keys and requires a strict weight match. Inference uses the upstream batch function with SoundFile-loaded audio, avoiding TorchCodec and automatic reference truncation. Reference clips are limited to 3–15 seconds.

The first reference is `references/voice01_06-13.wav`, cut from the supplied recording at the user's 6–13 second boundaries. Its matched transcript and a new test passage are in `test_voice01.py`. Run it with `.\\voice_cloning\\.venv\\Scripts\\python.exe .\\voice_cloning\\test_voice01.py`. If the boundary clips a word, adjust the cut and transcript together before judging similarity.

Sources: [IndicF5 code and API](https://github.com/AI4Bharat/IndicF5), [model and access terms](https://huggingface.co/ai4bharat/IndicF5).

First synthesis completed on 2026-09-26: `outputs/telugu_20260926_111821_1bce5ad3.wav` (5.33 seconds, 24 kHz mono PCM). Basic signal checks passed: peak 0.723, RMS 0.123. CPU loading plus synthesis took approximately 4 minutes 40 seconds. This confirms generation works; perceived similarity and pronunciation await the user's listening review. Restart any interface launched before these fixes to use the corrected loader.
