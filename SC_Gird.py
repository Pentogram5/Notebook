import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import heapq

class Graph:
    def __init__(self, rows, cols):
        """
        Инициализация графа для прямоугольника.
        :param rows: Количество строк.
        :param cols: Количество столбцов.
        """
        self.rows = rows
        self.cols = cols
        self.edges = []
        self.objects = {}
        self.node_properties = {}  # Словарь для хранения свойств узлов (размеры и координаты центра)
        self.build_rectangular_graph()

    def build_rectangular_graph(self):
        """
        Строит граф по форме прямоугольника с рёбрами между соседними вершинами, включая диагональные связи.
        """
        for i in range(self.rows):
            for j in range(self.cols):
                # Связываем узел (i, j) с соседями справа и снизу, если они есть
                if i < self.rows - 1:
                    self.edges.append(((i, j), (i + 1, j), 1))  # Связь с нижним соседом, вес 1
                if j < self.cols - 1:
                    self.edges.append(((i, j), (i, j + 1), 1))  # Связь с правым соседом, вес 1
                
                # # Добавляем диагональные связи с более высоким весом
                # if i < self.rows - 1 and j < self.cols - 1:
                #     self.edges.append(((i, j), (i + 1, j + 1), 2))  # Связь с нижним правым соседом, вес 2
                # if i < self.rows - 1 and j > 0:
                #     self.edges.append(((i, j), (i + 1, j - 1), 2))  # Связь с нижним левым соседом, вес 2

    def add_object_to_node(self, object_data):
        """
        Размещает объект в указанной вершине графа. 
        Поддерживается несколько объектов на один узел.
        """
        node = object_data[0]
        name = object_data[1]
        if 'alien' in name :
            status = 'impassable'
        else:
            status = 'passable'
        length = object_data[2]
        width= object_data[3]
        center_x = object_data [4]
        center_y=object_data[5]
        # Если в вершине ещё нет объектов, создаём список
        if node not in self.objects:
            self.objects[node] = []
        
        self.objects[node].append({
            'name': name,
            'status': status,
            'length': length,
            'width': width,
            'center': (center_x, center_y)
        })
        # print(f"Объект '{name}' размера {length}x{width} с центром ({center_x}, {center_y}) добавлен в узел {node}.")

    def set_node_properties(self, node, length, width, center_x, center_y):
        """
        Устанавливает длину, ширину и координаты центра для узла.
        :param node: Вершина, для которой нужно установить размер и центр.
        :param length: Длина узла.
        :param width: Ширина узла.
        :param center_x: X-координата центра.
        :param center_y: Y-координата центра.
        """
        self.node_properties[node] = {
            'length': length,
            'width': width,
            'center': (center_x, center_y)
        }
        # print(f"Размер {length}x{width} с центром ({center_x}, {center_y}) установлен для узла {node}.")

    def get_node_properties(self, node):
        """
        Возвращает длину, ширину и координаты центра узла.
        :param node: Вершина, свойства которой нужно получить.
        :return: Словарь с длиной, шириной и координатами центра узла.
        """
        return self.node_properties.get(node, "Свойства не установлены")

    def remove_edge(self, edges_to_remove):
        """
        Удаляет связь между двумя вершинами, если такая связь существует.

        """
        for edge in edges_to_remove:
            self.edges = [e for e in self.edges if frozenset([e[0], e[1]]) != frozenset(edge)]


    def remove_edge_by_objects(self):
            
        for node, properties in self.node_properties.items():
            if node in self.objects:
                for objects in self.objects[node]:
                    objects = self.objects[node]
                    for obj in objects:
                        obj_status = obj['status']
                        if obj_status == 'impassable':
                            edges_to_remove = [((node[0], node[1]), (node[0]+1, node[1])), 
                                               ((node[0], node[1]), (node[0], node[1]+1)), 
                                               ((node[0], node[1]), (node[0]-1, node[1])),
                                               ((node[0], node[1]), (node[0], node[1]-1))]
                            
                            self.remove_edge(edges_to_remove)




    def find_shortest_path(self, start, goal):
        """
        Находит кратчайший путь между двумя вершинами графа с помощью модифицированного алгоритма Дейкстры,
        который минимизирует количество поворотов и учитывает вес рёбер.
        :param start: Начальная вершина.
        :param goal: Конечная вершина.
        :return: Список вершин, представляющий кратчайший путь.
        """
        G = nx.Graph()

        # Добавляем рёбра в граф с учётом их веса
        for u, v, weight in self.edges:
            G.add_edge(u, v, weight=weight)

        # Функция для вычисления направления между двумя вершинами
        def get_direction(node1, node2):
            return (node2[0] - node1[0], node2[1] - node1[1])

        # Ищем кратчайший путь с минимальным количеством поворотов
        open_set = []
        heapq.heappush(open_set, (0, start, None))  # None для предыдущего направления
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}
        directions = {}  # Хранит направление для каждой вершины

        while open_set:
            current_cost, current, previous_direction = heapq.heappop(open_set)

            if current == goal:
                return self.reconstruct_path(came_from, current)

            for neighbor in G.neighbors(current):
                tentative_g_score = current_cost + G[current][neighbor]['weight']

                # Определяем текущее направление
                new_direction = get_direction(current, neighbor)

                # Штраф за поворот
                turn_penalty = 0
                if previous_direction is not None and new_direction != previous_direction:
                    turn_penalty = 10  # Более высокий штраф за поворот

                tentative_g_score += turn_penalty

                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                    directions[neighbor] = new_direction
                    heapq.heappush(open_set, (f_score[neighbor], neighbor, new_direction))

        return []

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def reconstruct_path(self, came_from, current):
        """
        Восстанавливает путь от начальной до текущей вершины на основе карты came_from.
        :param came_from: Словарь, где ключ — это вершина, а значение — предыдущая вершина, откуда был сделан шаг.
        :param current: Текущая вершина, до которой нужно восстановить путь.
        :return: Список вершин, представляющий путь от начала до текущей вершины.
        """
        total_path = [current]  # Начинаем с целевой вершины
        while current in came_from:
            current = came_from[current]  # Переходим к предыдущей вершине
            total_path.append(current)  # Добавляем её в путь

        return total_path[::-1]  # Возвращаем путь в прямом порядке (от начальной до целевой вершины)

    def visualize(self, path=None):
        """
        Визуализация графа с объектами в вершинах и опционально с кратчайшим путём.
        Отображаются прямоугольники с размерами узлов, а также грани между ними, если связи отсутствуют.
        :param path: Список вершин, представляющий кратчайший путь (опционально).
        """
        G = nx.Graph()

        # Добавление узлов и рёбер в граф
        for edge in self.edges:
            G.add_edge(edge[0], edge[1])

        fig, ax = plt.subplots()

        # Визуализация узлов как прямоугольников
        for node, properties in self.node_properties.items():
            length = properties['length']
            width = properties['width']
            center_x, center_y = properties['center']

            # Координаты нижнего левого угла для правильного построения
            lower_left_x = center_x - width / 2
            lower_left_y = center_y - length / 2

            # Рисуем прямоугольник
            rect = patches.Rectangle((lower_left_x, lower_left_y), width, length, linewidth=1, edgecolor='blue', facecolor='lightblue')
            ax.add_patch(rect)

            # Подпись для узла
            plt.text(center_x, center_y, f"{node}", ha='center', va='center', fontsize=10)

            if node in self.objects:
                for objects in self.objects[node]:
                    objects = self.objects[node]
                    for obj in objects:
                        obj_length = obj['length']
                        obj_width = obj['width']
                        obj_center_x, obj_center_y = obj['center']
                        # Координаты нижнего левого угла для объекта
                        obj_lower_left_x = obj_center_x - obj_width / 2
                        obj_lower_left_y = obj_center_y - obj_length / 2

                        # Рисуем прямоугольник для объекта
                        obj_rect = patches.Rectangle((obj_lower_left_x, obj_lower_left_y), obj_width, obj_length, linewidth=1, edgecolor='green', facecolor='lightgreen')
                        ax.add_patch(obj_rect)

                        # Подпись для объекта
                        plt.text(obj_center_x, obj_center_y+7, obj['name'], ha='center', va='center', fontsize=8, color='black')


        # Проверка наличия связей и выделение чёрных граней, где их нет
        for i in range(self.rows):
            for j in range(self.cols):
                current_node = (i, j)

                # Проверяем связь с правым соседом
                if j < self.cols - 1:
                    right_neighbor = (i, j + 1)
                    if not G.has_edge(current_node, right_neighbor):
                        # Нарисовать чёрную грань
                        current_props = self.node_properties[current_node]
                        right_props = self.node_properties[right_neighbor]
                        right_x = current_props['center'][0] + current_props['width'] / 2
                        right_y_top = current_props['center'][1] + current_props['length'] / 2
                        right_y_bottom = current_props['center'][1] - current_props['length'] / 2
                        plt.plot([right_x, right_x], [right_y_bottom, right_y_top], color='black', linewidth=2)

                # Проверяем связь с нижним соседом
                if i < self.rows - 1:
                    bottom_neighbor = (i + 1, j)
                    if not G.has_edge(current_node, bottom_neighbor):
                        # Нарисовать чёрную грань
                        current_props = self.node_properties[current_node]
                        bottom_props = self.node_properties[bottom_neighbor]
                        bottom_y = current_props['center'][1] + current_props['length'] / 2
                        bottom_x_left = current_props['center'][0] - current_props['width'] / 2
                        bottom_x_right = current_props['center'][0] + current_props['width'] / 2
                        plt.plot([bottom_x_left, bottom_x_right], [bottom_y, bottom_y], color='black', linewidth=2)

        # Если путь задан, визуализируем его красными линиями
        if path:
            path_edges = list(zip(path, path[1:]))
            for edge in path_edges:
                node1_props = self.node_properties[edge[0]]
                node2_props = self.node_properties[edge[1]]
                x1, y1 = node1_props['center']
                x2, y2 = node2_props['center']
                plt.plot([x1, x2], [y1, y2], color='red', linewidth=2)

        ax.set_aspect('equal', adjustable='box')
        plt.title(f"Rectangular Graph Visualization ({self.rows}x{self.cols})")
        plt.show()


