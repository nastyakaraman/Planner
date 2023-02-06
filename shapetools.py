import numpy as np
from shapefile import Writer, POLYLINE, POINT


def shape_to_area(shape_fig):
    # функция для преобразования объекта библиотеки shapely в удобный для нас
    # массив нампи
    shape_rec_fig = shape_fig.shapeRecords()
    d_all_fig = shape_rec_fig.__geo_interface__
    sh = d_all_fig['features']

    # определяем тип шейп файла
    # последовательно вскрываем словари
    geometry_shp = sh[0]['geometry']
    type_shp = geometry_shp['type']
    # создаем пустой массив нампи
    areanp = np.empty((0, 3))
    if type_shp == 'Point':
        for i in range(len(sh)):
            shape_rec_fig = shape_fig.shapeRecords()[i]
            di_fig = shape_rec_fig.__geo_interface__
            di_fig_prop = di_fig['properties']
            areanp = np.append(areanp, [[di_fig_prop['Id'], di_fig_prop['X'], di_fig_prop['Y']]], axis=0)

    elif type_shp == 'Polygon':
        shape_rec_fig = geometry_shp['coordinates']
        shape_rec_fig = shape_rec_fig[0]
        for i in range(len(shape_rec_fig)):
            di_fig = shape_rec_fig[i]
            areanp = np.append(areanp, [[i + 1, di_fig[0], di_fig[1]]], axis=0)
    else:
        print('Необходимо выбрать шейп файл с точками или полигоном')

    # сортируем точки, если они созданы не по порядку
    areanp = areanp[areanp[:, 0].argsort()]

    # замыкаем полигон,если он не замкнут
    if areanp[0, 1] != areanp[-1, 1] and areanp[0, 2] != areanp[-1, 2]:
        areanp = np.append(areanp, [[0, areanp[0, 1], areanp[0, 2]]], axis=0)
    return areanp


# Модуль для вывода шейпфайлов
def write_point_shpfile(test_file, A):
    with Writer(test_file, POINT) as shp:
        shp.field('Num', 'N')
        shp.field('X', 'N', decimal=10)
        shp.field('Y', 'N', decimal=10)
        shp.field('Z', 'N', decimal=10)
        shp.field('PR', 'N')

        for ii in range(len(A)):
            shp.point(A[ii, 0], A[ii, 1])
            shp.record(Num=ii, X=A[ii, 0], Y=A[ii, 1], Z=0, PR=A[ii, 3])


def write_polyline_shpfile(test_file, A):
    with Writer(test_file, POLYLINE) as shp:
        shp.field('Num', 'N')
        shp.field('PR', 'N')
        shp.field('Xs', 'N', decimal=10)
        shp.field('Ys', 'N', decimal=10)
        shp.field('Xe', 'N', decimal=10)
        shp.field('Ye', 'N', decimal=10)
        p = -1
        for ii in range(int((len(A)) / 2)):
            p = p + 1
            x = np.empty((0, 1))
            x = np.append(x, [[A[ii + p, 2]]], axis=0)
            x = np.append(x, [[A[ii + p + 1, 2]]], axis=0)
            y = np.empty((0, 1))
            y = np.append(y, [[A[ii + p, 3]]], axis=0)
            y = np.append(y, [[A[ii + p + 1, 3]]], axis=0)
            shp.line([list(zip(x, y))])
            shp.record(Num=ii, PR=A[ii + p, 4], Xs=A[ii + p, 2], Xe=A[ii + p + 1, 2],
                       Ys=A[ii + p, 3], Ye=A[ii + p + 1, 3])