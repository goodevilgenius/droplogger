#!/usr/bin/env python

import datetime
import dateutil
import dateutil.parser as dp
from .misc import is_string

def parse_date(date):
    r = None
    oneday = datetime.timedelta(days=1)
    switch = {
        "min": datetime.datetime.min + oneday,
        "max": datetime.datetime.max - oneday,
        "now": datetime.datetime.now(),
        "today": datetime.datetime.combine(datetime.date.today(),datetime.time.min.replace(tzinfo=dateutil.tz.tzlocal())),
        }
    switch["tomorrow"] = switch["today"] + oneday
    switch["yesterday"] = switch["today"] - oneday

    if date.lower() in switch: r = switch[date.lower()]
    elif date[0] == "@": r = datetime.datetime.fromtimestamp((float)(date[1:]), dateutil.tz.tzlocal())
    else:
        r = dp.parse(date)

    if r.tzinfo is None:
        r = r.replace(tzinfo = dateutil.tz.tzlocal())
    return r

def format_date(dt):
    d = ""
    if is_string(dt):
        dt = parse_date(dt)
    if dt.year < 1900:
        d2 = dt.replace(year=1900)
        d = d2.strftime('%B %d, %Y at %I:%M:%S%p %z').replace('1900', '%04d' % dt.year)
    else: d = dt.strftime('%B %d, %Y at %I:%M:%S%p %z')
    return d
