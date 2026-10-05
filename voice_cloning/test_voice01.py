"""Generate the first listening sample with the user-confirmed 6–13s reference."""
from pathlib import Path
import app

reference = Path(__file__).parent / "references" / "voice01_06-13.wav"
transcript = 'నమస్తే. ఇది "పురాణామృతం" ఛానల్. ఈ రోజు నుండి మనం మొదలుపెడుతున్నాం, సంపూర్ణ వాల్మీకి రామాయణం యొక్క ప్రయాణాన్ని.'
text = "మన జీవితానికి దారి చూపే గొప్ప కథ రామాయణం. ఈ ప్రయాణంలో మనమందరం కలిసి ముందుకు సాగుదాం."

if __name__ == "__main__":
    print("Loading model and generating the first voice sample...", flush=True)
    result, _ = app.generate(str(reference), transcript, text)
    print("Generated:", result, flush=True)
