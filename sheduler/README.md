#Shedule module
### General info
Getting cron expression in format "second minute hour day month years" \
Have any classes for parameters get string expression, then check that all need elements is have and parsing
- '*' - every time, every second, every day, etc
- '0' - specific time
- '0/15' - every any time from start example every 15 minute from start 0
- 'MON,TUE,WED,THU,FRI,SAT,SUN' - specific week days \

Parsing this expression, and classifiers him parameters then generate values for each parameter and yield him in iterator
### Structure
shedule.py - main script \
const.py - have all constants values \
### Uses
TaskManager - main class for manage sheduler tasks accepts several parameters \
*cron_expression: str, job_id: str, job: func, job_args: tuple* \
job function must be void \
job and job_args default have value *None* \
Init TaskManager in ur own apps \
*sm = TaskManager()* \
*sm.create_task("0 50,51,52 16,17 1 * 2021", "job_id", job, job_args)* \
Then start created task \
*sm.start_task("job_id")* \
if u need pause task use method \
*sm.pause_task("job_id")* \
if u need change shedule for task use method with *new_shedule_task* needed *job_id*
use *stop_task* for killing shedule task


