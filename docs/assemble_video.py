"""Assemble the ClosureCopilot 2-minute video: frames + TTS voiceover -> MP4 (exactly 120s)."""
import wave, os, subprocess, contextlib
import imageio_ffmpeg

VID = "docs/video"
AUD = f"{VID}/audio"
FF = imageio_ffmpeg.get_ffmpeg_exe()
TARGET = 120.0
GAP = 0.4  # pause after each segment

# read segment durations + params
durs = []
params = None
for i in range(1, 9):
    with contextlib.closing(wave.open(f"{AUD}/seg{i}.wav", "rb")) as w:
        if params is None:
            params = w.getparams()
        durs.append(w.getnframes() / w.getframerate())

nch, sw, fr = params.nchannels, params.sampwidth, params.framerate


def silence(seconds):
    return b"\x00" * int(round(seconds * fr)) * sw * nch


speech_plus_gaps = sum(durs) + GAP * 8       # gap after every segment
final_pad = max(0.0, TARGET - speech_plus_gaps)
print(f"speech={sum(durs):.1f}s  +gaps={GAP*8:.1f}s  final_pad={final_pad:.1f}s")

# build combined voice wav = seg + gap ... + final_pad, total == 120s
voice = f"{VID}/voice.wav"
with contextlib.closing(wave.open(voice, "wb")) as out:
    out.setparams(params)
    for i in range(1, 9):
        with contextlib.closing(wave.open(f"{AUD}/seg{i}.wav", "rb")) as w:
            out.writeframes(w.readframes(w.getnframes()))
        out.writeframes(silence(GAP))
    out.writeframes(silence(final_pad))

# frame durations (frame i visible during its segment + gap; last also holds final_pad)
frame_durs = [durs[i] + GAP for i in range(8)]
frame_durs[7] += final_pad
print("total video:", round(sum(frame_durs), 2), "s")

# concat file (absolute forward-slash paths, quoted for spaces)
absvid = os.path.abspath(VID).replace("\\", "/")
lines = []
for i in range(8):
    lines.append(f"file '{absvid}/frame{i+1}.png'")
    lines.append(f"duration {frame_durs[i]:.3f}")
lines.append(f"file '{absvid}/frame8.png'")  # repeat last (ffmpeg concat quirk)
with open(f"{VID}/frames.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

out_mp4 = "docs/ClosureCopilot_demo.mp4"
cmd = [FF, "-y",
       "-f", "concat", "-safe", "0", "-i", f"{VID}/frames.txt",
       "-i", voice,
       "-vf", "scale=1920:1080,fps=30,format=yuv420p",
       "-c:v", "libx264", "-preset", "medium", "-crf", "20",
       "-c:a", "aac", "-b:a", "192k",
       "-t", f"{TARGET:.3f}", "-movflags", "+faststart", out_mp4]
print("running ffmpeg...")
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode != 0:
    print("FFMPEG ERROR\n", r.stderr[-2000:])
else:
    print("saved", out_mp4)
