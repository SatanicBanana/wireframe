from renderer import stitch_anim, stitch_composite

# customise to make a loop from a specific frame
stitch_composite(153, 180, "overlay.png", "anim/f{}.png", "cmp/f{}.png")
stitch_anim(180, "cmp/f{}.png", "206f.gif")
