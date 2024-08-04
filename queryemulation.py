import csv
import math
import random


class Button:
    def __init__(self, sign):
        self.sign = sign

    def __eq__(self, sign):
        return self.sign == sign


class ButtonFactory:
    def get_buttons(self):
        return [Button('Unsigned')]


class DirectionButtonFactory(ButtonFactory):
    def get_buttons(self):
        return [Button('down'), Button('up')]


class NumberFloorButtonFactory(ButtonFactory):
    def __init__(self, number_of_floors: int):
        self.number_of_floors = number_of_floors

    def get_buttons(self):
        return [Button(f'{number}') for number in range(1, self.number_of_floors + 1)]


class SetFloorButtonFactory(ButtonFactory):
    def __init__(self, floors: list):
        self.name_floors = [floor.name for floor in floors]

    def get_buttons(self):
        return self.name_floors


class Floor:
    def __init__(self, name: str, buttons: list, level: int):
        self.name = name
        self.buttons = buttons
        self.level = level


class ResidentialBuildingFloor(Floor):
    def __init__(self, name: str, buttons: list, level: int, percentage_arrival: float, percentage_population: float):
        super().__init__(name, buttons, level)
        # по хорошему эти переменные должны быть названы долями, но поскольку данные значения назывались так в статье, то для меньшей путаницы менять название не стал

        self.percentage_arrival = percentage_arrival
        self.percentage_population = percentage_population


class Elevator:
    def __init__(self, lifting_capacity: int, floor_overcome_time: int, waiting_time: int, door_closing_time: int,
                 door_opening_time: int, buttons: list):
        # lifting_capacity показывает сколько киллограммов может поднимать лифт
        self.buttons = buttons
        self.lifting_capacity = lifting_capacity
        self.floor_overcome_time = floor_overcome_time
        self.waiting_time = waiting_time
        # Эти два параметра думаю не использовать (например записать сюда 0) для упрощения работы программы
        self.door_closing_time = door_closing_time
        self.door_opening_time = door_opening_time


class ElevatorSystem:
    def __init__(self, elevators: list):
        self.elevators = elevators
        self.request_queue = []

    # Добавить функцию которая будет


class Building:
    def __init__(self, number_of_floors: int, type_button_factory: type, elevator_system):
        # ввести защиту на неправильный ввод данных
        self.number_of_floors = number_of_floors

        self.floors = self.get_floors()

        self.type_button_factory = type_button_factory
        if self.type_button_factory == ButtonFactory or self.type_button_factory == DirectionButtonFactory:
            self.button_factory = self.type_button_factory()
        elif self.type_button_factory == SetFloorButtonFactory:
            self.button_factory = self.type_button_factory(self.floors)
        else:
            raise 'Задан неправильный тип кнопок'
        self.__adding_buttons_for_floors()
        self.elevator_system = elevator_system

    # Нужно сделать ввод и вывод из файла характеристик о здании
    def get_floors(self):
        floors = []
        for i in range(self.number_of_floors):
            floors.append(Floor(f'{i}', [], i))
        return floors

    def __adding_buttons_for_floors(self):
        self.button_factory: ButtonFactory
        for floor in self.floors:
            floor.buttons = self.button_factory.get_buttons()

    def get_floor_by_name(self, name) -> Floor:
        for floor in self.floors:
            if floor.name == name:
                return floor


class ResidentialBuilding(Building):
    def get_floors(self):
        floors = []
        for i in range(1, self.number_of_floors + 1):
            floors.append(ResidentialBuildingFloor(name=f'{i}', buttons=[], level=i, percentage_arrival=0,
                                                   percentage_population=1 / self.number_of_floors))
        floors[0].percentage_arrival = 1
        return floors


