import pandas as pd
import re
from bs4 import BeautifulSoup, Comment
import requests
import xlsxwriter
import sys

def get_soup(url):
    response = requests.get(url)
    page = response.text
    soup = BeautifulSoup(re.sub('<!--|-->', '', page), 'html5lib')
    return soup

def scrape_bref_lgseason_standardP(league, season):
    url = f'https://www.baseball-reference.com/leagues/{league}/{season}.shtml'
    response = requests.get(url)
    page = response.text
    soup = BeautifulSoup(re.sub('<!--|-->', '', page), 'html5lib')
    pitching = soup.find('table', {'id': 'teams_standard_pitching'})
    rows = [r for r in pitching.find_all('tr')]

    d = {}
    for row in rows[1:-1]:
        items = row.find_all('td')
        if len(items) > 0:
            idx = row.find('th').text
            d[idx] = [j.text.strip() for j in items]
    df = pd.DataFrame.from_dict(d, orient='index')
    df.columns = [k.text for k in rows[0].find_all('th')][1:]

    df = df.apply(pd.to_numeric)
    df = df.reset_index().rename(columns={'index':'Team'})
        
    return df

def scrape_bref_season_standardP(season):
    dfs = {}
    for lg in ['AL', 'NL']:
        dfs[lg + '_' + str(season)] = scrape_bref_lgseason_standardP(lg, season)
    return dfs

def write_bref_season_standardP(season_dfs, path):
    season_str = [k.split('_')[1] for k in season_dfs.keys()][0]
    writer = pd.ExcelWriter(path + '/' + season_str + '_standard_pitching.xlsx', engine='xlsxwriter')
    for lgseason in ['AL_' + season_str, 'NL_' + season_str]:
        season_dfs[lgseason].to_excel(writer, sheet_name=lgseason, index=False)
        wb = writer.book
        ws = writer.sheets[lgseason]
        fmt = wb.add_format({'italic': True})
        ws.set_row(len(season_dfs[lgseason]), cell_format = fmt)
    writer.save()
    
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Please specify command in the following format [script file] [season] [output directory]')
    elif not re.match('\d{4}', sys.argv[1]):
        print('Please specify the season in the following format: YYYY.')
    else:
        try:
            path = sys.argv[2]
            season_dfs = scrape_bref_season_standardP(sys.argv[1])
        except Exception as e:
            print(e)
        else:
            write_bref_season_standardP(season_dfs, path)