#Преобразователь времени для удобного вывода
class SystemTime:
    def __init__(self, time):
        self.time = time

    def __str__(self):
        second = int(self.time // 1)
        millisecond = int((self.time - second) * 1000)
        minute = second % 3600 // 60
        hours = second // 3600
        second %= 60
        return str(hours).zfill(2) + ':' + str(minute).zfill(2) + ':' + str(second).zfill(2) + '.' + str(
            millisecond).zfill(3)

