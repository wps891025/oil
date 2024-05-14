
from cgitb import reset
from importlib.metadata import files
from fastapi import FastAPI, Request, Response
import json
import datetime
import requests
app = FastAPI()


class Scrape:
    def __init__(self, request_data):
        self.start_date = self._pares_date(request_data.get('start_date'))
        self.end_date = self._pares_date(request_data.get('end_date'))

    def _pares_date(self, date_str):
        date_format = "%Y-%M-%d"
        try:

            if date_str:
                valid_date = datetime.datetime.strptime(date_str, date_format)
                date_str = date_str.replace("-", "/")
                return date_str
        except ValueError as e:
            raise Exception(e)
        return "init"

    def _prepare_data(self, data):
        result = []
        data = data.get('data', {}).get('gasoline', [])
        for i in data:
            result.append({
                'date': i.get('Date'),
                "oil": {
                    "cpc": self.get_oil_detail(i, 'A'),
                    "fpcc": self.get_oil_detail(i, 'B'),

                }
            })
        return {'result': result}

    def get_oil_detail(self, i, prefix):
        detail = [
            {"title": "92無鉛汽油", "price": i.get(f"{prefix}92")},
            {"title": "95無鉛汽油", "price": i.get(f"{prefix}95")},
            {"title": "98無鉛汽油", "price": i.get(f"{prefix}98")},
            {"title": "柴油", "price": i.get(f"{prefix}chai")},

        ]
        return detail

    def get_result(self):
        filess = {'start': self.start_date, 'end': self.end_date}
        req = requests.post(
            "https://www2.moeaea.gov.tw/oil111/Gasoline/RetailPrice/load", filess)
        result = self._prepare_data(req.json())
        return result


@app.post('/oil_history')
async def oil_history(resquest: Request):
    try:
        requests_data = await resquest.json()
        result = Scrape(requests_data).get_result()
        print(result)
        return Response(content=json.dumps(result), media_type="application/json")
    except Exception as e:
        return Response(content=json.dumps({"error_msg": str(e)}), media_type='application/json')
# if __name__ :
