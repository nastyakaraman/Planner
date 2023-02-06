# Данный скрипт разбивает указанную площадь на рядовые профили и пикеты через заданные интервалы.
# Для работы скрипта необходим .shp файл, содержащий полигон или точки.
# Обратите внимание, что в случае работы с точками необходимо задание полей X, Y в формате double
# и поля Id c нумерацией точек(порядок не важен) в атрибутивной таблице

# скрипт работает для всех форм полигонов

import numpy as np
from shapefile import Reader, ShapefileException  # нужно установить
import matplotlib.pyplot as plt
from sys import exit
import os

from shapely.geometry import Point, LineString
from shapely.geometry.polygon import Polygon

# импорт своих классов и функций
import ltools as l  # модуль для работы с линиями
import dirtools as d  # модуль для работы с директориями
import shapetools as sh  # модуль для работы с шейп-файлами
import polyclass as poly  # модуль для работы с классами для разбивки площади


# Вывод красного текста
def print_redtext(text):
    return print('\n', "\033[31m{}".format(text), '\033[0;0m')


# запрашиваем шейп-файл площади, с которым мы будем работать
try:
    filename = d.input_filepath('Введите директорию для shp-файла площади исследования без ковычек, апострофов и пр.: ')
    # filename=str(input('Введите директорию для shp файла площади исследования без ковычек, апострофов и пр.: '))
    shape = Reader(filename)
except ShapefileException as e:
    if not os.path.exists(filename):
        print_redtext('Ошибка в задании пути')
        filename = d.input_filepath(
            'Попробуйте еще раз. Введите директорию для shp файла площади исследования без ковычек, апострофов и пр.: ')
        shape = Reader(filename)
    else:
        print_redtext(f'Проверьте свой шейп-файл и запустите программу заново: {e}')
        exit()

else:
    print('Следуйте инструкциям на консоли')

# C:/Проекты/2022/Чукотка/gis/shp/utm/rzhaviy/area_rzhaviy_utm.shp
# C:/Users/Анастасия/Desktop/nevski_p/shp/pts_sovinoe.shp

# конвертировали шейп файл в массив нампи
area = sh.shape_to_area(shape)
# создаем объект Полигон с библиотекой shapely - на входе cписок из кортежей
area_polygon = Polygon(list(zip(area[:, 1], area[:, 2])))

# показываем полигон с нумерацией точек
plt.figure(dpi=300)
plt.title('Контур площади с пронумерованными вершинами')
plt.gca().set_aspect('equal', adjustable='box')

for i in range(len(area) - 1):
    podpis = str(int(area[i, 0]))
    plt.annotate(podpis, xy=(area[i, 1], area[i, 2]), xycoords='data',
                 textcoords='data')
plt.plot(area[:, 1], area[:, 2], area[:, 1], area[:, 2], '*')
plt.margins(0.15, 0.15)
plt.axis('off')
plt.show()

# спрашиваем через какую точку или точки должен пройти первый профиль
print('\nДолжен ли первый профиль проходить через определенные вершины?')
da_net = str(input('Введите да или нет: '))

# класс, характеризующий направление простирания профилей
profile = poly.ProfilesParametrs(da_net, area)
profile.set_alpha()  # устанавливаем азимут простирания прямой
profile.get_alpha()  # выводим азимут
profile.set_pr()  # считываем азимут и определяем простирание
profile.get_pr()  # выводим простирание

# инициализируем работу классов
pseudoaxis = poly.PseudoAxis(area, profile)
borders = poly.BordersToPseudoAxis(area, profile)
romb = poly.RombParametrs(area, borders, profile)

# необходимые параметры для разбивки по профилям
step = profile.set_step(romb.beta)
step2 = profile.set_step2()
n = profile.set_n(romb.gran03)  # предварительное количество профилей


# для нахождения координат обрезанной по площади линии по координатам
def cut_path(poly, X1, Y1, X2, Y2):
    path = LineString([[X1, Y1], [X2, Y2]])
    return path.intersection(poly)


# буферы
lines = np.empty((0, 8))  # буфер для начала и конца профиля
tochki = np.empty((0, 4))  # буфер для всех профилей
t = np.empty((0, 4))  # буфер для одного профиля
predel = romb.gran01 / step2 + 1  # количество точек на профиле с учетом горизонтального шага
in_out = []
tochki_in = np.empty((0, 4))

# разбиваем профили
Xs = romb.Xs
Ys = romb.Ys
Xe = romb.Xe
Ye = romb.Ye

cut_line = cut_path(area_polygon, Xs, Ys, Xe, Ye)
cut_cord = list(cut_line.bounds)

