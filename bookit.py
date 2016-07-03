#!/usr/bin/env python3
import argparse
import getpass
import re
import sys

from lxml import html
import requests


class BookingControl:
    def __init__(self):
        self.session = requests.Session()

    def login(self, username=None, password=None):
        if not username:
            username = input('Username: ')

        if not password:
            password = getpass.getpass(stream=sys.stderr)

        url = 'http://booking.queenscondo.com.sg/login.php'
        data = {'datadmin_username': username, 'datadmin_password': password}
        response = self.session.post(url, data=data)
        response.raise_for_status()

    def personal_info(self):
        url = 'http://booking.queenscondo.com.sg/admin_my_details.php?selected_box=personal'
        response = self.session.get(url)
        response.raise_for_status()
        page = html.fromstring(response.text, base_url=response.url)
        values = page.forms[0].form_values()
        return dict(values)

    def list_facility(self, facility_number):
        url = 'http://booking.queenscondo.com.sg/admin_booking.php'
        args = {'selected_box': 'personal', 'nFac': facility_number}
        response = self.session.get(url, params=args)
        response.raise_for_status()
        page = html.fromstring(response.text, base_url=response.url)
        page.make_links_absolute(page.base_url)
        links = page.find('.//div[@class="content-primary"]').find('ul').iterlinks()
        return links

    def make_booking(self, link):
        response = self.session.get(link)
        response.raise_for_status()
        page = html.fromstring(response.text, base_url=response.url)
        page.make_links_absolute(page.base_url)
        form = page.forms[0]
        form.inputs['reader'].value = form.inputs['reader'].attrib['value']
        data = form.form_values()
        result = self.session.post(form.action, data=data)
        result.raise_for_status()
        return 'SUCCESS' in result.text

    date_re = re.compile(r'dDate=(\d\d\d\d-\d\d-\d\d)')
    time_re = re.compile(r'cDesc=(\d\d\d\d)-(\d\d\d\d)')

    def book(self, facility_number, date, hour):
        links = self.list_facility(facility_number)
        for el, attr, link, pos in links:
            date_m = self.date_re.search(link)
            time_m = self.time_re.search(link)
            if date_m and date_m.group(1) == date:
                if time_m and time_m.group(1) == hour:
                    return self.make_booking(link)
                elif 'cancel=true' in link and el.text.startswith(hour):
                    raise RuntimeError('Facility {} on {} at {} already booked'.format(facility_number, date, hour))

        else:
            raise ValueError('Facility {} on {} at {} not available for booking'.format(facility_number, date, hour))


FACILITIES = {
    'bbq1': 1,
    'bbq2': 2,
    'bbq3': 3,
    'bbq4': 4,
    'bbq5': 5,
    'bbq6': 6,
    'bbq7': 7,
    'bbq8': 8,
    'bbq9': 9,
    'function_room': 10,
    'tennis1': 11,
    'tennis2': 12,
    'badminton': 13,
    'golf_driving': 14,
    'golf_putting': 15,
}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Helper for facility booking at Queens condo.')
    parser.add_argument('facility', choices=FACILITIES.keys(),
                        help='The facility to book, one of: {}'.format(sorted(FACILITIES.keys())),
                        metavar='facility')
    parser.add_argument('date', help='The date to book, of the form: YYYY-MM-DD')
    parser.add_argument('time', help='The time to book, of the form: HHMM')
    parser.add_argument('--retry', choices=range(1, 100), 
                        help='Retry this many times to make the booking (1-99)', 
                        metavar='attempts')

    args = parser.parse_args()

    control = BookingControl()
    control.login()

    bookit = lambda: control.book(FACILITIES[args.facility], args.date, args.time)

    result = False
    if args.retry:
        attempts = args.retry
        while attempts:
            print('.', end='')
            sys.stdout.flush()

            try:
                result = bookit()
            except ValueError:
                result = False

            if result:
                attempts = 0
            else:
                attempts -= 1

        print('')

    result = bookit()

    print('Booked!' if result else 'Failed to book :(')
