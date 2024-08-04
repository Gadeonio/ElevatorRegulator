import copy
import random

from querys import death_query_list
from system_time import SystemTime


def sign(number):
    if number > 0 + 10 ** (-16):
        return 1
    elif number < 0 - 10 ** (-16):
        return -1
    elif 0 - 10 ** (-16) <= number <= 0 + 10 ** (-16):
        return 0


class Elevator:
    def __init__(self, name, overcome_floor_time, acceleration_time, deceleration_time, holding_time):
        self.name = name
        self.overcome_floor_time = overcome_floor_time
        self.acceleration_time = acceleration_time
        self.deceleration_time = deceleration_time
        self.holding_time = holding_time
        # -1 едет вниз, 1 вверх, 0 стоит на месте
        self.direction = 0
        self.query_queue = []
        self.total_time = 0.0
        self.now_level = 1

    def run(self):
        while len(self.query_queue) > 0:
            query = self.query_queue.pop(0)
            if self.total_time < query.start_time:
                self.total_time = query.start_time
            # Нужно для сбора статистики
            query.query_processing_start_time = copy.copy(self.total_time)

            print(f'Обработка запроса {query} лифтом {self.name}')
            print(f'{SystemTime(self.total_time)} Начало')

            # Нужно для сбора статистики
            query.elevator_start_level = copy.copy(self.now_level)

            if self.now_level != query.task_level:
                self.change_direction(copy.copy(query.task_level))
                self.moving(copy.copy(query.task_level))
            self.hold()
            next_query = query.finish(self.total_time, self.name)

            if next_query is not None:
                self.query_queue.append(next_query)
            print(f'Конец: {SystemTime(self.total_time)}')
            del query

            # Нужно как то поменять класс объекта
            # Нужно поделить эту функцию в этом месте
            # Необходимо рассмотреть при дополнении запроса, может ли лифт остановиться для выполнения данного запроса, если может, то написать прерыватель

    def moving(self, level):
        old_time = self.total_time
        difference = self.now_level - level

        self.total_time += self.overcome_floor_time * (
                abs(difference) - 1) + self.acceleration_time + self.deceleration_time
        print(
            f'{SystemTime(old_time)} {SystemTime(self.total_time)} Перемещение с {self.now_level} на {level}. Направление {self.direction}')
        self.now_level = level

    def hold(self):
        old_time = self.total_time
        self.total_time += self.holding_time
        print(f'{SystemTime(old_time)} {SystemTime(self.total_time)} Ожидание')

    def change_direction(self, level):
        self.direction = self.get_direction(level)

    def get_direction(self, level):
        return sign(level - self.now_level)


class LimitedQueueElevator(Elevator):
    def __init__(self, name, overcome_floor_time, acceleration_time, deceleration_time, holding_time, limit_queue_len):
        super().__init__(name, overcome_floor_time, acceleration_time, deceleration_time, holding_time)
        self.limit_queue_len = limit_queue_len

    def run(self):
        query = self.query_queue.pop(0)
        if self.total_time < query.start_time:
            self.total_time = query.start_time
        # Нужно для сбора статистики
        query.query_processing_start_time = copy.copy(self.total_time)

        print(f'Обработка запроса {query} лифтом {self.name}')
        print(f'{SystemTime(self.total_time)} Начало')

        # Нужно для сбора статистики
        query.elevator_start_level = copy.copy(self.now_level)

        if self.now_level != query.task_level:
            self.change_direction(copy.copy(query.task_level))
            self.moving(copy.copy(query.task_level))
        self.hold()
        next_query = query.finish(self.total_time, self.name)

        if next_query is not None:
            self.query_queue.append(next_query)
        print(f'Конец: {SystemTime(self.total_time)}')
        del query


class ElevatorSystem:
    def __init__(self, elevators, query_queue):
        self.elevators = elevators
        self.query_queue = query_queue

    def run(self):
        if self.query_queue == []:
            print('Запросы отсутствуют')
            return
        print('Постепенно выполняем запросы')

    def save_statistic(self):
        death_query_list.saving_statistics(self.__class__.__name__)


