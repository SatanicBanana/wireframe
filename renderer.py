from PIL import Image, ImageDraw


def render_frame(frame, opacity_function, fname):
    # Given a frame, make a single image.
    # Colour particle location as circle of size 7 and opacity 1
    # Make a line of opacity (active_strength * link) for link in particle
    # Do this for every particle
    img_base = Image.new("RGB", (frame.xy.x, frame.xy.y), (0, 0, 0, 255))

    draw = ImageDraw.Draw(img_base, "RGBA")
    for point_id in frame.particles:
        point = frame.particles[point_id]
        # act_val = opacity_function(point.active_strength)
        act_val = 0.1 + (0.9 * point.active_strength)

        r = frame.circle_radius
        draw.ellipse(
            ((point.loc.x - r, point.loc.y - r), (point.loc.x + r, point.loc.y + r)),
            fill=(*[int(point.col[i] * act_val) for i in range(3)], 255)
        )

        for link in point.links.items():
            if link[0] in frame.particles:
                other_particle = frame.particles[link[0]]
                # links will always be doubled on both ends
                val = int(opacity_function(link[1] * point.active_strength) * 0.5 * 255)
                if val > 0:
                    colour = (*point.col, val)

                    # print(colour, point.loc, other_particle.loc, link[1] * point.active_strength)

                    draw.line((
                        (point.loc.x, point.loc.y), (other_particle.loc.x, other_particle.loc.y)
                    ), fill=colour, width=frame.line_weight)

    img_base.save(fname)


def render_act(frame):
    img_base = Image.new("L", (frame.xy.x, frame.xy.y), 0)

    draw = ImageDraw.Draw(img_base)
    for x in range(frame.xy.x):
        for y in range(frame.xy.y):
            amt = min(int(frame.act_map[y][x] * 255), 255)
            draw.point((x, y), fill=amt)

    img_base.save("test_act.png")


def load_act_map(path):
    im = Image.open(path)
    pixels = list(im.getdata())
    width, height = im.size
    act_map = []
    for i in range(height):
        act_map.append([])
        for j in range(width):
            px = pixels[(i * height + j)]
            if isinstance(px, tuple):
                val = px[0] / 255
            else:
                val = px / 255

            act_map[i].append(val)

    return act_map


def stitch_anim(length, f_base, save_to):
    import imageio
    images = []
    for f_id in range(length):
        images.append(imageio.imread(f_base.format(f_id + 1)))

    imageio.mimsave(save_to, images, duration=1/24)


def stitch_composite(start, length, f_overlay, f_base, f_to):
    overlay = Image.open(f_overlay)

    for f_id in range(1, length + 1):
        img_orig = Image.open(f_base.format(f_id + start))
        img_orig.paste(overlay, (0, 0), overlay)
        img_orig.save(f_to.format(f_id))


def find_loop(f_base, length):
    orig = Image.open(f_base.format("1"))

    for f_id in range(1, length):
        cmp = Image.open(f_base.format(f_id + 1))
        if orig.getdata() == cmp.getdata():
            return f_id
