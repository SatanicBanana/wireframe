from dat import Vector2
from random import randint


class Frame:
    def __init__(self, xy, freq, act, link_range, act_range=-1, col=(0, 255, 0), period=180, circle_radius=10,
                 line_weight=8):
        self.xy = xy
        self.freq = freq

        self.act_range = act_range
        self.link_range = link_range
        self.particles = {}

        self.spawn_val = 0
        self.ran_loc = 0
        self.seed_list = make_random_set(period * 10)
        self.col = col
        self.circle_radius = circle_radius
        self.line_weight = line_weight

        if act_range == -1:
            self.act = None
            self.act_map = act

        else:
            self.act = act
            self.act_map = []
            for i in range(xy.x):
                self.act_map.append([])
                for j in range(xy.y):
                    self.act_map[i].append(-1)

            self.gen_act_map()

    def gen_act_map(self):
        # this is a very expensive computation, hence why we do it now and not every step.
        # calculate the shortest distance between every single point on the frame and the act segments.
        # since we also use manhattan distance, it's not expensive to just calculate the direct distance every time
        for x in range(self.xy.x):
            for y in range(self.xy.y):
                closest_dist = 1e100
                for point in self.act:
                    vec_diff = -point + Vector2(x, y)
                    closest_dist = min(vec_diff.sqr_magnitude(), closest_dist)

                sq_dist = closest_dist ** (1/2)

                self.act_map[x][y] = max(0, (self.act_range - sq_dist)) / self.act_range
                # print(sq_dist, self.act_map[x][y])

            if x % 25 == 0:
                print("\r", x, end="")

        print("\r", x + 1)

    def r_next(self, low, high):
        self.ran_loc += 1
        if self.ran_loc >= len(self.seed_list):
            self.ran_loc = 0

        diff = high - low
        diff_selec = self.seed_list[self.ran_loc] * diff
        return int(diff_selec + low)

    def move_all(self):
        # delete particles that return True from their movement (out of bounds)
        remove_needed = []
        for particle in self.particles.values():
            if particle.move():
                remove_needed.append(particle.id)

        for remove in remove_needed:
            self.particles.pop(remove, None)

        # spawn new particles
        # use stable randomiser so that looping occurs
        self.spawn_val += self.freq
        for i in range(int(self.spawn_val // 1)):
            if self.r_next(0, 2) == 0:
                coords = Vector2(self.r_next(0, self.xy.x), self.r_next(0, 2) * (self.xy.y - 1))
            else:
                coords = Vector2(self.r_next(0, 2) * (self.xy.x - 1), self.r_next(0, self.xy.y))

            move_available = [i - 8 for i in range(17) if abs(i) > 3]
            self.spawn_point(
                coords,
                Vector2(
                    move_available[self.r_next(0, len(move_available))],
                    move_available[self.r_next(0, len(move_available))]
                ), self.link_range, self.col
            )

        self.spawn_val = self.spawn_val % 1

    def spawn_point(self, loc, mov, link_range, col):
        point_spawn = Point(self, loc, mov, link_range, col)
        self.particles[point_spawn.id] = point_spawn


class Point:
    id_inc = 0

    def __init__(self, parent, loc, mov, link_range, col):
        self.id = Point.id_inc
        Point.id_inc += 1

        self.parent = parent
        self.loc = loc
        self.mov = mov
        self.links = {}
        self.link_range = link_range
        self.col = col
        self.active_strength = 0
        self.lifetime = 0
        self.check_active()
        self.check_links()

    def __eq__(self, other):
        return self.id == other.id

    def check_links(self):
        # get links from parent then test distance between all points
        self.links.clear()
        for point_couple in self.parent.particles:
            point = self.parent.particles[point_couple]
            # print(self.id, point.id)

            if point != self:
                dist = (-point.loc + self.loc).magnitude()
                self.links[point.id] = (max(0, (self.link_range - dist)) / self.link_range) * point.active_strength * self.active_strength

    def check_active(self):
        # refer to the pre-generated act_map to look up the current active strength
        self.active_strength = self.parent.act_map[self.loc.y][self.loc.x]

    def translate(self, vec):
        self.loc += vec
        if self.loc.x >= self.parent.xy.x or self.loc.y >= self.parent.xy.y or self.loc.x < 0 or self.loc.y < 0:
            return True

        self.check_active()
        self.check_links()

    def move(self):
        self.lifetime += 1
        return self.translate(self.mov)


# Generates a list of random numbers with length n
def make_random_set(n):
    ran = []
    for i in range(n):
        ran.append(randint(0, 1e6) / 1e6)

    return ran
