"""Full-screen 9:16 reframe of the Vision 360 ad, planned shot by shot.

Each shot is either one full-height crop that follows the subject, or panels stacked top to bottom (split screen) when
two subjects are too far apart to fit one 9:16 window. Keyframes are (time in seconds, centre x as a fraction of width),
interpolated linearly. Run: python3 reframe_plan.py INPUT.mp4 AUDIO.wav OUT.mp4
"""
import subprocess
import sys

W, H = 1920, 1080  # source


def single(a, b, kf):
    return (a, b, [dict(h_out=1920, crop_h=1080, y0=0, kf=kf)])


def split(a, b, top, bottom, crop_h=700, y_top=0, y_bottom=0):
    return (a, b, [dict(h_out=960, crop_h=crop_h, y0=y_top, kf=top), dict(h_out=960, crop_h=crop_h, y0=y_bottom, kf=bottom)])


PLAN = [
    single(0, 13.33, [(0, .70), (4.5, .70), (6.5, .50)]),                       # logo, car, lion steps out
    single(13.33, 25.10, [(13.33, .52)]),             # lion close-up, counting fingers
    single(25.10, 33.47, [(25.10, .38), (29.3, .45), (33.47, .50)]),            # lion side view
    single(33.47, 36.0, [(33.47, .50)]),                                        # lion walks into the shop
    split(36.0, 43.43, [(36, .20), (43.43, .20)], [(36, .58), (43.43, .55)], y_bottom=60),   # lion | shop owner
    split(43.43, 49.33, [(43.43, .12), (46.4, .29), (48.7, .22)],              # camera in his hand | lion's face
          [(43.43, .55), (46.4, .58), (48.7, .62)], y_top=190),
    single(49.33, 51.27, [(49.33, .47)]),                                       # camera close-up
    single(51.27, 57.87, [(51.27, .43), (53.5, .43), (54.5, .46)]),            # lion talks
    single(57.87, 58.83, [(57.87, .40)]),                                       # installer with drill
    single(58.83, 59.77, [(58.83, .48)]),                                       # lens
    single(59.77, 60.80, [(59.77, .36)]),                                       # installer, dome camera
    single(60.80, 61.70, [(60.80, .50)]),                                       # dome close-up
    single(61.70, 62.87, [(61.70, .53)]),                                       # live view on the monitor
    single(62.87, 64.03, [(62.87, .55)]),                                       # house with camera
    single(64.03, 65.83, [(64.03, .47)]),                                       # lens
    single(65.83, 71.43, [(65.83, .74), (69.8, .76), (70.9, .60)]),            # technician with tablet, video wall
    split(71.43, 75.77, [(71.43, .20)], [(71.43, .80)], crop_h=900, y_bottom=180),                        # owner + staff | technician
    single(75.77, 85.83, [(75.77, .42), (78.5, .47), (80.8, .48), (84.8, .45)]),   # lion at the video wall
    single(85.83, 90.5, [(85.83, .47), (88.0, .53), (89.5, .48)]),                                        # lion at the shop door
    (90.5, 95.90, [dict(h_out=420, crop_h=545, y0=0, kf=[(90.5, .50), (95.9, .52)]),   # the VISION 360 sign
                   dict(h_out=1500, crop_h=650, y0=330, ykf=[(90.5, 360), (92.5, 430)], kf=[(90.5, .47), (95.9, .52)])]),  # lion under it
    single(95.90, 105.84, [(95.90, .47), (100.8, .49), (104.8, .45)]),         # closing line
]


def interp(kf, start):
    """ffmpeg expression for the centre x (pixels) over the segment's local time t."""
    pts = [(t - start, c * W) for t, c in kf]
    expr = f"{pts[-1][1]:.1f}"
    for (t0, x0), (t1, x1) in reversed(list(zip(pts, pts[1:]))):
        lerp = f"{x0:.1f}+({x1 - x0:.1f})*(t-{t0:.3f})/{max(t1 - t0, 1e-3):.3f}"
        expr = f"if(lt(t,{t1:.3f}),{lerp},{expr})"
    return f"if(lt(t,{pts[0][0]:.3f}),{pts[0][1]:.1f},{expr})"


def main():
    src, audio, out = sys.argv[1:4]
    chains, labels = [], []
    for i, (a, b, panels) in enumerate(PLAN):
        parts = []
        for j, p in enumerate(panels):
            cw = round(p["crop_h"] * 1080 / p["h_out"] / 2) * 2
            ch = p["crop_h"]
            x = f"max(0,min({W - cw},({interp(p['kf'], a)})-{cw / 2}))"
            y = max(0, min(H - ch, p["y0"]))
            if "ykf" in p:  # top edge of the crop moving over time (pixels)
                y = "'max(0,min(%d,%s))'" % (H - ch, interp([(tt, v / W) for tt, v in p["ykf"]], a))
            lbl = f"s{i}p{j}"
            edge = ",drawbox=y=ih-4:w=iw:h=4:color=white@0.9:t=fill" if j < len(panels) - 1 else ""
            chains.append(f"[v{i}_{j}]crop={cw}:{ch}:'{x}':{y},scale=1080:{p['h_out']}:flags=lanczos,setsar=1{edge}[{lbl}]")
            parts.append(lbl)
        n = len(panels)
        head = f"[0:v]trim=start={a}:end={b},setpts=PTS-STARTPTS" + (f",split={n}" if n > 1 else "")
        chains.insert(len(chains) - n, head + "".join(f"[v{i}_{j}]" for j in range(n)))
        if n > 1:
            chains.append("".join(f"[{l}]" for l in parts) + f"vstack=inputs={n}[seg{i}]")
        else:
            chains[-1] = chains[-1].replace(f"[{parts[0]}]", f"[seg{i}]")
        labels.append(f"[seg{i}]")
    chains.append("".join(labels) + f"concat=n={len(labels)}:v=1:a=0,fps=30,format=yuv420p[v]")
    graph = ";\n".join(chains)
    open(out + ".filter.txt", "w").write(graph)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-i", audio, "-filter_complex_script", out + ".filter.txt",
                    "-map", "[v]", "-map", "1:a", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], check=True)


if __name__ == "__main__":
    main()
