from sheduler import const
from time import sleep
from datetime import datetime
import threading


class ClassifierParameter:
    """
    Get parameter from cron expression check, and classifier him
    """

    def __init__(self, values):
        self.value, self.dt_part = values
        self.rank = None
        self.__ranking_param()
        self.__check_parameters_for_correct_values()

    def __check_parameters_for_correct_values(self):
        start = 0
        if self.value != '':
            if self.dt_part == const.DatetimeParts.Days:
                start = 1
                limit = 32
            elif self.dt_part == const.DatetimeParts.Hours:
                limit = 23
            elif self.dt_part == const.DatetimeParts.Months:
                start = 1
                limit = 12
            elif self.dt_part == const.DatetimeParts.Years:
                limit = 9999
            else:
                limit = 60
            values = []
            if self.rank == '':
                raise ValueError(f"Incorrect parameter: value {self.value} rank {self.rank} dt_part {self.dt_part}")
            if self.rank == const.Classifiers.StartEvery:
                values = list(map(int, self.value.split('/')))
            elif self.rank == const.Classifiers.Every:
                pass
            elif self.rank == const.Classifiers.SpecificWeekdays:
                pass
            else:
                values = list(map(int, self.value.split(',')))
            for value in values:
                if value in range(start, limit):
                    pass
                else:
                    raise ValueError(f"parameter {self} have value which the out of bound")
        else:
            raise ValueError(f"parameter {self} have null value")

    def __ranking_param(self):
        rank = ''
        for validator in const.VALIDATORS:
            rank = validator(self.value)
            if rank:
                break
            else:
                continue
        if rank == '' and self.dt_part == const.DatetimeParts.Years:
            rank = const.Classifiers.Specific
        self.rank = rank

    def generate_dt_values_from_parameter(self):
        """
        Generate datetime parameters from cron expression values
        TODO now logic bases from comparison classes values, but i think have another path
        :return:
        """
        now = datetime.now().replace(microsecond=0)
        if self.rank == const.Classifiers.Specific:
            values = list(map(int, self.value.split(",")))
            yield from sorted(values)
        elif self.rank == const.Classifiers.Every:
            start, end = 0, 0
            if self.dt_part == const.DatetimeParts.Years:
                start = now.year
                end = start + 1
            elif self.dt_part == const.DatetimeParts.Months:
                start = 1
                end = 13
            elif self.dt_part == const.DatetimeParts.Days:
                start = 1
                end = const.NUM_DAYS[now.month - 1] + 1
            elif self.dt_part == const.DatetimeParts.Hours:
                start = 0
                end = 24
            elif self.dt_part == const.DatetimeParts.Minutes:
                start = 0
                end = 60
            else:
                start = 0
                end = 60
            yield from range(start, end)
        elif self.rank == const.Classifiers.StartEvery:
            start, step = map(int, self.value.split("/"))
            if self.dt_part == const.DatetimeParts.Years:
                end = start + 1
            elif self.dt_part == const.DatetimeParts.Months:
                end = 13
            elif self.dt_part == const.DatetimeParts.Days:
                end = const.NUM_DAYS[now.month - 1] + 1
            elif self.dt_part == const.DatetimeParts.Hours:
                end = 24
            elif self.dt_part == const.DatetimeParts.Minutes:
                end = 60
            else:
                end = 60
            yield from range(start, end, step)
        elif self.rank == const.Classifiers.SpecificWeekdays:
            weekdays = list(map(lambda x: const.WEEKDAYS.index(x) + 1, self.value.split(",")))
            if weekdays:
                for weekday in weekdays:
                    if now.isoweekday() == weekday:
                        yield now.day
                    else:
                        yield self.find_next_day(now, weekday)

            else:
                raise ValueError(f'Incorrect value for day in weekday {self.value} ')
        return True

    @staticmethod
    def find_next_day(now, weekday):
        remain_days = range(int(now.day), const.NUM_DAYS[now.month-1]+1)
        for day in remain_days:
            __dt = now.replace(day=day)
            if __dt.isoweekday() == weekday:
                return __dt.day

    def __repr__(self):
        return f"datetime part: {self.dt_part} rank: {self.rank} expression value: {self.value}"


