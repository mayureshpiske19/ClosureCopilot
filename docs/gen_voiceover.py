"""Generate the ClosureCopilot voiceover with a natural MALE neural voice (edge-tts).

Human, explanatory narration — acronyms written as R-T-L / S-D-C / U-P-F so the neural
voice speaks them cleanly. Produces mp3 segments + meta.json (durations).
"""
import asyncio, os, subprocess, json, re
import edge_tts
import imageio_ffmpeg

VOICE = "en-US-GuyNeural"
RATE = "+9%"
HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "video", "vo")
os.makedirs(OUT, exist_ok=True)
FF = imageio_ffmpeg.get_ffmpeg_exe()

SCENES = [
    ("s01", "Meet Closure Copilot — an A-I native co-pilot for the hardest part of chip "
            "design: backend closure. Hand it any backend report, and it tells you exactly "
            "where each fix belongs: R-T-L, constraints, or power intent."),
    ("s02", "P-P-A closure — power, performance, and area — is where schedules slip. You "
            "launch synthesis and timing, wait hours, and get back thousands of lines of "
            "reports. The hard part isn't reading a number; it's the judgment. Is this a real "
            "logic bug you fix in R-T-L, or just a missing constraint? That instinct lives in "
            "a few senior engineers' heads, and it doesn't scale."),
    ("s03", "Closure Copilot captures that instinct. A supervisor agent directs nine "
            "specialists. Parsers read any tool's output — timing, synthesis, power, area, "
            "U-P-F, S-D-C, even congestion. And every answer is grounded in two knowledge "
            "bases: proven P-P-A methodology, and a living memory of your specific chip."),
    ("s04", "Its core skill is fix-layer routing. A setup failure on a configuration path? "
            "It's sampled once per write, so the fix is a multi-cycle constraint in S-D-C, "
            "not a logic change. A deep combinational path? That goes back to R-T-L to "
            "pipeline. Every recommendation comes with a ready-to-paste snippet, and its "
            "P-P-A trade-off."),
    ("s05", "And it goes further. It promotes block constraints up to the top. It signs off "
            "power intent — isolation, retention, and clock gating. It compares two runs and "
            "points to the change that caused a regression. And it turns physical congestion "
            "into concrete R-T-L hints."),
    ("s06", "Under the hood: Python, a Streamlit dashboard, and Azure Open A-I — with a fully "
            "offline mode, so it runs anywhere, and the demo never breaks."),
    ("s07", "No other tool ties these together — routing, constraint promotion, and "
            "regression tracing — for the person who owns the R-T-L. Closure Copilot turns "
            "hours of triage into minutes of grounded fixes, giving every designer a senior "
            "engineer on their shoulder."),
    ("s08", "Closure Copilot. Close faster. Fix smarter."),
]


def duration(path):
    r = subprocess.run([FF, "-i", path], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", r.stderr)
    h, mm, s = float(m.group(1)), float(m.group(2)), float(m.group(3))
    return h * 3600 + mm * 60 + s


async def main():
    meta = []
    for name, text in SCENES:
        mp3 = os.path.join(OUT, name + ".mp3")
        await edge_tts.Communicate(text, VOICE, rate=RATE).save(mp3)
        d = duration(mp3)
        meta.append({"name": name, "dur": round(d, 2)})
        print(f"{name}: {d:.2f}s")
    total = sum(m["dur"] for m in meta)
    print(f"TOTAL narration: {total:.1f}s  ({int(total // 60)}:{int(total % 60):02d})")
    json.dump(meta, open(os.path.join(OUT, "meta.json"), "w"), indent=2)


asyncio.run(main())
