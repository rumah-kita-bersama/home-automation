import crontab
import requests
import bs4
import time

PLAY_ADZAN_COMMAND = "mpg321 /home/pi/home-automation/adzan/adzan.mp3 >> /dev/null 2>&1"
PRAYER_WHITELIST = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
MUIS_PRAYER_LIST = [
    {"name": "Subuh", "hour_offset": 0},
    {"name": "Zohor", "hour_offset": 12},
    {"name": "Asar", "hour_offset": 12},
    {"name": "Maghrib", "hour_offset": 12},
    {"name": "Isyak", "hour_offset": 12},
]


def get_prayer_time() -> dict:
    response = requests.get(
        "https://api.pray.zone/v2/times/today.json", {"city": "singapore", "school": 10}
    ).json()

    if response["status"] == "OK":
        prayer_times = response["results"]["datetime"][0]["times"]
        return {
            prayer: time
            for prayer, time in prayer_times.items()
            if prayer in PRAYER_WHITELIST
        }
    return dict()


# def get_muis_prayer_time() -> dict:
#     response = requests.get("https://www.muis.gov.sg/")
#     result = {}

#     if response.status_code != 200:
#         return result

#     print(response.content)
#     soup = bs4.BeautifulSoup(response.content, features="html.parser")
#     for prayer in MUIS_PRAYER_LIST:
#         element = soup.find("span", {"id": f'PrayerTimeControl1_{prayer["name"]}'})

#         print(element)

#         if element is not None:
#             hour, minute = element.string.split(":")
#             hour = str((int(hour) + prayer["hour_offset"]) % 24)
#             result[prayer["name"]] = f"{hour}:{minute}"


#     return result
def get_muis_prayer_time() -> dict:
    response = requests.get(
        f"https://www.muis.gov.sg/api/pagecontentapi/GetPrayerTime?v={time.time() * 1000}"
    )
    result = dict()

    if response.status_code != 200:
        return result

    schedule = response.json()
    for prayer in MUIS_PRAYER_LIST:
        if prayer["name"] not in schedule:
            continue

        hour, minute = schedule[prayer["name"]].split(":")
        hour = str((int(hour) + prayer["hour_offset"]) % 24)
        result[prayer["name"]] = f"{hour}:{minute}"

    return result


def remove_cronjobs_by_command(cron: crontab.CronTab, cmd: str) -> None:
    jobs = cron.find_command(cmd)
    for job in jobs:
        cron.remove(job)


def set_adzan_cronjob(cron: crontab.CronTab) -> None:
    prayer_times = get_muis_prayer_time()

    if len(prayer_times) == 0:
        return

    for prayer, time in prayer_times.items():
        [hour, minute] = [int(c) for c in time.split(":")]

        job = cron.new(command=PLAY_ADZAN_COMMAND, comment=prayer)
        job.hour.on(hour)
        job.minute.on(minute)

        cron.write()


def main():
    cron = crontab.CronTab(user="pi")

    # Remove (possibly) outdated adzan time
    remove_cronjobs_by_command(cron, PLAY_ADZAN_COMMAND)

    set_adzan_cronjob(cron)


if __name__ == "__main__":
    main()