if cut_cord == []:
    if romb.script == 1 or romb.script == 3:
        lines = np.append(lines, [[Xs, Ys, 0, 0, 1,
                                   l.k_line(Xs, Ys, Xe, Ye), l.b_line(Xs, Ys, l.k_line(Xs, Ys, Xe, Ye)), 1]], axis=0)
        lines = np.append(lines, [[Xe, Ye, 0, 0, 1,
                                   l.k_line(Xs, Ys, Xe, Ye), l.b_line(Xs, Ys, l.k_line(Xs, Ys, Xe, Ye)), 1]], axis=0)
    else:
        lines = np.append(lines, [[Xs, Ys, 0, 0, 1,
                                   l.k_line(Xs, Ys, Xe, Ye), l.b_line(Xs, Ys, l.k_line(Xs, Ys, Xe, Ye)), 0]], axis=0)
        lines = np.append(lines, [[Xe, Ye, 0, 0, 1,
                                   l.k_line(Xs, Ys, Xe, Ye), l.b_line(Xs, Ys, l.k_line(Xs, Ys, Xe, Ye)), 0]], axis=0)
else:
    # какой-то неясный лаг в shapely
    if profile.prostiranie_PR == 'NW':  # and a.prostiranie_axis=='NW':
        cut_cord_copy = list.copy(cut_cord)
        cut_cord[1] = cut_cord_copy[3]
        cut_cord[3] = cut_cord_copy[1]
    # какой-то неясный лаг в shapely
    if cut_cord[0] == cut_cord[2]:
        cut_line_length = l.dlina(Xs, Ys, Xe, Ye)
    else:
        cut_line_length = l.dlina(cut_cord[0], cut_cord[1], cut_cord[2], cut_cord[3])
    lines = np.append(lines, [[Xs, Ys, 0, 0, 1,
                               l.k_line(Xs, Ys, Xe, Ye), l.b_line(Xs, Ys, l.k_line(Xs, Ys, Xe, Ye)), cut_line_length]],
                      axis=0)
    lines = np.append(lines, [[Xe, Ye, 0, 0, 1,
                               l.k_line(Xs, Ys, Xe, Ye), l.b_line(Xs, Ys, l.k_line(Xs, Ys, Xe, Ye)), cut_line_length]],
                      axis=0)

cut_cord = list(cut_line.bounds)

for i in range(n - 1):  # мб надо убрать единичку - вроде и не надо
    Xs = Xs + profile.XPR_s(pseudoaxis, romb)
    Ys = Ys + profile.YPR_s(pseudoaxis, romb)

    Xe = Xe + profile.XPR_s(pseudoaxis, romb)
    Ye = Ye + profile.YPR_s(pseudoaxis, romb)

    cut_line = cut_path(area_polygon, Xs, Ys, Xe, Ye)
    cut_cord = list(cut_line.bounds)

    if cut_cord == []:
        lines = np.append(lines,
                          [[Xs, Ys, 0, 0, 1, l.k_line(Xs, Ys, Xe, Ye), l.b_line(Xs, Ys, l.k_line(Xs, Ys, Xe, Ye)),
                            0]], axis=0)
        lines = np.append(lines,
                          [[Xe, Ye, 0, 0, 1, l.k_line(Xs, Ys, Xe, Ye), l.b_line(Xs, Ys, l.k_line(Xs, Ys, Xe, Ye)),
                            0]], axis=0)
    # двойки нужны потому что все с нуля, а первый профиль уже записан
    else:
        # какой-то неясный лаг в shapely
        if profile.prostiranie_PR == 'NW':  # and a.prostiranie_axis=='NW':
            cut_cord_copy = list.copy(cut_cord)
            cut_cord[1] = cut_cord_copy[3]
            cut_cord[3] = cut_cord_copy[1]

        cut_line_length = l.dlina(cut_cord[0], cut_cord[1], cut_cord[2], cut_cord[3])
        lines = np.append(lines, [[Xs, Ys, 0, 0, 2 + i, l.k_line(Xs, Ys, Xe, Ye),
                                   l.b_line(Xs, Ys, l.k_line(Xs, Ys, Xe, Ye)), cut_line_length]], axis=0)
        lines = np.append(lines, [[Xe, Ye, 0, 0, 2 + i, l.k_line(Xs, Ys, Xe, Ye),
                                   l.b_line(Xs, Ys, l.k_line(Xs, Ys, Xe, Ye)), cut_line_length]], axis=0)
ch = np.where(lines[:, 7] == 0)
ch = ch[0]
lines_cut = np.delete(lines, ch, axis=0)
# корректировка незатронутых вершин площади
l.tochki_peresechenia(area, lines_cut)

# заключительное количество профилей - проводим перпендикудяр между первым и последним профилем
n = round(l.dlina(lines_cut[1, 0], lines_cut[1, 1], lines_cut[-1, 0], lines_cut[-1, 1]) / step + 1)

