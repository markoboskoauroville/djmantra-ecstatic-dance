"""The Suno guide mix (request 76, 21.10.2026): one Centering song per element, from its steady middle, levelled to
-20 LUFS, crossfaded 6 s element to element. The audio reference for the Suno toning choir."""
import subprocess, os, json, tempfile
D = "/Volumes/EXT_1TB/MUSIC/MUSIC FOR EDITING/Centering [Marko]/"
PLAN = [("intro", "11. Calm", 30), ("a", "24. Breath of the Earth", 45), ("u", "4. Riverbank", 45), ("i", "13. Epilogue", 45),
        ("o", "12. Closeness", 45), ("ov", "22. Zense", 60), ("om", "20. Cradle of Stars", 45), ("si", "23. Aether Window", 40)]
XF = 6
T = tempfile.mkdtemp(); parts = []
def dur(f): return float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f],capture_output=True,text=True).stdout)
for i, (k, song, L) in enumerate(PLAN):
    f = D + song + ".mp4"; d = dur(f); n = L + (XF if i < len(PLAN) - 1 else 0)
    s = max(0, min(d * .3, d - n - 5))
    o = f"{T}/{i}.wav"
    subprocess.run(['ffmpeg','-v','error','-y','-ss',str(s),'-t',str(n),'-i',f,'-vn','-ac','2','-ar','44100','-af','loudnorm=I=-20:TP=-2:LRA=11',o],check=True)
    parts.append(o)
fc, last = "", "[0:a]"
for i in range(1, len(parts)):
    out = f"[x{i}]"; fc += f"{last}[{i}:a]acrossfade=d={XF}:c1=tri:c2=tri{out};"; last = out
fc += f"{last}afade=t=in:d=3,afade=t=out:st={sum(p[2] for p in PLAN)-6}:d=6[out]"
args = ['ffmpeg','-v','error','-y'] + sum([['-i', p] for p in parts], []) + ['-filter_complex', fc, '-map', '[out]', '-b:a', '256k', 'toning-guide-mix.mp3']
subprocess.run(args, check=True)
t, marks = 0, []
for k, song, L in PLAN: marks.append({"id": k, "song": song, "t": t}); t += L
json.dump({"total": t, "marks": marks}, open("toning-guide-mix.json", "w"), indent=1)
print(t, "s")
