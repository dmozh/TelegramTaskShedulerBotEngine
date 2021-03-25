from sheduler import shedule
import redis, requests
import json
from settings import BASE_URL, API_TOKEN, REDIS_DB, REDIS_PORT, REDIS_HOST

task_manager = shedule.TaskManager()

print('MAIN')
print(f"REDIS_HOST: {REDIS_HOST}\n"
      f"REDIS_PORT: {REDIS_PORT}\n"
      f"REDIS_DB:   {REDIS_DB}\n")
URL = BASE_URL + API_TOKEN
print(URL)
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
print(redis_client)
pubsub_client = redis_client.pubsub()
print(pubsub_client)


def send_msg(chat_id, msg):
    url = f"{URL}/sendMessage"
    params = {'chat_id': chat_id, 'text': msg,
              'reply_markup': {
                  'inline_keyboard': [
                      [{'text': 'test', "callback_data": 'test'}]
                  ]
              }}
    requests.post(url, json=params)


def delete_handler(message):
    data = json.loads(message['data'].decode())
    job_id = data['job_id']
    task_manager.delete_task(job_id)
    redis_client.delete(job_id)
    print("delete_handler", data)


def add_handler(message):
    data = json.loads(message['data'].decode())
    print(data)
    task_manager.create_task(data['cronexpr'],
                             data['job_id'],
                             send_msg,
                             (data['chat_id'], data['notify']))
    redis_client.mset({data['job_id']: json.dumps(data)})
    if data['work'] == 1:
        task_manager.start_task(data['job_id'])
    print("add_handler", data)


def change_handler(message):
    data = json.loads(message['data'].decode())
    job_id = data['job_id'] if 'job_id' in data else None
    if job_id is None:
        pass
    else:
        work = data['work'] if 'work' in data else None
        cronexpr = data['cronexpr'] if 'cronexpr' in data else None
        notify_msg = data['notify'] if 'notify' in data else None
        chat_id = data['chat_id'] if 'chat_id' in data else None

        _task = task_manager.get_task(job_id)
        if _task:
            if work is None:
                pass
            else:
                if work == 0:
                    task_manager.pause_task(job_id)
                elif work == 1:
                    task_manager.start_task(job_id)
                else:
                    pass
            if cronexpr is None:
                pass
            else:
                task_manager.new_schedule_task(cron_expression=cronexpr, job_id=job_id)
            if chat_id and notify_msg:
                _task.job_args = (chat_id, notify_msg)
            else:
                pass
            _change_task = json.loads(redis_client.get(job_id).decode())
            _change_task['chat_id'] = chat_id if chat_id is not None else _change_task['chat_id']
            _change_task['notify'] = notify_msg if notify_msg is not None else _change_task['notify']
            _change_task['cronexpr'] = cronexpr if cronexpr is not None else _change_task['cronexpr']
            _change_task['work'] = work if work is not None else _change_task['work']
            redis_client.mset({job_id: json.dumps(_change_task)})
        else:
            print(f"Haven't job with job id: {job_id}")
            pass
    print('change_handler', data)


for key in redis_client.keys():
    task = json.loads(redis_client.get(key.decode()))
    print(task)
    task_manager.create_task(task['cronexpr'], task['job_id'], send_msg, (task['chat_id'], task['notify']))
    redis_client.delete(key)
    if task['work'] == 1:
        task_manager.start_task(task['job_id'])
    else:
        continue

pubsub_client.subscribe(**{'add-channel': add_handler,
                           'delete-channel': delete_handler,
                           'change-channel': change_handler}
                        )

for i in pubsub_client.listen():
    print(i)
