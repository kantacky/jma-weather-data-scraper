from bs4 import BeautifulSoup
import datetime
import pandas as pd
import requests

def main(airport_code: str, prec_no: str, block_no: str, date: datetime.datetime):
    url = f'https://www.data.jma.go.jp/obd/stats/etrn/view/10min_a1.php?prec_no={prec_no}&block_no={block_no}&year={date.year}&month={date.month}&day={date.day}'

    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    table = soup.find('table', id='tablefix1')

    rows = table.find_all('tr')[3:]
    columns = [
        'timestamp',
        'precipitation',
        'temperature',
        'humidity',
        'ave_wind_speed_mps',
        'ave_wind_direction_degrees',
        'max_instantaneous_wind_speed_mps',
        'max_instantaneous_wind_direction_degrees',
        'sunshine_min'
    ]

    df = pd.DataFrame(columns=columns)

    d = {
        "北": 0,
        "北北東": 22.5,
        "北東": 45,
        "東北東": 67.5,
        "東": 90,
        "東南東": 112.5,
        "南東": 135,
        "南南東": 157.5,
        "南": 180,
        "南南西": 202.5,
        "南西": 225,
        "西南西": 247.5,
        "西": 270,
        "西北西": 292.5,
        "北西": 315,
        "北北西": 337.5,
        "静穏": None,
    }

    timestamp = date

    for i in range(len(rows)):
        tds = rows[i].find_all('td')
        values = [ td.text for td in tds ]
        timestamp += datetime.timedelta(minutes=10)
        values[0] = timestamp
        df = pd.concat([df, pd.DataFrame([values], columns=df.columns)])

    df = df.replace(d).replace('///', None)

    df.to_csv(f'./data/{airport_code}_{str(date.year).zfill(4)}{str(date.month).zfill(2)}{str(date.day).zfill(2)}.csv', index=False)

if __name__ == '__main__':
    df = pd.read_csv('./airport.csv')

    start_date = datetime.datetime(2023, 4, 3, tzinfo=datetime.timezone(datetime.timedelta(hours=9)))
    end_date = datetime.datetime(2023, 7, 16, tzinfo=datetime.timezone(datetime.timedelta(hours=9)))

    for i, airport in df.iterrows():
        date = start_date
        while date <= end_date:
            main(airport_code=str(airport['code']), prec_no=str(airport['prec_no']).zfill(2), block_no=str(airport['block_no']).zfill(4), date=date)
            print(f"{str(airport['code'])}_{str(date.year).zfill(4)}{str(date.month).zfill(2)}{str(date.day).zfill(2)}.csv")
            date += datetime.timedelta(days=1)
