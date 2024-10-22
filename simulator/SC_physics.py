import numpy as np

def project_vector_on_line(p, v, line, mu=0):
    """
    Проектирует вектор v на тангенциальный и нормальный векторы прямой.
    
    :param p: Кортеж (x, y) - позиция объекта.
    :param v: Кортеж (vx, vy) - вектор скорости объекта.
    :param line: Кортеж ((x1, y1), (x2, y2)) - координаты точек на прямой.
    :return: Обновленный вектор v_res после столкновения с прямой.
    """
    (x1, y1), (x2, y2) = line
    
    # Вектор прямой
    line_vector = np.array([x2 - x1, y2 - y1])
    line_vector_normalized = line_vector / np.linalg.norm(line_vector)
    
    # Тангенциальный вектор (направление линии)
    tau = line_vector_normalized
    
    # Нормальный вектор (перпендикуляр к линии)
    normal = np.array([-tau[1], tau[0]])  # Поворот на 90 градусов
    
    # Вектор от точки на линии к позиции объекта
    point_to_object = np.array(p) - np.array([x1, y1])
    
    # Проверка направления нормали
    if np.dot(point_to_object, normal) < 0:
        normal = -normal  # Изменяем направление нормали

    # Проекция V на tau
    V = np.array(v)
    Vt = np.dot(V, tau) * tau  # Тангенциальная проекция
    
    # Проекция V на нормаль
    Vn = np.dot(V, normal) * normal  # Нормальная проекция
    
    # print(p, [x1, y1], normal)
    
    if np.dot(Vn, normal) < 0:
        Vn_abs = np.sqrt(np.sum(np.square(Vn)))
        Vn = np.zeros_like(Vn)  # Обнуляем нормальную проекцию
        Vt = Vt * (1 - min(Vn_abs * mu, 1))
        
    # Результирующий вектор
    V_res = Vt + Vn
    
    return V_res

def vector_collision_on_lines(position, v, lines, mu=0):
    """
    Итеративно применяет проекции вектора v на линии.
    
    :param position: Кортеж (x, y) - позиция объекта.
    :param v: Кортеж (vx, vy) - скорость объекта.
    :param lines: Множество линий {((x1,y1),(x2,y2))}.
    :return: Обновленный вектор v_res после всех столкновений с линиями.
    """
    
    v_res = np.array(v)
    
    for line in lines:
        v_res = project_vector_on_line(position, v_res, line, mu=mu)
    
    return tuple(v_res)
