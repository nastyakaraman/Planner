import math
import numpy as np

def dlina(x1, y1, x2, y2):
    # расстояние между точками
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def dlina_start_end(npm):
    return math.sqrt((npm[-1, 0] - npm[0, 0]) ** 2 + (npm[-1, 1] - npm[0, 1]) ** 2)


# коэффициент прямой k
def k_line(x1, y1, x2, y2):
    return (y1 - y2) / (x1 - x2)


# коэффициент прямой b
def b_line(x1, y1, k):
    return y1 - k * x1


# координата x точки пересечения двух прямых
def x_t_per(k1, k2, b1, b2):
    if k1 == k2:
        return int(10000000000)
    else:
        return abs((b1 - b2)) / (abs(k1 - k2))


def tochki_peresechenia(np_area, np_lines):
    # считаем коэффициенты для всех граней многогранника
    area_coef = np.empty((0, 6))
    for i in range(len(np_area)):
        xs = np_area[i, 1]
        ys = np_area[i, 2]
        if i == len(np_area) - 1:
            if np_area[i, 1] != np_area[0, 1]:
                xe = np_area[0, 1]
                ye = np_area[0, 2]
                k = k_line(np_area[i, 1], np_area[i, 2], np_area[0, 1], np_area[0, 2])
                b = b_line(np_area[i, 1], np_area[i, 2], k)
                area_coef = np.append(area_coef, [[xs, ys, xe, ye, k, b]], axis=0)
        else:
            xe = np_area[i + 1, 1]
            ye = np_area[i + 1, 2]
            k = k_line(np_area[i, 1], np_area[i, 2], np_area[i + 1, 1], np_area[i + 1, 2])
            b = b_line(np_area[i, 1], np_area[i, 2], k)
            area_coef = np.append(area_coef, [[xs, ys, xe, ye, k, b]], axis=0)

    # проверяем точки пересечения линий профиля
    line_peres = np.empty((0, 2))
    p = -1
    for l in range(int(len(np_lines) / 2)):
        p = p + 1
        k_l = np_lines[l + p, 5]
        b_l = np_lines[l + p, 6]
        # line_peres=np.empty((0,2))
        for j in range(int(len(area_coef))):
            k_p = area_coef[j, 4]
            b_p = area_coef[j, 5]
            xs = area_coef[j, 0]
            ys = area_coef[j, 1]
            xe = area_coef[j, 2]
            ye = area_coef[j, 3]
            x_peres = x_t_per(k_l, k_p, b_l, b_p)
            # y_peres=y_t_per(k_l, k_p, b_l, b_p)
            if round(k_l) == round(k_p) and round(abs(b_l - b_p)) < 5:
                print('Профиль №', np_lines[l + p, 4], 'совпадает с гранью')
            else:
                if xs < xe:
                    # здесь было плюс и минус 5
                    if x_peres < xe + 1 and xs - 1 < x_peres and x_peres != 10000000000:
                        line_peres = np.append(line_peres, [[x_peres, (k_l * x_peres + b_l)]], axis=0)
                elif xs > xe:
                    if x_peres < xs + 1 and xe - 1 < x_peres and x_peres != 10000000000:
                        line_peres = np.append(line_peres, [[x_peres, (k_l * x_peres + b_l)]], axis=0)

        if len(line_peres) > 0:
            np_lines[l + p, 2] = line_peres[np.argmin(line_peres[:, 0]), 0]
            np_lines[l + p, 3] = line_peres[np.argmin(line_peres[:, 0]), 1]
            np_lines[l + p + 1, 2] = line_peres[np.argmax(line_peres[:, 0]), 0]
            np_lines[l + p + 1, 3] = line_peres[np.argmax(line_peres[:, 0]), 1]
            cut_line_length = dlina(np_lines[l + p, 2], np_lines[l + p, 3], np_lines[l + p + 1, 2],
                                    np_lines[l + p + 1, 3])
            np_lines[l + p, 7] = cut_line_length
            np_lines[l + p + 1, 7] = cut_line_length
            line_peres = np.empty((0, 2))

def cutting_lines(lines_cut_, points):
    p = -1
    for i in range(int((len(lines_cut_)) / 2)):
        p = p + 1
        v = np.where(points[:, 3] == lines_cut_[i + p, 4])
        v = v[0]
        bufer = points[v, :]
        lines_cut_[i + p, 2] = bufer[np.argmin(bufer[:, 0]), 0]
        lines_cut_[i + p, 3] = bufer[np.argmin(bufer[:, 0]), 1]
        lines_cut_[i + p + 1, 2] = bufer[np.argmax(bufer[:, 0]), 0]
        lines_cut_[i + p + 1, 3] = bufer[np.argmax(bufer[:, 0]), 1]