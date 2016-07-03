usage: bookit.py [-h] [--retry attempts] facility date time

Helper for facility booking at Queens condo.

positional arguments:
  facility          The facility to book, one of: ['badminton', 'bbq1',
                    'bbq2', 'bbq3', 'bbq4', 'bbq5', 'bbq6', 'bbq7', 'bbq8',
                    'bbq9', 'function_room', 'golf_driving', 'golf_putting',
                    'tennis1', 'tennis2']
  date              The date to book, of the form: YYYY-MM-DD
  time              The time to book, of the form: HHMM

optional arguments:
  -h, --help        show this help message and exit
  --retry attempts  Retry this many times to make the booking (1-99)
