import re
import datetime


def test_search_with_start_date(client, auth):
    auth.login()
    res = client.get('/szukaj?start_date=2019-05-05').data.decode('utf-8')
    date = get_date(0, res)
    assert date >= datetime.datetime(2019, 5, 5)


def test_search_with_start_and_end_date(client, auth):
    auth.login()
    res = client.get('/szukaj?start_date=2019-04-05&end_date=2019-05-20')\
        .data.decode('utf-8')
    start_date = get_date(0, res)
    assert start_date >= datetime.datetime(2019, 4, 5)

    end_date = get_date(-1, res)
    assert end_date <= datetime.datetime(2019,5,20)


def test_search_with_doctor_name(client, auth):
    auth.login()




def get_date(index, res):
    date = re.findall(r"^.*\d\d:.*$", res, re.MULTILINE)[index].strip()[4:-5]
    date = datetime.datetime(int(date[12:16]), int(date[9:11]), int(date[6:8]))
    return date