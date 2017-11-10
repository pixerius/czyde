import json
import math
import numpy
import itertools
import tkinter


WIDTH = 1024
HEIGHT = 768
MOVE_STEP = 3
ZOOM_STEP = 30
ROTATION_STEP = math.pi / 30
COLORS = ('white', 'red', 'green', 'blue', 'cyan', 'yellow', 'magenta')


with open('state.json') as f:
    state = json.load(f)


def zoom(positive):
    state['distance'] += ZOOM_STEP if positive else -ZOOM_STEP


def move(vector):
    def translate(point):
        return list(numpy.sum([point, vector], axis=0))
    state['polygons'] = list(map(lambda p: list(map(translate, p)),
                                 state['polygons']))


def turn(axis, direction):
    angle = direction * ROTATION_STEP
    matrix = {
        'x': [
            [1, 0, 0, 0],
            [0, math.cos(angle), -1 * math.sin(angle), 0],
            [0, math.sin(angle), math.cos(angle), 0],
            [0, 0, 0, 1]
        ],
        'y': [
            [math.cos(angle), 0, math.sin(angle), 0],
            [0, 1, 0, 0],
            [-1 * math.sin(angle), 0, math.cos(angle), 0],
            [0, 0, 0, 1]
        ],
        'z': [
            [math.cos(angle), -1 * math.sin(angle), 0, 0],
            [math.sin(angle), math.cos(angle), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ]
    }.get(axis)

    def rotate(point):
        return list(numpy.matmul(matrix, point + [1])[:-1])
    state['polygons'] = list(map(lambda p: list(map(rotate, p)),
                                 state['polygons']))


root = tkinter.Tk()
root.title('Camera')
canvas = tkinter.Canvas(root, width=WIDTH, height=HEIGHT, bg='black')


def priority(polygon):
    return math.sqrt(sum([e**2 for e in numpy.mean(numpy.array(polygon),
                                                   axis=0)]))


def project(point):
    return (WIDTH / 2 + (state['distance'] * point[0] / point[2]),
            HEIGHT / 2 - (state['distance'] * point[1] / point[2]))


def render():
    canvas.delete(tkinter.ALL)
    polygons = filter(lambda polygon: all(p[2] > 0 for p in polygon),
                      state['polygons'])
    polygons = sorted(polygons, key=priority, reverse=True)
    colors = itertools.cycle(COLORS)
    for polygon in map(lambda p: list(map(project, p)), polygons):
        color = next(colors)
        if len(polygon) < 3:
            canvas.create_line(polygon, fill=color)
        else:
            canvas.create_polygon(polygon, fill=color)
    canvas.pack()


def key(event):
    handler = {
        'z': lambda: zoom(True),
        'x': lambda: zoom(False),
        'a': lambda: move([MOVE_STEP, 0, 0]),
        'd': lambda: move([-MOVE_STEP, 0, 0]),
        'w': lambda: move([0, 0, -MOVE_STEP]),
        's': lambda: move([0, 0, MOVE_STEP]),
        'r': lambda: move([0, -MOVE_STEP, 0]),
        'f': lambda: move([0, MOVE_STEP, 0]),
        'e': lambda: turn('y', -1),
        'q': lambda: turn('y', 1),
        'k': lambda: turn('x', -1),
        'i': lambda: turn('x', 1),
        'j': lambda: turn('z', -1),
        'l': lambda: turn('z', 1),
    }.get(event.char)

    if handler:
        handler()
        render()


root.bind('<Key>', key)
render()
tkinter.mainloop()
