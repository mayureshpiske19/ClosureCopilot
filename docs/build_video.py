"""Build the ClosureCopilot 2-minute video: each slide + its male neural narration,
concatenated to EXACTLY 120.000s.  Uses the bundled ffmpeg from imageio-ffmpeg.
"""
import json, os, subprocess
import imageio_ffmpeg

HERE = os.path.dirname(__file__)
VO = os.path.join(HERE, "video", "vo")
FRAMES = os.path.join(HERE, "video")
OUT = os.path.join(HERE, "ClosureCopilot_demo.mp4")
FF = imageio_ffmpeg.get_ffmpeg_exe()
TARGET = 120.0

meta = json.load(open(os.path.join(VO, "meta.json")))
durs = [m["dur"] for m in meta]
n = len(durs)
GAP = (TARGET - sum(durs)) / n            # distribute remaining time as equal tail gaps
assert GAP > 0, f"narration too long ({sum(durs):.1f}s) — raise TTS rate"
print(f"speech={sum(durs):.1f}s  gap/scene={GAP:.2f}s")

VF = "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p,fps=30"


def run(args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-1500:])


scenes = []
for i, m in enumerate(meta):
    sd = durs[i] + GAP
    img = os.path.join(FRAMES, f"frame{i+1}.png")
    mp3 = os.path.join(VO, m["name"] + ".mp3")
    out = os.path.join(VO, f"scene{i+1}.mp4")
    run([FF, "-y", "-loop", "1", "-framerate", "30", "-t", f"{sd:.3f}", "-i", img,
         "-i", mp3, "-vf", VF, "-c:v", "libx264", "-preset", "medium", "-crf", "20",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-af", "apad",
         "-t", f"{sd:.3f}", out])
    scenes.append(out)
    print(f"scene{i+1}: {sd:.2f}s")

# concat
listfile = os.path.join(VO, "concat.txt")
with open(listfile, "w") as f:
    for s in scenes:
        f.write(f"file '{s.replace(os.sep, '/')}'\n")
run([FF, "-y", "-f", "concat", "-safe", "0", "-i", listfile,
     "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-r", "30",
     "-c:a", "aac", "-b:a", "192k", "-t", f"{TARGET:.3f}", "-movflags", "+faststart", OUT])
print("wrote", OUT, f"({os.path.getsize(OUT)/1e6:.2f} MB)")
