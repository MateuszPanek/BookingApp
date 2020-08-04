import calendar
import copy
import datetime
from typing import Union, Dict, List, Any
from clients.models import ClientProfile
from website.models import Service
from .models import Reservation, MonthlySchedule, DailySchedule


def get_month_number(month: str) -> int:
    months = {
        'January': 1,
        'February': 2,
        'March': 3,
        'April': 4,
        'May': 5,
        'June': 6,
        'July': 7,
        'August': 8,
        'September': 9,
        'October': 10,
        'November': 11,
        'December': 12
    }
    return months[month]


def check_time_collisions(time_range: list, time_to_check: datetime.time, end_time: datetime.time) -> bool:
    bool_list = []
    for time_tuple in time_range:
        bool_list.append(time_tuple[0] <= time_to_check < time_tuple[1])
    if end_time:
        for time_tuple in time_range:
            bool_list.append(time_tuple[0] < end_time <= time_tuple[1])
    if len(bool_list) > 0:
        return True not in bool_list

    else:
        return True


def get_current_reservations(person: object, person_type: str, date_today: datetime, template: dict) -> dict:
    try:
        if person_type == 'staff':
            active_reservations = Reservation.objects.filter(user=person, date__gte=date_today)
        elif person_type == 'client':
            active_reservations = Reservation.objects.filter(client=person, date__gte=date_today)
    except Reservation.DoesNotExist:
        active_reservations = []
    finally:
        reservation_dates = [reservation.date for reservation in active_reservations]
        current_reservations = copy.deepcopy(template)
        reservations = []
        for month, days in current_reservations.items():
            for day in days:
                if datetime.date(date_today.year, get_month_number(month), day) in reservation_dates:
                    if person_type == 'staff':
                        reservations = Reservation.objects.filter(
                            user=person,
                            date=datetime.date(date_today.year, get_month_number(month), day)
                        )
                    elif person_type == 'client':
                        reservations = Reservation.objects.filter(
                            client=person,
                            date=datetime.date(date_today.year, get_month_number(month), day)
                        )
                current_reservations[month][day] = [
                    (reservation.start_time, datetime.time(
                        (reservation.start_time.hour * 60 +
                         reservation.start_time.minute +
                         reservation.service.duration) // 60,
                        (reservation.start_time.hour * 60 +
                         reservation.start_time.minute +
                         reservation.service.duration) % 60
                    )) for reservation in reservations
                ]
                reservations = []
        return current_reservations


def check_gt_time_now(time: datetime.time) -> bool:
    return time > datetime.datetime.now().time()


# def get_availability(service, person) -> List[Union[Dict[Any, dict], bool]]:
#     date_today = datetime.date.today()
#     available_days = [workday.get_name_display() for workday in person.schedule.availability_days.all()]
#     month_id = [date_today.month, (date_today.month + 1 if date_today.month + 1 <= 12 else 1)]
#     year_id = [date_today.year, (date_today.year if month_id[1] > 1 else date_today.year + 1)]
#     year_change = True if year_id[0] < year_id[1] else False
#     day_id = [date_today.day, 1]
#     months_names = [calendar.month_name[i] for i in month_id]
#     availability = {}
#     start_hour = person.schedule.start_hour
#     end_hour = person.schedule.end_hour
#     for i, month in enumerate(months_names):
#         date = datetime.date(
#             year=year_id[i],
#             month=month_id[i],
#             day=day_id[i]
#         )
#         availability[month] = {
#             day: [] for day in [day for day in range(
#                 date.day, calendar.monthrange(date.year, date.month)[1] + 1
#             ) if datetime.date(date.year, date.month, day).strftime("%A") in available_days]
#         }
#     current_reservations = get_current_reservations(person, 'staff', date_today, availability)
#     for month, days in availability.items():
#         for day in days:
#             if current_reservations[month][day]:
#                 availability[month][day] = [datetime.time(
#                     hour=i,
#                     minute=j,
#
#                 ) for i in range(
#                     start_hour.hour, end_hour.hour
#                 ) for j in range(
#                     0, 60, 15
#                 ) if start_hour <= datetime.time(i, j) <= datetime.time(
#                     hour=(end_hour.hour * 60 + end_hour.minute - service.duration) // 60,
#                     minute=(end_hour.hour * 60 + end_hour.minute - service.duration) % 60)
#                      and check_time_collisions(
#                     current_reservations[month][day],
#                     datetime.time(i, j),
#                     datetime.time(
#                         hour=(datetime.time(i, j).hour * 60 + datetime.time(i, j).minute + service.duration) // 60,
#                         minute=(datetime.time(i, j).hour * 60 + datetime.time(i, j).minute + service.duration) % 60
#                     ))
#                 ]
#
#             else:
#                 availability[month][day] = [datetime.time(
#                     hour=i,
#                     minute=j,
#
#                 ) for i in range(
#                     start_hour.hour, end_hour.hour
#                 ) for j in range(
#                     0, 60, 15
#                 ) if start_hour <= datetime.time(i, j) <= datetime.time(
#                     hour=(end_hour.hour * 60 + end_hour.minute - service.duration) // 60,
#                     minute=(end_hour.hour * 60 + end_hour.minute - service.duration) % 60)
#                 ]
#
#         try:
#             availability[calendar.month_name[month_id[0]]][date_today.day] = [
#                 value for value in availability[calendar.month_name[month_id[0]]][date_today.day] if
#                 value > datetime.datetime.now().time()
#             ]
#         except KeyError:
#             pass
#
#     return [availability, year_change]

