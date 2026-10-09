# import schedule
# import time
# from plyer import notification

# def remind(medicine_name):
#     notification.notify(
#         title="💊 Medicine Reminder",
#         message=f"Time to take {medicine_name}",
#         timeout=10
#     )

# def start_scheduler(medicine_name, medicine_time):
#     schedule.every().day.at(medicine_time).do(remind, medicine_name)

#     while True:
#         schedule.run_pending()
#         time.sleep(1)
import schedule
import time
from plyer import notification


def remind(medicine_name):
    notification.notify(
        title="💊 Medicine Reminder",
        message=f"Time to take {medicine_name}",
        timeout=10
    )


def start_scheduler(medicine_name, medicine_time):
    schedule.every().day.at(medicine_time).do(
        remind,
        medicine_name
    )

    while True:
        schedule.run_pending()
        time.sleep(1)