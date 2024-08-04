import copy

from elevator import Elevator, MinGradualImplementationElevatorSystem, RandomGradualImplementationElevatorSystem, \
    GradualImplementationElevatorSystem, GroopingElevatorSystem, LevelGroopingElevatorSystem
from querys import get_querys, death_query_list

if __name__ == '__main__':
    # query_queue = get_querys('easy_querys.csv')
    # query_queue = get_querys('hard_querys.csv')
    filename = 'querys'
    query_queue = get_querys(f'{filename}.csv')

    elevator_1 = Elevator('Вася', 1.25, 1.25, 1.25, 7)
    elevator_2 = Elevator('Асия', 1.25, 1.25, 1.25, 7)

    gies = MinGradualImplementationElevatorSystem([copy.copy(elevator_1), copy.copy(elevator_2)], query_queue)
    # gies = RandomGradualImplementationElevatorSystem([copy.copy(elevator_1), copy.copy(elevator_2)], query_queue)
    # gies = GroopingElevatorSystem([copy.copy(elevator_1), copy.copy(elevator_2)], query_queue)
    # gies = LevelGroopingElevatorSystem([copy.copy(elevator_1), copy.copy(elevator_2)], query_queue)
    gies.run()