def get_available_months(person: object, months_ids: list, years: list) -> list:
    """
    Gets available months within given criteria
    :param person: Personnel profile object
    :param months_ids: list of months ids
    :param years: list of years
    :return: list of available months as MonthlySchedule objects
    """
    years = [str(year) for year in years]
    return [month for month in MonthlySchedule.objects.filter(
        user=person, month__in=months_ids, year__in=years
    )]


def get_available_days(month: MonthlySchedule) -> list:
    """
    Gets available days in MonthlySchedule object
    :param month: MonthlySchedule object
    :return: list of available days
    """
    days = [day for day in DailySchedule.objects.filter(month=month) if datetime.date(
        int(month.year), int(month.month), day.day.day) >= datetime.datetime.now().date()]
    return days


def get_time_range(day: DailySchedule) -> list:
    """
    Checks time range for specified DailySchedule object and returns it as a list
    :param day: DailySchedule object
    :return: list of hour ranges
    """
    breaks = [day.break_start, day.break_end]
    if None in breaks:
        return [i for i in range(day.start_time.hour, day.end_time.hour + 1)]
    else:
        return [i for i in range(day.start_time.hour, day.break_start.hour + 1)] + \
               [i for i in range(day.break_end.hour, day.end_time.hour + 1)]


def check_if_time_in_range(day: DailySchedule, service: Service, hour: int, minute: int) -> bool:
    """
    Checks if given time (based on hour and minute) fits DailySchedule times
    (start ,end time and break start, end time)
    :param day: DailySchedule object to be checked
    :param service: Service object
    :param hour: int representing hour
    :param minute: int representing minute
    :return: True if time fits DailySchedule, otherwise False
    """

    day_breaks = False if None in [day.break_start, day.break_end] else True
    #MODIFICATION TO THE EQUALITY FOR BETTER TIME MANAGEMENT Previous code wasn't allowing situations in which
    # reservation start time will be the same as previous reservation end time / now it's ok but
    # et's keep this code in case issues will be encountered
    # if day_breaks:
    #     return day.start_time <= datetime.time(hour, minute) <= datetime.time(
    #         hour=(day.break_start.hour * 60 + day.break_start.minute - service.duration) // 60,
    #         minute=(day.break_start.hour * 60 + day.break_start.minute - service.duration) % 60
    #         ) or day.break_end <= datetime.time(hour, minute) <= datetime.time(
    #             hour=(day.end_time.hour * 60 + day.end_time.minute - service.duration) // 60,
    #             minute=(day.end_time.hour * 60 + day.end_time.minute - service.duration) % 60)
    #
    # else:
    #     return day.start_time <= datetime.time(hour, minute) <= datetime.time(
    #         hour=(day.end_time.hour * 60 + day.end_time.minute - service.duration) // 60,
    #         minute=(day.end_time.hour * 60 + day.end_time.minute - service.duration) % 60)
    if day_breaks:
        return day.start_time <= datetime.time(hour, minute) < datetime.time(
            hour=(day.break_start.hour * 60 + day.break_start.minute - service.duration) // 60,
            minute=(day.break_start.hour * 60 + day.break_start.minute - service.duration) % 60
            ) or day.break_end < datetime.time(hour, minute) <= datetime.time(
                hour=(day.end_time.hour * 60 + day.end_time.minute - service.duration) // 60,
                minute=(day.end_time.hour * 60 + day.end_time.minute - service.duration) % 60)

    else:
        return day.start_time <= datetime.time(hour, minute) < datetime.time(
            hour=(day.end_time.hour * 60 + day.end_time.minute - service.duration) // 60,
            minute=(day.end_time.hour * 60 + day.end_time.minute - service.duration) % 60)