# Пример использования

# Пример использования для графа 5x5, где для всех узлов заданы размеры и центры

# Размеры графа
rows = cols = 5

# Создаём граф
g = Graph(rows, cols)

start = (0, 0)
goal = (4, 4)

g.set_node_properties((0, 0), 95, 45, 22.5, 47.5)
g.set_node_properties((0, 1), 95, 70, 80, 47.5)
g.set_node_properties((0, 2), 95, 70, 150, 47.5)
g.set_node_properties((0, 3), 95, 70, 220, 47.5)
g.set_node_properties((0, 4), 95, 45, 277.5, 47.5)

g.set_node_properties((1, 0), 60, 45, 22.5, 125)
g.set_node_properties((1, 1), 55, 60, 80, 127.5)
g.set_node_properties((1, 2), 50, 80, 150, 125)
g.set_node_properties((1, 3), 55, 60, 220, 127.5)
g.set_node_properties((1, 4), 60, 45, 277.5, 125)

g.set_node_properties((2, 0), 70, 45, 22.5, 190)
g.set_node_properties((2, 1), 70, 60, 80, 190)
g.set_node_properties((2, 2), 70, 70, 150, 190)
g.set_node_properties((2, 3), 70, 60, 220, 190)
g.set_node_properties((2, 4), 70, 45, 277.5, 190)

