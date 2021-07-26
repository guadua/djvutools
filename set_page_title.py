#!/usr/bin/env python3
'''
usage:
    python3 set_page_title.py [djvu_file] [page.csv]

    pages.csv should be:

    Start,Style,Prefix,Logical
    3,i,,1          # from 3 to 6, 'select 3; set-page-title i;', etc.
    7,1,,1          # from 7 to 99, 'select 7, set-page-title 1;', etc.
    50,i,plate,1    # from 50 to 99 'select 50, set-page-title plate-1', etc.
    100             # end page, only "Start" required
'''

import os
import sys
import roman
import pandas as pd
from pdb import set_trace

def csv2cmd(csv='pages.csv'):
    df = pd.read_csv('pages.csv')
    df.columns = [x.strip() for x in df.columns]
    df['Stop'] = df['Start'].shift(-1)-1
    df['Style'] = df['Style'].fillna('')
    df['Prefix'] = df['Prefix'].fillna('')
    df['Logical'] = df['Logical'].fillna(-1).astype(int)
    df.loc[max(df.index), 'Stop'] = df.loc[max(df.index), 'Start']
    df['Stop'] = df['Stop'].astype(int)
    set_trace()

    cmds = []
    for index, row in df[:-1].iterrows():
        shift = int(row['Start'] - row['Logical'])
        prefix = row['Prefix']
        for p in range(int(row['Start']), int(row['Stop'])+1):
            logical = p - shift
            if row['Style'] == 'i':
                logical = roman.toRoman(logical).lower()
            elif row['Style'] == 'I':
                logical = roman.toRoman(logical)
            elif row['Style'] == 1:
                pass

            if prefix != '':
                logical = '-'.join([prefix, str(logical)])

            cmd = 'select %s; set-page-title %s;' % (p, logical)
            cmds.append(cmd)
    cmds.append('save;')
    return cmds

def main():
    fname = sys.argv[1]
    csv = sys.argv[2]
    cmds = csv2cmd(csv)
    cmd = 'djvused %s -e \'%s\'' % (fname, ''.join(cmds))
    print(cmd)
    os.system(cmd)

if __name__ == '__main__':
    main()