# Если нет заранее заготовленных запросов, то используется генератор запросов
class PoissonProcess:
    # period_of_time - период времени на которою рассматриваем симуляцию
    # 86400 - сутки в секундах
    # Рассматривается неоднородный пуассоновский процесс

    def __init__(self, intensity: float, period_of_time):
        # period_of_time - период времени на которою рассматриваем симуляцию
        # 86400 - сутки в секундах
        self.period_of_time = period_of_time

        # Количество человек проходящих в период времени
        self.intensity = intensity

        self.query_time_queue = []
        # Выключена поскольку это len(self.query_time_queue)
        # self.events_amount = 0
        self.now_time = 0.0

        self.set_query_time_queue()

    def set_query_time_queue(self):
        while self.now_time < self.period_of_time:
            u = random.random()
            time = math.log(u) / self.intensity
            self.now_time = self.now_time - time
            self.add_time()
        self.query_time_queue.pop(-1)
        # self.events_amount -= 1

    def add_time(self):
        pass


class HomogeneousPoissonProcess(PoissonProcess):
    def add_time(self):
        self.query_time_queue.append(self.now_time)
        # self.events_amount += 1


def hours_to_sec(hours):
    return hours * 60 * 60


class InhomogeneousPoissonProcess(PoissonProcess):
    def time_dependent_intensity(self):
        now_time_format_day = self.now_time % hours_to_sec(24)
        match now_time_format_day:
            case now_time_format_day \
                if 0 <= now_time_format_day < hours_to_sec(3):
                return 0.05 * self.intensity
            case now_time_format_day \
                if hours_to_sec(3) <= now_time_format_day < hours_to_sec(4):
                return 0.02 * self.intensity
            case now_time_format_day \
                if hours_to_sec(4) <= now_time_format_day < hours_to_sec(6):
                return 0.05 * self.intensity
            case now_time_format_day \
                if hours_to_sec(6) <= now_time_format_day < hours_to_sec(7):
                return 0.5 * self.intensity
            case now_time_format_day \
                if hours_to_sec(7) <= now_time_format_day < hours_to_sec(9):
                return 1 * self.intensity
            case now_time_format_day \
                if hours_to_sec(9) <= now_time_format_day < hours_to_sec(14):
                return 0.1 * self.intensity
            case now_time_format_day \
                if hours_to_sec(14) <= now_time_format_day < hours_to_sec(17):
                return 0.3 * self.intensity
            case now_time_format_day \
                if hours_to_sec(17) <= now_time_format_day < hours_to_sec(20):
                return 0.7 * self.intensity
            case now_time_format_day \
                if hours_to_sec(20) <= now_time_format_day < hours_to_sec(24):
                return 0.2 * self.intensity
            case _:
                print('Ошибка во времени')

    def add_time(self):
        u = random.random()
        if u <= self.time_dependent_intensity() / self.intensity:
            self.query_time_queue.append(self.now_time)
            # self.events_amount += 1


class MyPoissonProcess(InhomogeneousPoissonProcess):
    def __init__(self, intensity: float, start_time, period_of_time):
        self.now_time = start_time
        self.period_of_time = period_of_time + start_time
        self.intensity = intensity
        self.query_time_queue = []

        self.set_query_time_queue()


class Query:
    def __init__(self, query_time: int):
        self.query_time = query_time


class BuildingQuery(Query):
    def __init__(self, query_time: int, location: Floor, signal_source: Button):
        super().__init__(query_time)
        self.location = location
        self.signal_source = signal_source


class ElevatorQuery(Query):
    def __init__(self, query_time: int, location: Elevator | None, signal_source: Button):
        super().__init__(query_time)
        self.location = location
        self.signal_source = signal_source


class SaveQuery:
    def __init__(self, start_time, task_level, end_level):
        self.start_time = start_time
        self.task_level = task_level
        self.end_level = end_level


# Специальный класс, хранящий в себе пару запросов BuildingQuery и ElevatorQuery.

class QueryCouple:
    def __init__(self, building_query, elevator_query):
        self.building_query = building_query
        self.elevator_query = elevator_query


