import numpy as np
import math
import ltools

def s_cos(ugol, shag):
    return shag * math.cos(math.radians(ugol))


def s_sin(ugol, shag):
    return shag * math.sin(math.radians(ugol))


class ProfilesParametrs:
    def __init__(self, message, area_numpy):
        self.area = area_numpy
        self.alpha = None
        self.prostiranie_PR = ''
        self.n1 = 0
        self.n2 = 0
        self.step = None  # шаг между профилями, заданный пользователем
        self.step_cor = None  # скорректированный шаг между профилями для расчетов
        self.step2 = None  # шаг для снятия отметок рельефа
        self.n_pr = None  # предварительное количество профилей

        if message.lower() == 'да':
            self.message = 1  # расчитываем азимут профилей по заданным вершинам
        else:
            self.message = 0  # нужно запросить азимут

    def alpha_input():
        alpha = int(input('Введите азимут простирания профилей в северных румбах: '))
        if alpha > 180 and alpha < 270:
            alpha = alpha - 180
        elif alpha < 180 and alpha > 90:
            alpha = alpha + 180
        else:
            alpha = alpha
        return (alpha)

    def get_alpha(self):
        return print(f'\nАзимут простирания профилей = {round(self.alpha)}')

    def set_alpha(self):
        if self.message:
            str_ppr = str(input(
                'Введите номера одной или двух крайних точек, через которые должен пройти профиль, через запятую: '))
            str_ppr = str_ppr.replace(' ', '')  # удаляем ненужные пробелы, если есть
            if ',' in str_ppr:
                tochki_ppr = str_ppr.split(',')
                tochki_ppr = list(map(int, tochki_ppr))
                self.n1 = np.where(self.area[:, 0] == tochki_ppr[0])[0][0]
                self.n2 = np.where(self.area[:, 0] == tochki_ppr[1])[0][0]
                if self.area[self.n1, 2] > self.area[self.n2, 2]:
                    self.n1, self.n2 = self.n2, self.n1
                    alpha = math.degrees(math.atan(ltools.k_line(self.area[self.n1, 1],
                                                                 self.area[self.n1, 2],
                                                                 self.area[self.n2, 1],
                                                                 self.area[self.n2, 2])))
                    if alpha < 0:
                        self.alpha = 270 - alpha
                    elif alpha >= 0:
                        self.alpha = 90 - alpha
            else:
                tochki_ppr = int(str_ppr)
                self.n1 = np.where(self.area[:, 0] == tochki_ppr[0][0])
                print('\nПервый профиль пройдет через вершину №', str_ppr)
                self._alpha = self.alpha_input()
        else:
            self._alpha = self.alpha_input()

    def set_pr(self):
        if self.alpha >= 270:
            self.prostiranie_PR = 'NW'
        elif self.alpha <= 90:
            self.prostiranie_PR = 'NE'
        return self.prostiranie_PR

    def get_pr(self):
        if self.alpha >= 270:
            return print('\n Простирание профилей CЗ')
        elif self.alpha <= 90:
            return print('\n Простирание профилей CВ')

    def set_step(self, beta):
        value = int(input('Введите шаг между профилями в метрах: '))
        self.step = value
        self.step_cor = self.step / math.sin(math.radians(beta))
        return self.step

    def set_step2(self):
        value = int(input('Введите шаг для снятия отметок рельефа по профилю (в метрах): '))
        self.step2 = value
        return self.step2

    def set_n(self, dist):
        self.n_pr = int(dist / self.step_cor + 1)
        return self.n_pr

    # для определения стартовых точек
    def XPR_s(self, pseudoaxis_, romb_):
        if pseudoaxis_.prostiranie_axis == 'NW':
            return -s_cos(romb_.phi, self.step)
        elif pseudoaxis_.prostiranie_axis == 'NE':
            return s_cos(romb_.phi, self.step)
        else:
            return 0

    def YPR_s(self, pseudoaxis_, romb_):
        if pseudoaxis_.prostiranie_axis == 'NW':
            return -s_sin(romb_.phi, self.step)
        elif pseudoaxis_.prostiranie_axis == 'NE':
            return -s_sin(romb_.phi, self.step)

    # для определения пикетов
    def XPR_piket(self):
        if self.prostiranie_PR == 'NE':
            return s_sin(self.alpha, self.step2)
        elif self.prostiranie_PR == 'NW':
            return s_cos(self.alpha - 270, self.step2)
        else:
            print('Простирание профилей неопределено')

    def YPR_piket(self):
        if self.prostiranie_PR == 'NE':
            return s_cos(self.alpha, self.step2)
        elif self.prostiranie_PR == 'NW':
            return -s_sin(self.alpha - 270, self.step2)
        else:
            print('Простирание профилей неопределено')


