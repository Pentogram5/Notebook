from SC_Gird import *

def calculate_vertex_objects(x, y, g): # Вычисление вершины в которой находится объект
    base_map = g.return_node_coordinate()
    for bound in base_map:
        length = bound[0]
        wight = bound[1]
        x_b = bound[2][0]
        y_b = bound[2][1]
        x_r = abs(x_b-x)
        y_r = abs(y_b - y)
        if x_r <= length and y_r <= wight:
            return bound[3]

def build_center(x1, y1, x2, y2): # Вычисление центра координат объекта

    x = (x1+x2)/2
    y = (y1+y2)/2

    return x, y

def get_closest_PL(data, robot_coordinates): # Поиск минимального пути для кубов
    paths = []
    size  = 5
    g = Graph(size)
    g.set_standart_map()
    base_map = g.return_node_coordinate()
    add_data(g, data)
    for key, value in data.items():
        if key == 'cube':
            for index, data in enumerate(value):
                try:
                    x, y = build_center(data[0], data[1], data[2], data[3])
                    vertex = calculate_vertex_objects(x, y, g)
                    paths.append(get_current_path(g, vertex, robot_coordinates))
                except Exception as e:
                    continue
    min_path_count = 100
    min_path = 0
    for p in range(0, len(paths)):
        if len(paths[p]) <= min_path_count:
            min_path_count = len(paths[p])
            min_path = paths[p]
    
    return min_path

def get_to_base(data, robot_coordinates, base_coordinates): # Поиск минимального пути до базы
    size  = 5
    g = Graph(size)
    g.set_standart_map()
    add_data(g, data)

    return get_current_path(g, base_coordinates, robot_coordinates)

def add_data(g, data): # Добавление данных в граф 
    for key, value in data.items():
        for index, data in enumerate(value):
            x, y = build_center(data[0], data[1], data[2], data[3])
            vertex = calculate_vertex_objects(x, y, g)
            some_obj = [vertex, key, data[0]-data[2], data[1]-data[3], x, y]
            print(some_obj)
            g.add_object_to_node(some_obj)

def get_current_path(g, aim, robot_coordinates): # Построение графа
    x, y = build_center(robot_coordinates[0],robot_coordinates[1],robot_coordinates[2],robot_coordinates[3])
    start_vertex = g.get_node_our_robot(x, y)
    start = start_vertex
    g.remove_edge_by_objects()
    path = g.find_shortest_path(start, aim)
    del path[-1]
    cootdinate_path = g.reconstruct_path_to_aim(path)
    return cootdinate_path


# # Example
# dict = {
#     "cube": [[100, 150, 200, 250],[50, 10, 10, 50]],
#     "robot": [[300, 350, 200, 250]],
#     "alien": [[30, 35, 20, 20]]}

# get_closest_PL(dict, [300, 350, 200, 250])