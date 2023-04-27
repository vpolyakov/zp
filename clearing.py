import pandas as pd
from thefuzz import process

black_vac = pd.read_excel('settings/exclude_jobs.xlsx', sheet_name='jobs')
black_vac = black_vac.astype('string')


class ClearError(Exception):
    pass


# TODO для пустых плохих вакансий сделать обработку
def exclude_vac_names_strict(row: pd.Series, ex_df: pd.DataFrame) -> bool:
    excluded_names = ex_df[ex_df.job.str.lower() == row.loc['job'].lower()]['exclude_name'].str.lower().values
    return not (row.loc['name'].lower() in excluded_names)


def strict_filter_non_relevant(df: pd.DataFrame) -> pd.DataFrame:
    return df[df.apply(exclude_vac_names_strict, axis=1, args=(black_vac,))]


def excluded_vac_nam(row: pd.Series, ex_df: pd.DataFrame, score_cutoff: int = 90) -> bool:
    excluded_df = ex_df[ex_df.job.str.lower() == row.loc['job'].lower()]
    if excluded_df.empty:  # Если нет плохих вакансий для этой специальности, то возвращаю True
        return True
    excluded_names = excluded_df['exclude_name'].str.lower().drop_duplicates().values

    res = process.extractOne(row.loc['name'].lower(), excluded_names)
    if res[1] < score_cutoff:
        return True
    else:
        return False


def soft_exclude_vac(df: pd.DataFrame, score_cutoff: int = 90) -> pd.DataFrame:
    return df[df.apply(excluded_vac_nam, axis=1, args=(black_vac, score_cutoff))]


def soft_include_vac(df: pd.DataFrame, score_cutoff: int = 90) -> pd.DataFrame:
    return df[~df.apply(excluded_vac_nam, axis=1, args=(black_vac, score_cutoff))]


def exclude_non_relevant_jobs(df: pd.DataFrame, how='soft', score_cutoff: int = 90):
    if how not in ['soft', 'strict']:
        raise ClearError('"how" должно установлено либо "soft", либо "strict"')

    if how == 'soft':
        return soft_exclude_vac(df, score_cutoff=score_cutoff)
    else:
        return strict_filter_non_relevant(df)
