#!/usr/bin/env python3
"""Independent dialogue transcript of the centre (dialogue) channel with faster-whisper.
Usage: transcribe.py <wav> <out.json> [model]  -> segments with word timestamps."""
import sys, json, time
import numpy as np
from scipy.io import wavfile
from faster_whisper import WhisperModel
wav, out = sys.argv[1], sys.argv[2]
model = sys.argv[3] if len(sys.argv) > 3 else "mobiuslabsgmbh/faster-whisper-large-v3-turbo"
m = WhisperModel(model, device="cpu", compute_type="int8", cpu_threads=3)
t0 = time.time()
sr, a = wavfile.read(wav); assert sr == 16000
audio = (a.astype(np.float32) / 32768.0)
segs, info = m.transcribe(audio, language="en", word_timestamps=True, vad_filter=True,
                          vad_parameters={"min_silence_duration_ms": 400}, condition_on_previous_text=False)
res = []
with open(out + ".partial.txt", "w") as pf:
    for s in segs:
        res.append({"start": s.start, "end": s.end, "text": s.text.strip(),
                    "avg_logprob": s.avg_logprob, "no_speech_prob": s.no_speech_prob,
                    "words": [{"s": w.start, "e": w.end, "w": w.word, "p": w.probability} for w in (s.words or [])]})
        pf.write(f"{s.start:9.2f} {s.end:9.2f} {s.text.strip()}\n"); pf.flush()
json.dump({"model": model, "duration": info.duration, "segments": res, "elapsed_s": time.time()-t0}, open(out, "w"), indent=1)
print("done", len(res), "segments in", round(time.time()-t0), "s")
