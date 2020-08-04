import calendar
from website.models import Service
from personnel.models import PersonnelProfile
from reservations.models import Reservation, MonthlySchedule, DailySchedule
from reservations import availability_check
import datetime
import json
from .forms import ReservationDateSelection
from django.http import HttpResponse
import pandas as pd
import datetime as dt
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


def date_form_generator(request, client):
    """
    Function that helps to generate date selection form for different versions of Create Service Form
    (different version for client users and staff users)
    :param request: request.POST
    :param client: Client user object
    :return:
        date_form - context dictionary with date_form initiated and all data from previous forms
    """
    service = Service.objects.get(id=request['service'])
    usr = request['user'].split()
    person = PersonnelProfile.objects.get(user__first_name=usr[0], user__last_name=usr[1])
    availability = availability_check.get_reservations_for_client(service, person, client)
    months = [month for month in availability.keys()]
    year_now = datetime.datetime.now().year
    years = json.dumps({
        months[0]: year_now,
        months[1]: year_now if months[0] != 'December' else year_now + 1
    })
    months.insert(0, 'Select a month')
    date_form = ReservationDateSelection(availability.keys(), years, data={
        'client': client,
        'service': service,
        'user': person,
        'years': years
    })
    context = {
        'availability': json.dumps(availability_check.availability_time_to_string(availability)),
        'client': client,
        'service': service,
        'person': person,
        'date_form': date_form,
    }

    return context


def date_form_handler(request, client: object):
    """
    Checks if specified client has reservation at the same time
    :param request: request.POST
    :param client: Client user object
    :return: True if reservation is created, HttpResponseRedirect otherwise
    """
    years = json.loads(request['years'])
    date_time = datetime.datetime(
        year=years[request['month']],
        month=availability_check.get_month_number(request['month']),
        day=int(request['day']),
        hour=int(request['time'].split(':')[0]),
        minute=int(request['time'].split(':')[1])
    )
    user = PersonnelProfile.objects.get(id=int(request['user']))
    service = Service.objects.get(id=int(request['service']))
    confirmed = availability_check.check_if_any_collisions(
        int(request['user']),
        int(request['service']),
        date_time
    )

    if confirmed is False and type(confirmed) == bool:
        return HttpResponse(403, 'Sorry - you already have reservation by this time')

    elif type(confirmed) == dict:
        if False in confirmed.values():
            return HttpResponse(403, 'Sorry - you already have reservation by this time!')

    Reservation.objects.create(
        user=user,
        service=service,
        client=client,
        date=date_time.date(),
        start_time=date_time.time()
    )

    return True


def is_day_in_schedule(month: object, day: datetime.date) -> bool:
    """
    Checks if specified day exists for given MonthlySchedule object
    :param month: MonthlySchedule object
    :param day: datetime.date representing day that needs to be checked
    :return: True if day exits else False
    """
    if day in [day.day for day in DailySchedule.objects.filter(month=month)]:
        return True
    else:
        return False


def check_exsting_days_schedule(month: object) -> list:
    """
    Returns list of existing days in schedule for given MonthlySchedule object
    :param month: MonthlySchedule object
    :return: list of existing daily schedules represented as datetime.date
    """
    return [item.day for item in DailySchedule.objects.filter(month=month)]


def get_day_choices(pk: str, collision_check=False) -> list:
    """
    Checks days in MonthlySchedule object based on given pk and returns list of days
    :param pk: ID of MontlhySchedule object
    :param collision_check: True if day_choices are supposed to exclude existing days in given MonthlySchedule,
    otherwise False (default)
    :return: day_choices - list of days in he given month pk

    """
    month_object = MonthlySchedule.objects.get(id=int(pk))
    year = int(month_object.year)
    month = int(month_object.month)
    days_range = calendar.monthrange(year, month)[1] + 1
    existing_schedule_days = check_exsting_days_schedule(month_object) if collision_check is True else []
    day_choices = [
        f'{day} : {datetime.datetime(year, month, day).strftime("%A")}' for day in range(1, days_range)
        if datetime.date(year, month, day) not in existing_schedule_days
    ]
    return day_choices