def get_availability(service, person) -> List[Union[Dict[Any, dict], bool]]:
    """

    :param service:
    :param person:
    :return:
    """
    availability = {}
    availability_with_day_objects = {}
    date_today = datetime.date.today()
    months_ids = [date_today.month, date_today.month + 1 if date_today.month + 1 <= 12 else '1']
    years = [date_today.year, (date_today.year if months_ids[1] > 1 else date_today.year + 1)]
    year_change = True if years[0] < years[1] else False
    available_months = get_available_months(person, months_ids, years)

    for i, month in enumerate(available_months):
        month_days = get_available_days(month)
        availability[month.get_month_name()] = {
            day.day.day: [] for day in month_days
        }
        availability_with_day_objects[month.get_month_name()] = {
            day.day.day: [day] for day in month_days
        }
    current_reservations = get_current_reservations(person, 'staff', date_today, availability)
    for month, days in availability.items():
        for day in days:
            if current_reservations[month][day]:
                availability[month][day] = [
                    datetime.time(
                        hour=hour,
                        minute=minute
                    ) for hour in get_time_range(
                        availability_with_day_objects[month][day][0]
                    ) for minute in range(0, 60, 15)
                    if check_if_time_in_range(
                        availability_with_day_objects[month][day][0], service, hour, minute
                    ) and check_time_collisions(
                        current_reservations[month][day],
                        datetime.time(hour, minute),
                        datetime.time(
                            hour=(hour * 60 + minute + service.duration) // 60,
                            minute=(hour * 60 + minute + service.duration) % 60
                        ))
                ]

            else:
                availability[month][day] = [
                    datetime.time(hour=hour, minute=minute) for hour in get_time_range(
                        availability_with_day_objects[month][day][0]
                    ) for minute in range(0, 60, 15)
                    if check_if_time_in_range(availability_with_day_objects[month][day][0], service, hour, minute)
                ]
        try:
            if int(available_months[0].month) == date_today.month:
                availability[available_months[0].get_month_name()][date_today.day] = [
                    value for value in availability[available_months[0].get_month_name()][date_today.day] if
                    value > datetime.datetime.now().time()
                ]
        except KeyError:
            pass

    return [availability, year_change]


def check_if_available(person: int, service: int, date_time: datetime) -> bool:
    bool_list = []
    current_reservations = Reservation.objects.filter(user=person, date=date_time.date())
    service = Service.objects.get(id=service)
    duration = service.duration
    start_time = date_time.time()
    end_time = date_time.time() + datetime.timedelta(minutes=duration)
    for reservation in current_reservations:
        reservation_end_time = reservation.start_time + datetime.timedelta(minutes=duration)
        bool_list.append(
            reservation.start_time <= start_time <= reservation_end_time
            or
            reservation.start_time <= end_time <= reservation_end_time
        )
    if bool_list:
        return True not in bool_list
    else:
        return True


def check_if_any_collisions(person: int, service: int, date_time: datetime, client: int = None) -> \
        Union[bool, Dict[str, bool]]:
    current_reservations = Reservation.objects.filter(user=person, date=date_time.date())
    service = Service.objects.get(id=service)
    duration = service.duration
    start_time = date_time.time()
    end_time = (datetime.datetime.combine(
        datetime.date.today(), start_time
    ) + datetime.timedelta(minutes=duration)).time()
    time_range = [
        (reservation.start_time,
         (datetime.datetime.combine(datetime.date.today(), reservation.start_time)
          + datetime.timedelta(minutes=reservation.service.duration)).time()
         )
        for reservation in current_reservations
    ]
    no_collisions_with_current_reservations = check_time_collisions(time_range, start_time, end_time)
    no_collisions_with_client_reservations = True
    if client is not None:
        client_reservations = Reservation.objects.filter(client=client, date=date_time.date())
        time_range = [
            (reservation.start_time,
             (datetime.datetime.combine(datetime.date.today(), reservation.start_time)
              + datetime.timedelta(minutes=reservation.service.duration)).time()
             )
            for reservation in client_reservations
        ]
        no_collisions_with_client_reservations = check_time_collisions(time_range, start_time, end_time)

    if no_collisions_with_current_reservations and no_collisions_with_client_reservations:
        return True
    else:
        return {
            'current_reservations': no_collisions_with_current_reservations,
            'client_reservations': no_collisions_with_client_reservations
        }


def remove_client_reservations(availability: dict, client: object, service: object) -> dict:
    client_reservations = get_current_reservations(client, 'client', datetime.date.today(), availability)
    for month, days in availability.items():
        for day in days:
            if client_reservations[month][day]:
                availability[month][day] = [
                    time for time in availability[month][day]
                    if check_time_collisions(
                        client_reservations[month][day],
                        time,
                        datetime.time(
                            hour=(time.hour * 60 + time.minute + service.duration) // 60,
                            minute=(time.hour * 60 + time.minute + service.duration) % 60
                        )
                    )
                ]
    return availability


def remove_empty_days(availability: dict) -> dict:
    for month, days in copy.deepcopy(availability).items():
        for day, hours in days.items():
            if not hours:
                availability[month].pop(day)

    return availability


def get_reservations_for_client(service: object, person: object, client: object):
    availability = remove_empty_days(remove_client_reservations(get_availability(service, person)[0], client, service))

    return availability


def availability_time_to_string(availability):
    availability_str = copy.deepcopy(availability)
    for month, days in availability_str.items():
        for day, time_list in days.items():
            availability_str[month][day] = [time.strftime('%H:%M') for time in time_list]

    return availability_str