class Emulation:
    def __init__(self, period_of_time: int, number_of_people_per_day: int, building: Building):
        self.period_of_time = period_of_time
        self.number_of_people_per_day = number_of_people_per_day
        self.intensity = self.number_of_people_per_day / self.period_of_time
        self.poisson_process = PoissonProcess(self.intensity, period_of_time)

        # Подумать по поводу задания типов этажам
        self.building = building


class ResidentialEmulation(Emulation):
    def __init__(self, start_time, period_of_time, number_of_people_per_day: int, intensity, building=None):
        self.start_time = start_time
        self.period_of_time = period_of_time
        self.number_of_people_per_day = number_of_people_per_day
        self.intensity = intensity
        self.poisson_process = HomogeneousPoissonProcess(self.intensity, period_of_time)
        # Нужно подумать как вводить ElevatorSystem, скорее всего также как и ButtonFactory
        self.building = ResidentialBuilding(20, ButtonFactory, ElevatorSystem)

        # Задаем OD матрицу (прихода и ухода)
        self.incoming = 0.80
        self.outgoing = 0.18
        self.inter_floor = 0.02
        self.inter_entrance = 0

        self.floor_parameters = self.get_floor_parameters()
        self.OD_matrix = dict()
        self.set_OD_matrix()

        # Создаем запросы BuildingQuery основываясь на времени запросов poisson_process и матрице OD

        # Должен ли быть связан BuldingQuery с ElevatorQuery
        # Если нет, тогда берем любой этаж, и потом по матрице OD и случайному значению выбираем точку отправления
        # Если да, генерируем случайную переменную, затем выбираем откуда-куда по матрице OD
        # Есть проблема того, что я думал генерировать ElevatorQuery после выполнения определенного BuildingQuery
        # Есть решение, будем генерировать ПАРУ ElevatorQuery и BuildingQuery

        self.querys = self.get_querys()
        self.save_querys_in_cvs_file()

    def create_OD_matrix(self):
        floor_names = self.floor_parameters.keys()
        for i in floor_names:
            self.OD_matrix[i] = self.OD_matrix.get(i, {})
            for j in floor_names:
                self.OD_matrix[i][j] = self.OD_matrix[i].get(j, 0.0)

    def set_OD_matrix(self):
        self.create_OD_matrix()
        sum_incoming = 0.0
        sum_outgoing = 0.0
        sum_inter_floor = 0.0
        sum_inter_entrance = 0.0

        for i in self.OD_matrix:
            for j in self.OD_matrix[i]:
                if i == j: continue
                if self.floor_parameters[i]['percentage_arrival'] != 0 and self.floor_parameters[j][
                    'percentage_arrival'] != 0:
                    self.OD_matrix[i][j] = self.floor_parameters[i]['percentage_arrival'] * self.floor_parameters[j][
                        'percentage_arrival']
                    sum_inter_entrance += self.OD_matrix[i][j]
                elif self.floor_parameters[i]['percentage_arrival'] != 0 and self.floor_parameters[j][
                    'percentage_arrival'] == 0:
                    self.OD_matrix[i][j] = self.floor_parameters[i]['percentage_arrival'] * self.floor_parameters[j][
                        'percentage_population']
                    sum_incoming += self.OD_matrix[i][j]
                elif self.floor_parameters[i]['percentage_arrival'] == 0 and self.floor_parameters[j][
                    'percentage_arrival'] != 0:
                    self.OD_matrix[i][j] = self.floor_parameters[i]['percentage_population'] * self.floor_parameters[j][
                        'percentage_arrival']
                    sum_outgoing += self.OD_matrix[i][j]
                else:
                    self.OD_matrix[i][j] = self.floor_parameters[i]['percentage_population'] * self.floor_parameters[j][
                        'percentage_population']
                    sum_inter_floor += self.OD_matrix[i][j]

        for i in self.OD_matrix:
            for j in self.OD_matrix[i]:
                if i == j: continue
                if self.floor_parameters[i]['percentage_arrival'] != 0 and self.floor_parameters[j][
                    'percentage_arrival'] != 0:
                    self.OD_matrix[i][j] = self.OD_matrix[i][j] / sum_inter_entrance * self.inter_entrance
                elif self.floor_parameters[i]['percentage_arrival'] != 0 and self.floor_parameters[j][
                    'percentage_arrival'] == 0:
                    self.OD_matrix[i][j] = self.OD_matrix[i][j] / sum_incoming * self.incoming
                elif self.floor_parameters[i]['percentage_arrival'] == 0 and self.floor_parameters[j][
                    'percentage_arrival'] != 0:
                    self.OD_matrix[i][j] = self.OD_matrix[i][j] / sum_outgoing * self.outgoing
                else:
                    self.OD_matrix[i][j] = self.OD_matrix[i][j] / sum_inter_floor * self.inter_floor
        sum_row = 0.0
        # Возможно нужно отредактировать плавающею точку
        for i in self.OD_matrix:
            for j in self.OD_matrix[i]:
                self.OD_matrix[i][j] = self.OD_matrix[i][j] + sum_row
                sum_row = self.OD_matrix[i][j]

    def get_floor_parameters(self):
        floor: ResidentialBuildingFloor
        return {
            floor.name: {
                'percentage_arrival': floor.percentage_arrival,
                'percentage_population': floor.percentage_population
            }
            for floor in self.building.floors
        }

    def get_couple_matrix_OD(self, random_number: float):
        fault = 1e-13
        necessary_i = ''
        necessary_j = list(self.OD_matrix.keys())[0]
        for i in self.OD_matrix.__reversed__():
            if self.OD_matrix[i][list(self.OD_matrix.keys())[0]] <= random_number + fault:
                necessary_i = i
                break
        for j in self.OD_matrix[necessary_i]:
            if self.OD_matrix[necessary_i][j] >= random_number + fault:
                necessary_j = j
                break
        if necessary_j == '':
            print('lol')
        return necessary_i, necessary_j

    def get_querys(self):
        querys = []
        for query_time in self.poisson_process.query_time_queue:
            u = random.random()
            necessary_i, necessary_j = self.get_couple_matrix_OD(u)
            querys.append(SaveQuery(round(query_time, 4), necessary_i, necessary_j))
        return querys

    def old_save_querys_in_cvs_file(self):
        with open('querys.csv', 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=';',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for query in self.querys:
                spamwriter.writerow([round(query.start_time, 3), query.task_level, query.end_level])
            print('Запросы успешно сохранены')

    def save_querys_in_cvs_file(self):
        try:
            csvfile = open('querys.csv', 'w', newline='')
        except PermissionError:
            print('Файл querys.csv занят другим процессом')
            print('Запросы не сохранены')
        else:
            with csvfile:
                spamwriter = csv.writer(csvfile, delimiter=';',
                                        quotechar='|', quoting=csv.QUOTE_MINIMAL)
                for query in self.querys:
                    spamwriter.writerow([round(query.start_time, 3), query.task_level, query.end_level])
                print('Запросы успешно сохранены')


if __name__ == '__main__':
    # эти характеристики рассчитаны на день
    number_of_people_per_day = 2000
    day_time = 64840
    # Возьмем час
    start_time = 25200
    period_time = 3600

    # intensity = number_of_people_per_day / day_time
    intensity = 0.05
    # simulation = ResidentialEmulation(start_time=start_time, period_of_time=period_time, number_of_people_per_day=number_of_people_per_day, intensity = intensity)
    simulation = ResidentialEmulation(start_time=start_time, period_of_time=period_time,
                                      number_of_people_per_day=number_of_people_per_day, intensity=intensity)

    # Вывод матрицы
    '''for i in simulation.OD_matrix:
        print(simulation.OD_matrix[i])'''

    '''a = Building(5, ButtonFactory)
    b = Building(5, SetFloorButtonFactory)
    print('gog')'''
    '''number_of_people_per_day = 500
    period_time = 64840
    intensity = number_of_people_per_day / period_time
    a = HomogeneousPoissonProcess(intensity, period_time)
    b = InhomogeneousPoissonProcess(intensity, period_time)'''

    # print('')