def times_valid(times: list, val=pd.NaT, null: bool = True, types: list = False) -> bool:
    """
    Checks if given times from 2 elements list are valid - start time is not smaller than end time,
    if both are filled / not filled depending on null parameter
    :param times: 2 element list with start and end time for comparison
    :param val: expected empty value, pd.NaT by default
    :param null: default True - accepts situation in which both of the times are empty val,
    :param types: list of accepted time objects, if False, function will assume default as pd.Timestamp
    otherwise both times need to be filled in
    :return: bool True if times are valid, otherwise False
    """
    nat = times.count(val)
    types = [dt.time, str] if not types else types
    if nat == 1:
        return False
    if nat == 0:
        if type(times[0]) in types and type(times[1]) in types:
            bs, be = times[0], times[1]
            if bs > be:
                return False
        else:
            return False
    if nat == 2 and null is False:
        return False
    return True


def breaks_valid(times: list) -> bool:
    """
    Checks if breaks are within day start and end time
    :param times: list of time - start time, end time, break start, break end
    :return: True if breaks are valid else False
    """
    return times[0] < times[2] < times[3] < times[1]


def unique_months(user: list, years: list, months: list) -> set:
    months_list = [(user[i], years[i], months[i]) for i in range(len(years))]
    return set(months_list)


def schedule_creator(user: list, years: list, months: list, days: list,
                     start_time: list, end_time: list, break_start: list,
                     break_end: list, update: bool) -> dict:
    """
    Creates / Updates schedule objects (MonthlySchedule, DailySchedule) from given lists
    :param user: user object list
    :param years: list with years (string format)
    :param months: list with months (string format)
    :param days: list with days (str format)
    :param start_time: list with days start time : datetime.time format
    :param end_time: list with days end time : datetime.time format
    :param break_start: list with days break start time : datetime.time format or None
    :param break_end: list with days break end time : datetime.time format or None
    :param update: True for additionally checking and updating existing MonthlySchedule / Dailyschedule objects
    :return: outcome dict with outcome of the operation
    """
    outcome = {
        'existing_months': set(),
        'existing_days': set(),
        'created_months': [],
        'created_days': [],
        'error_months': set(),
        'error_days': set(),
        'updated_days': set()
    }

    cleaned_months = unique_months(user, years, months)
    for item in cleaned_months:
        try:
            date_object = datetime.date(year=int(item[1]), month=int(item[2]), day=1)
            try:
                month = MonthlySchedule.objects.get(user=item[0], year=date_object.year, month=date_object.month)
                if month not in outcome['existing_months']:
                    outcome['existing_months'].add(f'{month.__str__()} {item[0]}')
            except MonthlySchedule.DoesNotExist:
                month = MonthlySchedule.objects.create(user=item[0], year=date_object.year, month=date_object.month)
                outcome['created_months'].append(f'{month.__str__()} {item[0]}')
        except (ValueError, TypeError):
            outcome['error_months'].add(f'{item[2]}/{item[1]} {item[0]}')

    for i in range(len(years)):
        try:
            date_object = datetime.date(year=int(years[i]), month=int(months[i]), day=int(days[i]))
            month = MonthlySchedule.objects.get(user=user[i], year=date_object.year, month=date_object.month)
            try:
                day = DailySchedule.objects.get(month=month, day=date_object)
                if update is True:
                    if times_valid([start_time[i], end_time[i]], null=False) and \
                            times_valid([break_start[i], break_end[i]]):
                        break_s = break_start[i] if type(break_start[i]) not in (str, pd.NaT) else None
                        break_e = break_end[i] if type(break_end[i]) not in (str, pd.NaT) else None
                        valid_breaks = True
                        if break_s and break_e:
                            valid_breaks = breaks_valid([start_time[i], end_time[i], break_s, break_e])
                        if any([
                            day.start_time != start_time[i],
                            day.end_time != end_time[i],
                            day.break_start != break_s,
                            day.break_end != break_e
                        ]) and valid_breaks:
                            day.start_time = start_time[i]
                            day.end_time = end_time[i]
                            day.break_start = break_s
                            day.break_end = break_e
                            day.save()
                            outcome['updated_days'].add(f'{day.__str__()} {month.user.user.get_full_name()}')
                        else:
                            if day not in outcome['existing_days']:
                                outcome['existing_days'].add(f'{day.__str__()} {month.user.user.get_full_name()}')
                    else:
                        outcome['error_days'].add(f'{days[i]}/{months[i]}/{years[i]} at row {i + 2}')
                else:
                    if day not in outcome['existing_days']:
                        outcome['existing_days'].add(f'{day.__str__()} {month.user.user.get_full_name()}')

            except DailySchedule.DoesNotExist:
                try:
                    valid_time = times_valid([start_time[i], end_time[i]], null=False)
                    valid_break = times_valid([break_start[i], break_end[i]])
                    if valid_time and valid_break:
                        break_s = break_start[i] if break_start[i] is not pd.NaT else None
                        break_e = break_end[i] if break_end[i] is not pd.NaT else None
                        valid_breaks = True
                        if break_s and break_e:
                            valid_breaks = breaks_valid([start_time[i], end_time[i], break_s, break_e])
                        if valid_breaks:
                            d = DailySchedule.objects.create(month=month, day=date_object,
                                                             start_time=start_time[i], end_time=end_time[i],
                                                             break_start=break_s, break_end=break_e)
                            outcome['created_days'].append(f'{d.__str__()} {month.user.user.get_full_name()}')
                        else:
                            outcome['error_days'].add(f'{days[i]}/{months[i]}/{years[i]} at row {i + 2}')
                    else:
                        outcome['error_days'].add(f'{days[i]}/{months[i]}/{years[i]} at row {i + 2}')
                except ValidationError:
                    outcome['error_days'].add(f'{days[i]}/{months[i]}/{years[i]} at row {i + 2}')
        except (ValueError, TypeError):
            outcome['error_days'].add(f'{days[i]}/{months[i]}/{years[i]} at row {i + 2}')
        except ValidationError:
            outcome['error_days'].add(f'{days[i]}/{months[i]}/{years[i]} at row {i + 2}')
    return outcome


