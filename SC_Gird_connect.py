'''
Дано
- self.robot_color
- self.base_color
- get_objects
- _get_our_raw_position
Нужно
- путь для захвата ближайшего кубика (не включая позицию кубика)
— блокируй те объекты, что заняты чужим роботом
- путь до корзины
'''

# from Test import *
# from SC_Gird import *
# from SC_detectors import *

def calculate_vertex_objects(x, y, base_map):
    for bound in base_map:
        length = bound[0]
        wight = bound[1]
        x_b = bound[2][0]
        y_b = bound[2][1]
        x_r = abs(x_b-x)
        y_r = abs(y_b - y)
        if x_r <= length and y_r <= wight:
            return bound[3]

def build_center(x1, y1, x2, y2):

    x = (x1+x2)/2
    y = (y1+y2)/2

    return x, y

def get_nearest_cube_path(data, base_map):
    paths = []
    for key, value in data.items():
        if key == 'cube':
            for index, data in enumerate(value):
                x, y = build_center(data[0], data[1], data[2], data[3])
                vertex = calculate_vertex_objects(x, y, base_map)

                paths.append(get_current_path(data, vertex))

    return paths

def add_data(g, data):
    base_map = g.return_node_coordinate()
    for key, value in data.items():
        for index, data in enumerate(value):
            x, y = build_center(data[0], data[1], data[2], data[3])
            vertex = calculate_vertex_objects(x, y, base_map)
            some_obj = [vertex, key, data[0]-data[2], data[1]-data[3], x, y]
            print(some_obj)
            g.add_object_to_node(some_obj)

def get_current_path(g, aim):

    
    # start_vertex = g.get_node_our_robot(250.0, 300.0)
    # # start_vertex = (0,0)
    # start = start_vertex
    # goal = aim

    g.remove_edge_by_objects()

    path = g.find_shortest_path(start, goal)
    g.visualize(path)
    del path[-1]

    print(path)
    return path

def create_base(data):
    size  = 5
    g = Graph(size)
    g.set_standart_map()
    add_data(g, data)
    

dict = {
    "cube": [[100, 150, 200, 250],[50, 10, 10, 50]],
    "robot": [[300, 350, 200, 250]]}

get_nearest_cube_path(dict)