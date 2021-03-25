from enum import Enum


class DatetimeParts(Enum):
    Seconds = 1
    Minutes = 2
    Hours = 3
    Days = 4
    Months = 5
    Years = 6


class Classifiers(Enum):
    Every = 1
    StartEvery = 2
    Specific = 3
    SpecificWeekdays = 4


NUM_DAYS = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
WEEKDAYS = ["MON",
            "TUE",
            "WED",
            "THU",
            "FRI",
            "SAT",
            "SUN"]
SPECIFIC_LIMITTER = [str(n) for n in range(60)]
VALIDATORS = [
    lambda param: Classifiers.Every if '*' in param else '',
    lambda param: Classifiers.StartEvery if '/' in param else '',
    lambda param: Classifiers.Specific if all(list(spec in SPECIFIC_LIMITTER for spec in param.split(','))) else '',
    lambda param: Classifiers.SpecificWeekdays if all(list(word in WEEKDAYS for word in param.split(','))) else ''
]
