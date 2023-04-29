from datetime import date

import pandas as pd

from hh import HH
import clearing

JOBS_FILE = 'settings/jobs.csv'


def read_vacancies_titles_from_csv(file):
    """
    Чтение csv файла с названиями вакансий
    """
    vacancies = pd.read_csv(file)
    vacancies = vacancies[vacancies['search'].notna()]
    vacancy_titles = vacancies['title'].to_list()

    print('Будет произведен анализ следующих вакансий:')
    for title in vacancy_titles:
        print(title)
    print("")

    return vacancy_titles


def parse():
    hr = HH()

    today = date.today()
    excel_file = f'vacdata/vacancies_{today.strftime("%Y-%m-%d")}.xlsx'

    empty_vacancies_file = pd.DataFrame(columns=hr.col_dtypes.keys())
    empty_vacancies_file.to_excel(excel_file, sheet_name="Вакансии", index=False)

    jobs = read_vacancies_titles_from_csv(JOBS_FILE)

    for job in jobs:
        df = hr.get_vacancies(job)
        df = clearing.exclude_non_relevant_jobs(df, how='soft', score_cutoff=89)

        vc = pd.read_excel(excel_file, sheet_name='Вакансии')
        new_vc = pd.concat([vc, df], axis=0)
        new_vc.to_excel(excel_file, sheet_name='Вакансии', index=False, engine='xlsxwriter')


if __name__ == "__main__":
    parse()
