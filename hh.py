import pandas as pd
import requests

HH_URL = 'https://api.hh.ru/'


class HH:
    """
    Получить вакансии с сайта zp
    """
    def __init__(
            self,
            search_period=30,
            per_page=100,
            search_field='name',
            area=79,  # Саратов
    ):

        self.search_period = search_period
        self.per_page = per_page
        self.search_field = search_field
        self.area = area
        self.col_dtypes = {
            'job': 'string',
            'vacid': float,
            'name': 'string',
            'salary_from': float,
            'salary_to': float,
            'curr': 'string',
            'employer_id': float,
            'employer_name': 'string',
            'employer_url': 'string',
            'vacancy_url': 'string',
            'published_at': 'datetime64[ns]',
        }

    def parse_hh_page(self, job, page=0):
        payloads = {
            'area': self.area,
            'text': job,
            'only_with_salary': 'true',
            'employment': 'full',
            'search_field': self.search_field,
            'search_period': self.search_period,
            'per_page': self.per_page,
            'page': page,
        }
        return requests.get(f'{HH_URL}vacancies', params=payloads).json()

    def parse_vacancies(self, job: str):
        vacancies = {col: [] for col in self.col_dtypes.keys()}

        pages = 1
        page = 0
        while pages > 0:
            r = self.parse_hh_page(job, page=page)
            if 'items' not in r.keys() or not r['items']:
                break
            for vacancy in r['items']:
                vacancies['job'].append(job)
                vacancies['vacid'].append(vacancy['id'])
                vacancies['name'].append(vacancy['name'])
                vacancies['salary_from'].append(vacancy['salary']['from'])
                vacancies['salary_to'].append(vacancy['salary']['to'])
                vacancies['curr'].append(vacancy['salary']['currency'])

                vacancies['employer_id'].append(vacancy['employer'].get('id', None))
                vacancies['employer_name'].append(vacancy['employer']['name'])
                vacancies['employer_url'].append(vacancy['employer'].get('alternate_url', None))
                vacancies['vacancy_url'].append(vacancy['alternate_url'])
                vacancies['published_at'].append(vacancy['published_at'])

            pages = r['pages'] - r['page'] - 1
            page = r['page'] + 1

        return vacancies

    @staticmethod
    def aprise(row):
        if row.loc['salary_to'] is pd.NA:
            return int(round(row.loc['salary_from'] * 1.1, 0))
        if row.loc['salary_from'] is pd.NA:
            return int(round(row.loc['salary_to'] * .9, 0))
        return int(round((row.loc['salary_to'] + row.loc['salary_from']) / 2, 0))

    def get_vacancies(self, job) -> pd.DataFrame:
        vacs_data = self.parse_vacancies(job)
        vacancy_df = pd.DataFrame(vacs_data)
        if vacancy_df.empty:
            return vacancy_df
        vacancy_df['published_at'] = pd.to_datetime(vacancy_df.published_at).dt.tz_convert(None)
        vacancy_df = vacancy_df.astype(self.col_dtypes)
        vacancy_df = vacancy_df.convert_dtypes()

        vacancy_df.sort_values(by=['published_at', 'employer_name'], ascending=False, inplace=True)
        vacancy_df.drop_duplicates(subset=['name', 'employer_id'], keep='first', inplace=True)
        salary_apr = vacancy_df[['salary_from', 'salary_to']].apply(self.aprise, axis=1)
        vacancy_df.insert(5, 'salary_apr', salary_apr)
        print(job, vacancy_df.shape[0])
        return vacancy_df


if __name__ == '__main__':
    hh = HH()
    df = hh.get_vacancies('1с программист')
    df.info()
