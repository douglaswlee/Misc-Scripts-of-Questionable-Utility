import pandas as pd
import re
from bs4 import BeautifulSoup, Comment
import requests
import xlsxwriter
import sys

def get_soup(url):
    '''
    Given:
        url, string of webpage location
    Return:
        soup, the python-compatible objects of the html parsed webpage content collected and read thru
        requests
    '''
    
    response = requests.get(url)
    page = response.text
    soup = BeautifulSoup(re.sub('<!--|-->', '', page), 'html5lib')
    return soup

def scrape_bref_lgseason_standardP(league, season):
    '''
    Given:
        league, the name of the MLB league ('AL' or 'NL') you want to scrape standard team pitching for
        season, the MLB season you want to scrape standard team pitching for
    Return:
        df, a dataframe of the standard team pitching table from Baseball-Reference for the given league/season
    '''
    
    # scrape the league season summary page
    url = f'https://www.baseball-reference.com/leagues/{league}/{season}.shtml'
    soup = get_soup(url)
    
    # get the team standard pitching table and all its rows
    pitching = soup.find('table', {'id': 'teams_standard_pitching'})
    rows = [r for r in pitching.find_all('tr')]
    
    # collect each table row (corresponding to team) into a dict then convert dict to dataframe
    d = {}
    for row in rows[1:-1]:
        items = row.find_all('td')
        if len(items) > 0:
            idx = row.find('th').text
            d[idx] = [j.text.strip() for j in items]
    df = pd.DataFrame.from_dict(d, orient='index')
    df.columns = [k.text for k in rows[0].find_all('th')][1:]
    
    # convert to numeric and de-index the team names
    df = df.apply(pd.to_numeric)
    df = df.reset_index().rename(columns={'index':'Team'})
        
    return df

def scrape_bref_season_standardP(season):
    '''
    Given:
        season, the MLB season you want to scrape standard team pitching for
    Return:
        dfs, a dict of dataframesof the standard team pitching table from Baseball-Reference for leagues in the given season
    '''
    
    # initialize dict of dataframes for the leagues and then scrape them
    dfs = {}
    for lg in ['AL', 'NL']:
        dfs[lg + '_' + str(season)] = scrape_bref_lgseason_standardP(lg, season)
    return dfs

def write_bref_season_standardP(season_dfs, dir_path):
    '''
    Given:
        season_dfs, a dict of dataframes of the scraped tables for each league for a given season
        dir_path, the directory path where the .xlsx file will be written
    Write season_dfs to a .xlsx file with each league on its own formatted sheet
    '''
    
    # create/open .xlsx file to write season_dfs
    season_str = [k.split('_')[1] for k in season_dfs.keys()][0]
    writer = pd.ExcelWriter(dir_path  + '/' + season_str + '_standard_pitching.xlsx', engine='xlsxwriter')
    
    # for each league, write to its own sheet and format the last row (for the 'Lg Avg') to be in italics and save file
    for lgseason in ['AL_' + season_str, 'NL_' + season_str]:
        season_dfs[lgseason].to_excel(writer, sheet_name=lgseason, index=False)
        wb = writer.book
        ws = writer.sheets[lgseason]
        fmt = wb.add_format({'italic': True})
        ws.set_row(len(season_dfs[lgseason]), cell_format = fmt)
    writer.save()
    
# check for the correct number of arguments after the script file: the season and the output directory path
# then check if the season is specified in the correct format before trying to scrape and write to .xlsx file
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Please specify command in the following format [script file] [season] [output directory]')
    elif not re.match('\d{4}', sys.argv[1]):
        print('Please specify the season in the following format: YYYY.')
    else:
        try:
            dir_path = sys.argv[2]
            season_dfs = scrape_bref_season_standardP(sys.argv[1])
            write_bref_season_standardP(season_dfs, dir_path)
        except Exception as e:
            print(e)