g.set_node_properties((3, 0), 65, 45, 22.5, 257.5)
g.set_node_properties((3, 1), 60, 60, 80, 255)
g.set_node_properties((3, 2), 55, 80, 150, 257.5)
g.set_node_properties((3, 3), 60, 60, 220, 255)
g.set_node_properties((3, 4), 65, 45, 277.5, 257.5)

g.set_node_properties((4, 0), 95, 45, 22.5, 337.5)
g.set_node_properties((4, 1), 95, 70, 80, 337.5)
g.set_node_properties((4, 2), 95, 70, 150, 337.5)
g.set_node_properties((4, 3), 95, 70, 220, 337.5)
g.set_node_properties((4, 4), 95, 45, 277.5, 337.5)

сube1_position = [(4, 4), 'cube', 5, 5, 280, 340]
cube2_position = [(4, 4), 'cube', 5, 5, 280, 340]

sphere_position = [(2, 2), 'sphere', 5, 5, 150, 190]

base1_position = [(2, 0), 'base', 42, 29.7, 29.7/2, 190]
base2_position = [(2, 4), 'base', 42, 29.7, 300-29.7/2, 190]

backet1_position = [(2, 2), 'backet', 15, 10, 5, 190]
basket2_position = [(4, 4), 'backet', 15, 10, 295, 190]

button1_position = [(2, 2), 'button', 16, 20, 150, 8]
button2_position = [(4, 4), 'button', 16, 20, 150, 385-8]

out_robot_position = [start, 'our', 25, 29, 22.5, 47.5]
alien_robot_position = [(1, 4), 'alien', 29, 25, 277.5, 125]

g.add_object_to_node(сube1_position)
g.add_object_to_node(сube1_position)

g.add_object_to_node(sphere_position)

g.add_object_to_node(base1_position)
g.add_object_to_node(base2_position)

g.add_object_to_node(backet1_position)
g.add_object_to_node(basket2_position)

g.add_object_to_node(button1_position)
g.add_object_to_node(button2_position)

g.add_object_to_node(button1_position)
g.add_object_to_node(button2_position)

g.add_object_to_node(out_robot_position)
g.add_object_to_node(alien_robot_position)

edges_to_remove = [((1, 0), (1, 1)), ((0, 1), (1, 1)), 
                   ((1, 3), (1, 4)),((1, 3), (0, 3)), 
                   ((4, 3), (3, 3)),((3, 3), (3, 4)),
                   ((4, 1), (3,1)),((3, 0), (3, 1)),
                   ((2, 2), (1,2)),((2, 2), (3, 2)),
                   ((2, 0), (2,1)),((2, 3), (2, 4)),]

g.remove_edge(edges_to_remove)

g.remove_edge_by_objects()


# Пример поиска кратчайшего пути
start = (0, 0)
goal = (4, 4)
path = g.find_shortest_path(start, goal)
print(f"Кратчайший путь: {path}")

# Визуализируем граф с кратчайшим путём
g.visualize(path)

