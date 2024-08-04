import copy
import csv

from system_time import SystemTime


def csv_number_for_excel(number):
    return str(number).replace('.', ',')


def get_querys(filename: str):
    querys = []
    try:
        csvfile = open(filename, 'r', newline='')
    except FileNotFoundError:
        print(f'Файл {filename} отсутствует')
    else:
        with csvfile:
            spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
            try:
                '''if spamreader.line_num == 0:
                    print('Файл пуст')
                    return []'''

                file_is_empty = True
                for row in filter(lambda row: row != [], spamreader):
                    file_is_empty = False
                    start_time, task_level, end_level = row
                    querys.append(BuidingQuery(float(start_time), int(task_level), int(end_level)))
                if file_is_empty:
                    print('Файл пуст')
                    return []
            except ValueError:
                print('Некорректные данные в файле')
                querys = []
    return querys


class DeathQuery:
    def __init__(self, query_type, query_arrival_time, query_processing_start_time, query_processing_end_time, task_level,
                 elevator_start_level, elevator_name):
        self.query_type = query_type
        self.query_arrival_time = query_arrival_time
        self.query_processing_start_time = query_processing_start_time
        self.query_processing_end_time = query_processing_end_time
        self.task_level = task_level
        self.elevator_start_level = elevator_start_level
        self.elevator_name = elevator_name

    def __iter__(self):
        query_as_list = [self.query_type, csv_number_for_excel(self.query_arrival_time),
                         csv_number_for_excel(self.query_processing_start_time),
                         csv_number_for_excel(self.query_processing_end_time), self.task_level,
                         self.elevator_start_level, self.elevator_name]
        return iter(query_as_list)


class DeathQueryList:
    def __init__(self):
        self.query_list = []

    def append(self, query: DeathQuery):
        self.query_list.append(query)

    def append_query(self, query_type, query_arrival_time, query_processing_start_time, query_processing_end_time, task_level,
                 elevator_start_level, elevator_name):
        self.append(DeathQuery(query_type, query_arrival_time, query_processing_start_time, query_processing_end_time, task_level, elevator_start_level, elevator_name))

    def saving_statistics(self, filename):
        try:
            csvfile = open(f'{filename}_statistic.csv', 'w', newline='')
        except PermissionError:
            print(f'Файл {filename}_statistic.csv занят другим процессом')
            print('Статистика выполнения запросов не сохранена')
        else:
            with csvfile:
                spamwriter = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                for query in self.query_list:
                    spamwriter.writerow(query)
                print('Статистика выполнения запросов успешно сохранена')

    def saving_statistics_folder(self, filename, folder):
        try:
            csvfile = open(f'{folder}\\{filename}_statistic.csv', 'w', newline='')
        except PermissionError:
            print(f'Файл {folder}\\{filename}_statistic.csv занят другим процессом')
            print('Статистика выполнения запросов не сохранена')
        else:
            with csvfile:
                spamwriter = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                for query in self.query_list:
                    spamwriter.writerow(query)
                print('Статистика выполнения запросов успешно сохранена')


class Query:
    def __init__(self, start_time, task_level):
        self.task_level = task_level
        self.start_time = start_time
        self.end_time = -1
        self.query_processing_start_time = -1
        self.elevator_start_level = -1
        self.elevator_name = None

    def __str__(self):
        return f'{self.task_level}'

    '''def __del__(self):
        death_query_list.append(
            DeathQuery(self.__class__, self.start_time, self.query_processing_start_time, self.end_time,
                       self.task_level, self.elevator_start_level))'''


death_query_list = DeathQueryList()


class BuidingQuery(Query):
    def __init__(self, start_time, task_level, end_level):
        super().__init__(start_time, task_level)
        self.end_level = end_level

    def __str__(self):
        return f'{SystemTime(self.start_time)} - {self.task_level}'

    def finish(self, end_time, elevator_name):
        self.elevator_name = elevator_name
        self.end_time = end_time
        end_time = copy.copy(self.end_time)
        end_level = copy.copy(self.end_level)
        return ElevatorQuery(end_time, end_level)

    def __del__(self):
        print('BuldingQuery был удален')
        death_query_list.append_query('BuidingQuery', copy.copy(self.start_time), copy.copy(self.query_processing_start_time),
                       copy.copy(self.end_time),
                       copy.copy(self.task_level), copy.copy(self.elevator_start_level), copy.copy(self.elevator_name))


class ElevatorQuery(Query):
    def __init__(self, start_time, task_level):
        super().__init__(start_time, task_level)

    def __str__(self):
        return f'{SystemTime(self.start_time)} {self.task_level}'

    def finish(self, end_time, elevator_name):
        self.elevator_name = elevator_name
        self.end_time = end_time
        return None

    def __del__(self):
        print('ElevatorQuery был удален')
        death_query_list.append_query('ElevatorQuery', copy.copy(self.start_time), copy.copy(self.query_processing_start_time),
                       copy.copy(self.end_time),
                       copy.copy(self.task_level), copy.copy(self.elevator_start_level), copy.copy(self.elevator_name))