def user_getter(full_name: str) -> object or str:
    """
    Gets user profile if full_name is correct
    :param full_name: str representing user full name
    :return: PersonnelProfile object if operation is successful else returns input
    """

    try:
        names = [name for name in full_name.split(' ')]
        user = User.objects.get(first_name=names[0], last_name=names[1]).personnelprofile
        return user
    except (User.DoesNotExist, AttributeError):
        return str(full_name)


def convert_time(time: str or pd.datetime) -> pd.Timedelta or str:
    """
    Converts input string with time to pd.Timedelta
    :param time: time represented as string
    :return: dt.datetime object if operation was succesful, else input as a string
    """
    try:
        if type(time) is dt.datetime:
            return time.time()
        elif type(pd.Timestamp):
            return time.time()
        elif len(time) == 5:
            return dt.datetime.strptime(time, '%H%:M').time()
        else:
            return dt.datetime.strptime(time.split(' ')[1], '%H:%M:%S').time()
    except (TypeError, AttributeError, ValueError):
        return str(time)


def schedule_import_handler(file: object, user: object or None, update, user_column=False):
    from xlrd import XLRDError
    try:
        data_opened = pd.read_excel(file)
        df = pd.DataFrame(data_opened)
        years = [x for x in df['Year']]
        months = [x for x in df['Month']]
        days = [x for x in df['Day']]
        start_time = [convert_time(x) if type(x) is not pd.NaT else x for x in df['Start_time']]
        end_time = [convert_time(x) if type(x) is not pd.NaT else x for x in df['End_time']]
        break_start = [convert_time(x) if type(x) is not pd.NaT else x for x in df['Break_start']]
        break_end = [convert_time(x) if type(x) is not pd.NaT else x for x in df['Break_end']]
        if user_column is False:
            user = [user for i in range(len(years))]
        else:
            user = [user_getter(user) for user in df['User']]
        if any([type(usr) for usr in user]) is str:
            outcome = {'user_error': [f'Wrong user in row{i} : {user}' for
                                      i, usr in enumerate(user, 2) if type(user) is str]}
            return outcome
        outcome = schedule_creator(user, years, months, days, start_time, end_time, break_start, break_end, update)

    except KeyError as e:
        outcome = {'errors': [str(e)]}
    except XLRDError:
        outcome = {'errors': ['Please import a valid file']}
    return outcome
