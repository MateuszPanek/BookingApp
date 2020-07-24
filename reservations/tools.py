from website.models import Service
from personnel.models import PersonnelProfile
from reservations.models import Reservation
from reservations import availability_check
import datetime
import json
from .forms import ReservationDateSelection
from django.http import HttpResponse


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