class PseudoAxis:
    def __init__(self, r_points, prparam):

        self.alpha = prparam.alpha
        self.prostiranie_PR = prparam.prostiranie_PR
        # это скорее всего понадобится для субмеридиональных профилей, пока оставим i=1
        i = 1
        self.Xmax_axis = r_points[np.argmax(r_points[:, i]), 1]
        self.Xmin_axis = r_points[np.argmin(r_points[:, i]), 1]
        self.Ymax_axis = r_points[np.argmax(r_points[:, i]), 2]
        self.Ymin_axis = r_points[np.argmin(r_points[:, i]), 2]

        # делаем страховку, чтобы ось фигуры не была слишком наклонена
        self.ugol_check = math.degrees(
            math.atan(ltools.k_line(self.Xmin_axis, self.Ymin_axis, self.Xmax_axis, self.Ymax_axis)))
        if self.ugol_check > 30:
            n_bufer = np.where(r_points[:, 1] == self.Xmax_axis)
            n_bufer = int(n_bufer[0])
            dop_step = 0.1 * ltools.dlina(self.Xmin_axis, self.Ymin_axis, self.Xmax_axis, self.Ymax_axis)
            self.Xmax_axis = r_points[n_bufer, 1] + dop_step  # увеличиваем Х
            self.Ymax_axis = r_points[n_bufer, 2] - dop_step  # уменьшаем  Y
            n_bufer = np.where(r_points[:, 1] == self.Xmin_axis)
            n_bufer = int(n_bufer[0])
            self.Xmin_axis = r_points[n_bufer, 1] - dop_step  # уменьшаем   Х
            self.Ymin_axis = r_points[n_bufer, 2] + dop_step  # увеличиваем Y
            self.ugol_check = math.degrees(
                math.atan(ltools.k_line(self.Xmin_axis, self.Ymin_axis, self.Xmax_axis, self.Ymax_axis)))

        if self.Ymin_axis > self.Ymax_axis:
            self.prostiranie_axis = 'NW'
        elif self.Ymin_axis < self.Ymax_axis:
            self.prostiranie_axis = 'NE'

        self.XY_axis = np.empty((0, 2))
        self.XY_axis = np.append(self.XY_axis, [[self.Xmin_axis, self.Ymin_axis]], axis=0)
        self.XY_axis = np.append(self.XY_axis, [[self.Xmax_axis, self.Ymax_axis]], axis=0)

        # параметры оси
        self.k = ltools.k_line(self.Xmin_axis, self.Ymin_axis, self.Xmax_axis, self.Ymax_axis)
        self.b = ltools.b_line(self.Xmax_axis, self.Ymax_axis, self.k)
        # self.Ymax_axis - self.k*self.Xmax_axis
        self.X = np.linspace(self.Xmin_axis, self.Xmax_axis, num=51)
        self.Y = self.k * self.X + self.b


