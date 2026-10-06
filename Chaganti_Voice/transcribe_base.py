from faster_whisper import WhisperModel


AUDIO = r"C:\Users\91738\Downloads\(Audio) Part_01_Raamaayanam.m4a"
OUTPUT = "Chaganti_Voice/Part_01_Raamaayanam_base_telugu.txt"


model = WhisperModel("base", device="cpu", compute_type="int8")
segments, info = model.transcribe(
    AUDIO,
    language="te",
    task="transcribe",
    beam_size=5,
    condition_on_previous_text=False,
)

with open(OUTPUT, "w", encoding="utf-8") as text_file:
    for segment in segments:
        text_file.write(
            f"[{segment.start:.2f} - {segment.end:.2f}] "
            f"{segment.text.strip()}\n"
        )

print(f"Saved: {OUTPUT}")