class ScheduleTask(threading.Thread):
    """
    Class for chat-bot-task-sheduler object, get cron expression and job name
    """

    def __init__(self, expr: str, job_id: str, job=None, job_args=None):
        super().__init__()
        self.start_event = threading.Event()
        self.__work = threading.Event()
        self.__next_task = None
        self.expression_parameters, self.job_id = None, None
        self.wait = None
        self.job = job
        self.job_args = job_args
        self.new_schedule(expr, job_id)

    def generate_schedule_dt(self):
        """
        Generate datetime for job execution
        in 6 for in *_gen constructions, getting new datetime parameters
        :return:
        """
        now = datetime.now().replace(microsecond=0)
        year_gen, month_gen, day_gen, hour_gen, minute_gen, second_gen = self.expression_parameters

        def __next_day():
            __second_to_new_day = 86400 - ((now.hour * 60 * 60) + (now.minute * 60) + now.second)
            return datetime.fromtimestamp(now.timestamp() + __second_to_new_day), -1

        for year in year_gen.generate_dt_values_from_parameter():
            for month in month_gen.generate_dt_values_from_parameter():
                if month < now.month and year < now.year:
                    continue
                for day in day_gen.generate_dt_values_from_parameter():
                    if day < now.day and month < now.month and year < now.year:
                        continue
                    if day > const.NUM_DAYS[month - 1]:
                        continue
                    for hour in hour_gen.generate_dt_values_from_parameter():
                        for minute in minute_gen.generate_dt_values_from_parameter():
                            for second in second_gen.generate_dt_values_from_parameter():
                                dt = datetime(year, month, day, hour, minute, second)
                                if dt >= now:
                                    yield dt
                                else:
                                    continue
                else:
                    if year_gen and month_gen and day_gen and hour_gen and minute_gen and second_gen:
                        pass
                    else:
                        yield __next_day()

    def run(self):
        """
        Method for assignment for execution job
        :return: void
        """
        # self.__work = True
        self.restart()
        while self.start_event.is_set():
            if self.__work.is_set():
                for time in self.generate_schedule_dt():
                    dt = datetime.now().replace(microsecond=0)
                    if not self.__work.is_set():
                        break
                    if isinstance(time, tuple):
                        wait = time[0].timestamp() - dt.timestamp()
                        print(f'End, wait new day {wait}s')
                        sleep(wait)
                        break
                    print('next task in ', time)
                    self.__get_wait(time)
                    try:
                        if self.__work.is_set():
                            if self.job is None and self.job_args is None:
                                self.job = print
                                self.job_args = ("test",)
                            self.__run_timer()
                        continue
                    except OverflowError:
                        print('Overflow timeout, thread stopped')
                        self.stop()
                else:
                    break
            else:
                self.__work.wait()
                continue

    def __get_wait(self, time):
        dt = datetime.now().replace(microsecond=0)
        self.wait = time.timestamp() - dt.timestamp()

    def __run_timer(self):
        self.__next_task = threading.Timer(self.wait, self.job, self.job_args)
        self.__next_task.start()
        self.__next_task.join()

    def stop(self):
        print(f'STOPPED {self.job_id}')
        self.start_event.clear()
        self.__work.clear()
        self.__next_task.cancel()

    def pause(self):
        self.start_event.wait()
        self.__work.clear()
        self.__next_task.cancel()

    def restart(self):
        self.__work.set()
        self.start_event.set()
        # if self.__next_task:
        #     self.__run_timer()
        # print('restart', self.__next_task)

    def new_schedule(self, expr, job_id, restart=False):
        """add new shedule"""
        if self.__next_task is not None:
            self.pause()
        self.expression_parameters = list(reversed(self.cron_expr_parser(expr)))
        self.job_id = job_id
        print(f"new shedule for task {self.job_id} expr {expr}")
        if restart:
            sleep(0.5)
            self.restart()

    @staticmethod
    def cron_expr_parser(expression):
        """
        parser for cron expression
        get string expression, then check that all need elements is have
        and parsing
        *    *    *      *     *      *
        sec  min  hours  days  month  years
        * - every time, every second, every day, etc
        0 - specific time
        0/15 - every any time from start example every 15 minute from start 0
        MON,TUE,WED,THU,FRI,SAT,SUN - specific week days
        :param expression: str
        :return:
        """
        elems = expression.split()
        if len(elems) != 6:
            raise ValueError(f"Incorrect expression {expression}")
        return list(map(lambda values: ClassifierParameter(values), zip(elems, const.DatetimeParts)))

    def __repr__(self):
        tmp = ''
        for param in self.expression_parameters:
            tmp += f"{param} \n"
        return f"Job: {self.job_id}\nExpression parameters: \n" + tmp


class TaskManager:

    def __init__(self):
        self.tasks = {}

    def create_task(self, cron_expression: str, job_id: str, job=None, job_args=None):
        self.tasks[job_id] = ScheduleTask(cron_expression, job_id, job, job_args)

    def new_schedule_task(self, cron_expression: str, job_id: str):
        self.tasks[job_id].new_sсhedule(cron_expression, job_id, restart=True)

    def start_task(self, job_id: str):
        try:
            self.tasks[job_id].start()
        except RuntimeError:
            self.tasks[job_id].restart()

    def pause_task(self, job_id: str):
        self.tasks[job_id].pause()

    def delete_task(self, job_id: str):
        self.tasks[job_id].stop()
        del self.tasks[job_id]

    def get_task(self, job_id: str):
        try:
            return self.tasks[job_id]
        except KeyError:
            return None


# st = TaskManager()
# st.create_task('0 0 14 WED * *', 'rrsr')
# st.start_task('rrsr')