# Попробуем два подхода
# 1 Лифты сразу получают запросы и выполняют их
class ImmediatelyPerformingElevatorSystem(ElevatorSystem):
    def run(self):
        if self.query_queue == []:
            print('Запросы отсутствуют')
            return
        print('Постепенно выполняем запросы')
        len_query_queue = len(self.query_queue)
        len_elevators = len(self.elevators)
        avg_elevator_query_queue_number = len_query_queue // len_elevators
        mod_elevator_query_queue_number = len_query_queue % len_elevators
        elevator_queue_count = {}
        for elevator in self.elevators:
            elevator_queue_count[elevator] = elevator_queue_count.get(elevator, 0) + avg_elevator_query_queue_number
            if mod_elevator_query_queue_number > 0:
                elevator_queue_count[elevator] += 1
                mod_elevator_query_queue_number -= 1
            elevator.query_queue = self.query_queue[:elevator_queue_count[elevator]]
            for i in range(elevator_queue_count[elevator]):
                self.query_queue.pop(0)

        for elevator in self.elevators:
            elevator.run()

        self.save_statistic()


# 2 Лифты постепенно выполняют запросы и потом получают другие
# Нужно подумать как обработать остановку лифта на каком либо этаже

class GradualImplementationElevatorSystem(ElevatorSystem):
    def run(self):
        if self.query_queue == []:
            print('Запросы отсутствуют')
            return
        print('Постепенно выполняем запросы')
        while len(self.query_queue) > 0:
            query = self.query_queue.pop(0)
            elevator = self.get_elevator()
            elevator.query_queue.append(query)
            del query
            elevator.run()
            print('Лифт выполнил запрос')
        self.save_statistic()

    def get_elevator(self) -> Elevator:
        return self.elevators[0]


class MinGradualImplementationElevatorSystem(GradualImplementationElevatorSystem):
    def get_elevator(self) -> Elevator:
        min_time_elevator = self.elevators[0]
        for elevator in self.elevators[1:]:
            if elevator.total_time < min_time_elevator.total_time:
                min_time_elevator = elevator
        return min_time_elevator


class RandomGradualImplementationElevatorSystem(GradualImplementationElevatorSystem):
    def get_elevator(self) -> Elevator:
        return random.choice(self.elevators)


class CodirectionElevatorSystem(ElevatorSystem):
    def run(self):
        if self.query_queue == []:
            print('Запросы отсутствуют')
            return
        print('Постепенно выполняем запросы')
        while len(self.query_queue) > 0:
            query = self.query_queue.pop(0)
            elevator = self.get_codirectional_elevator(query.task_level)
            if elevator is None:
                elevator = self.get_elevator()
            elevator.query_queue.append(query)
            del query
            elevator.run()
            print('Лифт выполнил запрос')
        self.save_statistic()

    def get_elevator(self) -> Elevator:
        self.elevators: list
        elevators = self.elevators.copy()
        elevators = filter(lambda x: len(x.len_query_queue), elevators)
        elevators = list(sorted(elevators, key=lambda x: (len(x.len_query_queue), x.total_time)))
        return elevators[0]

    def get_codirectional_elevator(self, level):
        codirectional_elevator = None
        elevator: Elevator
        for elevator in self.elevators:
            if elevator.get_direction(level) == elevator.direction:
                codirectional_elevator = elevator
                break
        return codirectional_elevator


class GroopingElevatorSystem(ElevatorSystem):
    def run(self):
        if self.query_queue == []:
            print('Запросы отсутствуют')
            return
        print('Постепенно выполняем запросы')
        while len(self.query_queue) > 0:
            group_query = self.get_groop_query()
            elevator = self.get_elevator()
            elevator.query_queue.extend(group_query)
            del group_query
            elevator.run()
            print('Лифт выполнил запрос')
        self.save_statistic()

    def get_groop_query(self):
        groop_query = []
        query = self.query_queue.pop(0)

        groop_query.append(query)
        start_time = query.start_time
        del query
        end_time = start_time + 10
        while len(self.query_queue) > 0:
            if self.query_queue[0].start_time > end_time:
                break
            else:
                query = self.query_queue.pop(0)
                groop_query.append(query)
                del query
        return groop_query

    def get_elevator(self) -> Elevator:
        min_time_elevator = self.elevators[0]
        for elevator in self.elevators[1:]:
            if elevator.total_time < min_time_elevator.total_time:
                min_time_elevator = elevator
        return min_time_elevator


class LevelGroopingElevatorSystem(GroopingElevatorSystem):
    def get_groop_query(self):
        groop_query = []
        query = self.query_queue.pop(0)

        groop_query.append(query)
        start_time = query.start_time
        level = query.task_level
        del query
        end_time = start_time + 10
        i = 0
        while len(self.query_queue) > 0 and len(self.query_queue) > i:
            now_query = self.query_queue[i]
            if now_query.start_time > end_time:
                break
            else:
                if now_query.task_level == level:
                    query = self.query_queue.pop(0)
                    groop_query.append(query)
                    del query
                else:
                    i += 1
        return groop_query