# разбивка пикетов по профилю
p = -1
for i in range(n):
    p = p + 1
    Xps = lines_cut[i + p, 2]
    Yps = lines_cut[i + p, 3]
    Xpe = lines_cut[i + p + 1, 2]
    Ype = lines_cut[i + p + 1, 3]
    N_PR = lines_cut[i + p, 4]
    t = np.append(t, [[Xps, Yps, int(0), N_PR]], axis=0)

    while len(t) < (lines_cut[i + p, 7] / step2):
        Xps = Xps + profile.XPR_piket()
        Yps = Yps + profile.YPR_piket()
        t = np.append(t, [[Xps, Yps, int(0), N_PR]], axis=0)

    t = np.append(t, [[Xpe, Ype, int(0), N_PR]], axis=0)
    tochki = np.append(tochki, t, axis=0)
    t = np.empty((0, 4))  # буфер для одного профиля

# создаем буфер в 5 метров вокруг полигона
area_polygon_buf = Polygon.buffer(area_polygon, 5)

# проверка,какие точки находятся в пределах полигона
for i in range(len(tochki)):  # проверяем, попадают ли созданные нами точки в пределы полигона
    point = Point(tochki[i, 0], tochki[i, 1])  # создаем объект Точка с библоиотекой shapely
    in_out.append(str((area_polygon_buf.contains(point))))  # записываем список true/false - попадает ли точка в площадь

for i in range(len(in_out)):  # создаем список tochki_in, в котором содержатся только нужные точки
    if in_out[i] == 'True':
        tochki_in = np.append(tochki_in, [[tochki[i, 0], tochki[i, 1], tochki[i, 2], tochki[i, 3]]], axis=0)

# корректируем номера профилей
minPR = lines_cut[np.argmin(lines_cut[:, 4]), 4]
lines_cut[:, 4] = lines_cut[:, 4] - int(minPR) + 1
minPR = tochki_in[np.argmin(tochki_in[:, 3]), 3]
tochki_in[:, 3] = tochki_in[:, 3] - int(minPR) + 1
minPR = tochki[np.argmin(tochki[:, 3]), 3]
tochki[:, 3] = tochki[:, 3] - int(minPR) + 1

l.cutting_lines(lines_cut, tochki_in)

save_filename = d.dir_modify(filename, 'python_files')
if os.path.exists(save_filename) == False:
    os.mkdir(save_filename)

plt.title('Ось, соединяющая крайние точки по оси ОХ')
plt.plot(area[:, 1], area[:, 2], 'b',
         pseudoaxis.XY_axis[:, 0], pseudoaxis.XY_axis[:, 1], '*g',
         pseudoaxis.X, pseudoaxis.Y, 'r')
plt.show()

plt.title('Начальные и конечные точки профилей')
plt.plot(romb.X_pr, romb.Y_pr, 'y',
         romb.Xs, romb.Ys, '*r',
         romb.Xe, romb.Ye, '*r',
         lines[:, 0], lines[:, 1], '*g',
         area[:, 1], area[:, 2], 'b')
plt.show()

fig, ax = plt.subplots(dpi=300, constrained_layout=True)
ax.plot(tochki[:, 0], tochki[:, 1], 's', label='tochki.shp')
ax.plot(tochki_in[:, 0], tochki_in[:, 1], 'o', label='tochki_in.shp')
ax.plot(area[:, 1], area[:, 2], 'b')
ax.legend(loc='best')
ax.margins(0.15, 0.15)
ax.set_title('Точки профилей - файл tochki_in.shp')

plt.figure(dpi=300)
plt.title('Линии профилей')
p = -1
for i in range(int(len(lines_cut) / 2)):
    p = p + 1
    x1 = lines_cut[i + p, 2]
    x2 = lines_cut[i + p + 1, 2]
    y1 = lines_cut[i + p, 3]
    y2 = lines_cut[i + p + 1, 3]
    xy = np.empty((0, 2))
    xy = np.append(xy, [[x1, y1]], axis=0)
    xy = np.append(xy, [[x2, y2]], axis=0)
    if (int(lines_cut[i + p, 4])) % 5 == 0 or (int(lines_cut[i + p, 4])) == 1:
        plt.annotate(str(int(lines_cut[i + p, 4])), xy=(x1 - step * 1.5, y1 + step / 4), xycoords='data',
                     textcoords='data')
        plt.plot(area[:, 1], area[:, 2], 'b', xy[:, 0], xy[:, 1], 'r', x1, y1, '*r')
    else:
        plt.plot(area[:, 1], area[:, 2], 'b', xy[:, 0], xy[:, 1], 'k')
plt.margins(0.15, 0.15)
plt.show()

print('Шейп файлы с точками (tochki_in.shp, tochki.shp) и профилями (lines.shp) автоматически сохранены в директории: ',
      save_filename)
sh.write_point_shpfile(save_filename + '/tochki_in.shp', tochki_in)
sh.write_point_shpfile(save_filename + '/tochki.shp', tochki)
sh.write_polyline_shpfile(save_filename + '/lines.shp', lines_cut)

np.save(save_filename + '/tochki_in', tochki_in)# Данный скрипт разбивает указанную площадь на рядовые профили и пикеты через заданные интервалы.