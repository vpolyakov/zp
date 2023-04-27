import dotenv
import pandas as pd
import requests

from config import LOGIN, PASSWORD, APP_ID, SECRET_KEY, ACCESS_TOKEN, REFRESH_TOKEN, update_token


def get_from_api_tokens_update_env(url, params):
    response = requests.get(url, params)
    response.raise_for_status()
    token_dict = response.json()
    dotenv.set_key('.env', 'ACCESS_TOKEN', token_dict['access_token'])
    dotenv.set_key('.env', 'REFRESH_TOKEN', token_dict['refresh_token'])
    update_token()


def get_access_tokens():
    """Получить токены для api"""
    payloads = {
       'login': LOGIN,
       'password': PASSWORD,
       'client_id': APP_ID,
       'client_secret': SECRET_KEY,
    }
    get_from_api_tokens_update_env(url='https://api.superjob.ru/2.0/oauth2/password/', params=payloads)


def refresh_token():
    payloads = {
        'refresh_token': REFRESH_TOKEN,
        'client_id': APP_ID,
        'client_secret': SECRET_KEY,
    }
    get_from_api_tokens_update_env(url='https://api.superjob.ru/2.0/oauth2/refresh_token/', params=payloads)


class Key:
    def __init__(self, keys, srws=None, skwc=None):
        self.keys = keys
        self.srws = srws
        self.skwc = skwc


class Sjob:
    def __init__(self, secret_key=SECRET_KEY, access_token=ACCESS_TOKEN):
        self.session = requests.Session()
        self.session.headers.update(
            {
                'X-Api-App-Id': secret_key,
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        )
        self.col_dtypes = {
            # 'job': 'string',
            'vacid': int,
            'name': 'string',
            'salary_from': int,
            'salary_to': int,
            'curr': 'string',
            'employer_id': int,
            'employer_name': 'string',
            'employer_url': 'string',
            'vacancy_url': 'string',
            'published_at': 'datetime64[ns]',
        }

    def key_param_make(self, num: int, key: Key) -> dict:
        key_param = dict()
        key_nam = f'keywords[{num}]'
        key_param[f'{key_nam}[keys]'] = key.keys
        if key.srws:
            key_param[f'{key_nam}[srws]'] = key.srws
        if key.skwc:
            key_param[f'{key_nam}[skwc]'] = key.skwc
        return key_param

    def parse_vacancies(self, keywords: list, town=146, no_agreement=1, agency=1, period=7):
        payloads = {
            'town': town,
            'no_agreemen': no_agreement,
            'agency': agency,
            'period': period,
        }
        for i in range(len(keywords)):
            key_param = self.key_param_make(i, key=keywords[i])
            payloads.update(key_param)

        res = self.session.get('https://api.superjob.ru/2.0/vacancies/', params=payloads)
        if res.status_code == 410:
            res.raise_for_status()  # TODO Необходимо обновить токен
        return res.json()

    def collect_vacancies_dict(self, *params):
        vacancies = {col: [] for col in self.col_dtypes.keys()}
        js_vacs = self.parse_vacancies(*params)
        if not js_vacs.get('total'):
            return vacancies

        for row_vac in js_vacs['objects']:
            # vacancies['job'].append(job)  # TODO Добавить по чему ищем
            vacancies['vacid'].append(row_vac['id'])
            vacancies['name'].append(row_vac['profession'])
            vacancies['salary_from'].append(row_vac['payment_from'])
            vacancies['salary_to'].append(row_vac['payment_to'])
            vacancies['curr'].append(row_vac['currency'])
            vacancies['employer_id'].append(row_vac['id_client'])
            vacancies['employer_name'].append(row_vac['firm_name'])

            vacancies['employer_url'].append(row_vac['client'].get('link'))
            vacancies['vacancy_url'].append(row_vac['link'])
            vacancies['published_at'].append(row_vac['date_published'])
        return vacancies

    def get_vacancies(self, *params):
        vacancies_dict = self.collect_vacancies_dict(*params)
        vacancy_df = pd.DataFrame(vacancies_dict)
        vacancy_df['published_at'] = pd.to_datetime(vacancy_df['published_at'], unit='s')

        return vacancy_df


if __name__ == '__main__':
    sj = Sjob()

    key_buh = Key('Бухгалтер', 1)
    key_words = [key_buh]

    r = sj.get_vacancies(key_words)