# наследник
class BordersToPseudoAxis(PseudoAxis):
    def __init__(self, area_points, prparam):
        PseudoAxis.__init__(self, area_points, prparam)
        # коэффициенты
        self.b_min = (self.Xmin_axis / self.k) + self.Ymin_axis
        self.b_max = (self.Xmax_axis / self.k) + self.Ymax_axis

        if self.prostiranie_axis == 'NE':
            if self.alpha <= 45:
                self.XWest_min = self.k * (self.b_min - ((area_points[np.argmax(area_points[:, 2]) - 1, 2] +
                                                          area_points[np.argmax(area_points[:, 2]), 2]) / 2))
                self.XEast_max = self.k * (self.b_max - ((area_points[np.argmin(area_points[:, 2]) - 1, 2] +
                                                          area_points[np.argmin(area_points[:, 2]), 2]) / 2))
            elif self.alpha > 45:
                self.XWest_min = self.k * (self.b_min - area_points[np.argmax(area_points[:, 2]), 2])
                self.XEast_max = self.k * (self.b_max - area_points[np.argmin(area_points[:, 2]), 2])

            self.YWest_min = -(self.XWest_min / self.k) + self.b_min
            self.YEast_max = -(self.XEast_max / self.k) + self.b_max

            self.XWest_max = self.k * (self.b_min - area_points[np.argmin(area_points[:, 2]), 2])
            self.YWest_max = -(self.XWest_max / self.k) + self.b_min

            self.XEast_min = self.k * (self.b_max - area_points[np.argmax(area_points[:, 2]), 2])
            self.YEast_min = -(self.XEast_min / self.k) + self.b_max

        if self.prostiranie_axis == 'NW':
            if self.alpha <= 45:
                self.XWest_min = self.k * (self.b_min - ((area_points[np.argmin(area_points[:, 2]) - 1, 2] +
                                                          area_points[np.argmin(area_points[:, 2]), 2]) / 2))
                self.XEast_max = self.k * (self.b_max - ((area_points[np.argmax(area_points[:, 2]) - 1, 2] +
                                                          area_points[np.argmax(area_points[:, 2]), 2]) / 2))
            elif self.alpha > 45:
                self.XWest_min = self.k * (self.b_min - area_points[np.argmin(area_points[:, 2]), 2])
                self.XEast_max = self.k * (self.b_max - area_points[np.argmax(area_points[:, 2]), 2])

            self.YWest_min = -(self.XWest_min / self.k) + self.b_min
            self.YEast_max = -(self.XEast_max / self.k) + self.b_max

            self.XWest_max = self.k * (self.b_min - area_points[np.argmax(area_points[:, 2]), 2])
            self.YWest_max = -(self.XWest_max / self.k) + self.b_min

            self.XEast_min = self.k * (self.b_max - area_points[np.argmin(area_points[:, 2]), 2])
            self.YEast_min = -(self.XEast_min / self.k) + self.b_max


# наследник
# здесь будут параметры ромба, описывающего фигуру площади
# коэффициенты даны для верхней грани ромба в соответствии с простиранием профилей

