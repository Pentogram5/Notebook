import numpy as np
from shapely.geometry import Polygon
from shapely.affinity import rotate, translate

class Collider:
    def __init__(self, poly, x=0, y=0, off_x=0, off_y=0, angle=0):
        """
        Инициализация класса Collider с заданными координатами полигона,
        положением, смещением и углом поворота.

        :param poly: Список кортежей (xi, yi) - координаты вершин полигона.
        :param x: Координата x положения коллайдера.
        :param y: Координата y положения коллайдера.
        :param off_x: Смещение по оси x относительно системы координат.
        :param off_y: Смещение по оси y относительно системы координат.
        :param angle: Угол поворота полигона в градусах (по часовой стрелке).
        """
        self.original_polygon = Polygon(poly)
        self.x = x
        self.y = y
        self.off_x = off_x
        self.off_y = off_y
        self.angle = angle

    def get_transformed_polygon(self):
        """
        Возвращает повернутый и перемещенный полигон с учетом смещения.

        :return: Преобразованный полигон.
        """
        pol = self.original_polygon
        pol = translate(pol, xoff=self.off_x, yoff=self.off_y)
        
        # Сначала поворачиваем полигон
        pol = rotate(pol, self.angle, origin='centroid')
        
        # Затем перемещаем его с учетом положения и смещения
        pol = translate(pol, xoff=self.x, yoff=self.y)
        
        return pol

    @staticmethod
    def are_collided(obj1, obj2):
        """
        Проверяет, пересекаются ли два полигона.

        :param obj1: Первый объект Collider.
        :param obj2: Второй объект Collider.
        :return: True, если полигоны пересекаются; иначе False.
        """
        transformed_polygon1 = obj1.get_transformed_polygon()
        transformed_polygon2 = obj2.get_transformed_polygon()
        
        # print(transformed_polygon1)
        # # print(transformed_polygon2)
        # print(obj2.x, obj2.y)
        # print(transformed_polygon1.intersects(transformed_polygon2))
        # print()
        
        return transformed_polygon1.intersects(transformed_polygon2)

# Пример использования
if __name__ == "__main__":
    # Создаем два полигона с углом поворота и положением
    poly1 = [(0, 0), (2, 0), (2, 2), (0, 2)]
    poly2 = [(1, 1), (3, 1), (3, 3), (1, 3)]
    
    collider1 = Collider(poly1, x=1, y=1, off_x=0.5, off_y=0.5, angle=45)  # Поворот на 45 градусов и смещение
    collider2 = Collider(poly2)                                              # Без поворота и смещения
    
    # Проверяем на пересечение
    if Collider.are_collided(collider1, collider2):
        print("Полигоны пересекаются.")
    else:
        print("Полигоны не пересекаются.")
