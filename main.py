from frame_handler import *
from renderer import *
from time import time


print("loading frame")
frame_test = Frame(
    Vector2(512, 512), 2, load_act_map("act.png"), 120, period=180, circle_radius=10, line_weight=8, col=(255, 40, 255)
)

time_avg = 0
for i in range(360):
    time_before = time()
    secs_left = int(((360 - i) * time_avg) * ((360 - i) / 180)) + 1
    mins_left = secs_left // 60
    spare_secs = secs_left % 60

    print("\rprewarming... (step: {}/360, particles: {:3},"
          " avg {:2} ms per step; ETA {:02}:{:02})".format(
        i + 1, len(frame_test.particles), int(time_avg * 1000), int(mins_left), int(spare_secs)
    ), end="")
    frame_test.move_all()
    time_avg = ((time_avg * i) + (time() - time_before)) / (i + 1)

print("")

time_avg = 0
for i in range(360):
    time_before = time()
    secs_left = (((360 - i) * time_avg) // 1) + 1
    mins_left = secs_left // 60
    spare_secs = secs_left % 60

    print("\rrendering... (frame: {}/360, particles: {:3},"
          " avg {:2} ms per frame; ETA {:02}:{:02})".format(
        i + 1, len(frame_test.particles), int(time_avg * 1000), int(mins_left), int(spare_secs)
    ), end="")

    render_frame(frame_test, lambda x: (x + 0.02) ** 0.3 - 0.3092, "anim/f{}.png".format(i + 1))
    frame_test.move_all()
    time_avg = ((time_avg * i) + (time() - time_before)) / (i + 1)

print("\nmaking gif...")
stitch_anim(360, "anim/f{}.png", "360f.gif")

print("\nstitching loop...")
# this value is based off weird things. all i know is that with frequency 3.5 it loops perfectly at 206 frames and
# at frequency 2 it loops perfectly at 180 frames. i could write a calculation to do this given more info but like why
# i dont ever want to touch this code again
stitch_composite(0, 180, "overlay.png", "anim/f{}.png", "cmp/f{}.png")
stitch_anim(180, "cmp/f{}.png", "206f.gif")

print("\ncomplete!")