class RombParametrs(PseudoAxis):
    def __init__(self, r_points, b_class, prparam):
        PseudoAxis.__init__(self, r_points, prparam)
        if self.prostiranie_PR == 'NE':
            self.k_alpa = math.tan(math.radians(90 - self.alpha))
            # self.b_profile=b_class.YWest_min-self.k_alpa*b_class.XWest_min
        elif self.prostiranie_PR == 'NW':
            self.k_alpa = math.tan(math.radians(270 - self.alpha))  # здесь такая разность, чтобы указать нужный наклон
            # self.b_profile=r_points[np.argmax(r_points[:,2])-1,2]-self.k_alpa*r_points[np.argmax(r_points[:,2])-1,1]

        # угол для построения профилей
        self.phi = abs(math.degrees(math.atan(-1 / self.k)))
        if self.prostiranie_PR == 'NE':
            self.beta = 90 - self.phi + self.alpha  # а откуда берется этот угол - большой вопрос
        elif self.prostiranie_PR == 'NW':
            self.beta = self.phi - (self.alpha - 270)  # откуда берется этот угол - видно по рисунку

        if prparam.message:
            if prparam.n2:
                if r_points[prparam.n1, 2] >= self.Ymin_axis:
                    self.script = 1  # две вершины выше оси фигуры
                else:
                    self.script = 2  # две вершины ниже оси фигуры - нельзя начать с них разбивку
                    print(
                        'Задано, что первый профиль является самым северным. Выбранные вершины находится ниже горизонтальной оси фигуры, поэтому задание первого профиля через данные вершины невозможно (пока)')
            else:
                if r_points[prparam.n1, 2] >= self.Ymin_axis:
                    self.script = 3  # вершина выше оси фигуры
                else:
                    self.script = 4  # вершина ниже оси фигуры - нельзя начать с нее разбивку
                    print(
                        'Задано, что первый профиль является самым северным. Выбранная вершина находится ниже горизонтальной оси фигуры, поэтому задание первого профиля через данную вершину невозможно (пока)')
        else:
            self.script = 5

        if self.script == 1 or self.script == 3:
            self.b_profile = r_points[prparam.n1, 2] - self.k_alpa * r_points[prparam.n1, 1]
            self.Xs = (b_class.b_min - self.b_profile) / (self.k_alpa + 1 / self.k)
            self.Ys = self.k_alpa * self.Xs + self.b_profile
            self.Xe = (b_class.b_max - self.b_profile) / (self.k_alpa + 1 / self.k)
            self.Ye = self.k_alpa * self.Xe + self.b_profile

        elif self.script == 2 or self.script == 4 or self.script == 5:
            if self.prostiranie_axis == 'NE':
                if self.prostiranie_PR == 'NE':
                    self.b_profile = b_class.YWest_min - self.k_alpa * b_class.XWest_min
                    self.Xs = b_class.XWest_min
                    self.Ys = b_class.YWest_min
                    self.Xe = (b_class.b_max - self.b_profile) / (self.k_alpa + 1 / self.k)
                    self.Ye = self.k_alpa * self.Xe + self.b_profile
                elif self.prostiranie_PR == 'NW':
                    self.b_profile = ltools.b_line(b_class.XEast_min, b_class.YEast_min, self.k_alpa)
                    self.Xs = (b_class.b_min - self.b_profile) / (self.k_alpa + 1 / self.k)
                    self.Ys = self.k_alpa * self.Xs + self.b_profile
                    self.Xe = b_class.XEast_min
                    self.Ye = b_class.YEast_min

            elif self.prostiranie_axis == 'NW':
                if self.prostiranie_PR == 'NE':
                    self.b_profile = ltools.b_line(b_class.XWest_max, b_class.YWest_max, self.k_alpa)
                    self.Xs = (b_class.b_min - self.b_profile) / (self.k_alpa + 1 / self.k)
                    self.Ys = self.k_alpa * self.Xs + self.b_profile
                    self.Xe = (b_class.b_max - self.b_profile) / (self.k_alpa + 1 / self.k)
                    self.Ye = self.k_alpa * self.Xe + self.b_profile
                elif self.prostiranie_PR == 'NW':
                    self.b_profile = ltools.b_line(b_class.XEast_max, b_class.YEast_max, self.k_alpa)
                    self.Xs = (b_class.b_min - self.b_profile) / (self.k_alpa + 1 / self.k)
                    self.Ys = self.k_alpa * self.Xs + self.b_profile
                    self.Xe = b_class.XEast_max
                    self.Ye = b_class.YEast_max
        else:
            print('Ошибка с выбором сценария для разбивки профилей. Проверьте заданные вами вершины полигона')

        # длина "оси" площади для расчета количества профилей
        if self.prostiranie_axis == 'NE':
            if self.prostiranie_PR == 'NE':
                self.gran03 = ltools.dlina(self.Xe, self.Ye, b_class.XEast_max, b_class.YEast_max)
            elif self.prostiranie_PR == 'NW':
                self.gran03 = ltools.dlina(self.Xs, self.Ys, b_class.XWest_max, b_class.YWest_max)
        elif self.prostiranie_axis == 'NW':
            if self.prostiranie_PR == 'NE':
                self.gran03 = ltools.dlina(b_class.XEast_min, b_class.YEast_min, self.Xe, self.Ye)
            elif self.prostiranie_PR == 'NW':
                self.gran03 = ltools.dlina(self.Xs, self.Ys, b_class.XWest_min, b_class.YWest_min)

        # длина профиля
        self.gran01 = ltools.dlina(self.Xs, self.Ys, self.Xe, self.Ye)
        # координаты для построения
        self.X_pr = np.linspace(self.Xs, self.Xe, num=51)
        self.Y_pr = self.k_alpa * self.X_pr + self.b_profile


# Чтение текстового файла в последовательный кортеж (элементы записываются друг за другом)
# razdelitel - разделитель один, указан в ковычках
# удаляются символы: (,), пробел, переход на другую строку
def txt2tuple(file, razdelitel):
    # открываем файл в режиме чтения utf-8
    file = open(file, 'r', encoding='utf-8')

    # читаем все строки и удаляем переводы строк
    lines = file.readlines()
    lines = [line.rstrip('\n') for line in lines]
    lines = [line.strip('(') for line in lines]
    lines = [line.strip(')') for line in lines]
    lines = [line.replace(' ', "") for line in lines]

    tuple_ = tuple()
    for element in lines:
        tuple_ = tuple_ + (float(element),)
    file.close()

    return tuple_