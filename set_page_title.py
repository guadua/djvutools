#!/usr/bin/env python3
'''
usage:
    python3 set_page_title.py [djvu_file] [page.csv]

    pages.csv should be:

    Start,Style,Prefix,Logical,Suffix
    3,i,,1          # from 3 to 6, 'select 3; set-page-title i;', etc.
    7,1,,1          # from 7 to 99, 'select 7, set-page-title 1;', etc.
    50,i,plate,1    # from 50 to 99 'select 50, set-page-title plate-1', etc.
    100             # end page, only "Start" required
'''

import os
import sys
import json
import roman
import pandas as pd
import subprocess as sp
from internetarchive import get_item
from pdb import set_trace

def csv2cmd(csv='pages.csv'):
    df = pd.read_csv(csv, dtype={'Prefix': str})
    df.columns = [x.strip() for x in df.columns]
    df['Stop'] = df['Start'].shift(-1)-1
    df['Style'] = df['Style'].fillna('')
    df['Prefix'] = df['Prefix'].fillna('')
    df['Logical'] = df['Logical'].fillna(-1).astype(int)
    df.loc[max(df.index), 'Stop'] = df.loc[max(df.index), 'Start']
    df['Stop'] = df['Stop'].astype(int)
    df['Suffix'] = df['Suffix'].fillna('')
    # set_trace()

    cmds = []
    for index, row in df[:-1].iterrows():
        shift = int(row['Start'] - row['Logical'])
        prefix = row['Prefix']
        suffix = row['Suffix']
        for p in range(int(row['Start']), int(row['Stop'])+1):
            logical = p - shift
            if row['Style'] == 'i':
                logical = roman.toRoman(logical).lower()
            elif row['Style'] == 'I':
                logical = roman.toRoman(logical)
            elif row['Style'] == 'a':
                logical = ' abcdefghijklmnopqrstuvwxyz'[logical]
            elif row['Style'] == 'A':
                logical = ' abcdefghijklmnopqrstuvwxyz'[logical].upper()
            elif row['Style'] == 1:
                pass

            if prefix != '':
                if row['Style'] == '':
                    page_title = prefix
                else:
                    # set_trace()
                    page_title = ''.join([prefix, str(logical)])
            else:
                page_title = logical
            if suffix != '':
                page_title += suffix

            cmd = 'select %s; set-page-title %s;' % (p, page_title)
            cmds.append(cmd)
    cmds.append('save;')
    return cmds

def get_page_count(identifier):
    cmd = 'djvused %s.djvu -e "n"' % identifier
    ret = sp.check_output(cmd, shell=True)
    return int(ret)

def page_numbers_json_to_cmd(identifier, reset=False):
    item = get_item(identifier)
    page_count = get_page_count(identifier)

    cmds = []
    for f in item.get_files():
        if f.name.endswith('page_numbers.json'):
            print('page_numbers.json found:', f.name)
            f.download()
            with open(f.name, 'r') as ff:
                df = pd.DataFrame(json.load(ff))

            for index, row in df.iterrows():
                title = row['pages']['pageNumber']
                n = int(row['pages']['leafNum'])
                if title != '' and n < page_count:
                    if reset:
                        cmd = 'select %s_%04d.djvu; set-page-title %s_%04d.djvu;' % (identifier, n, identifier, n)
                    else:
                        cmd = 'select %s_%04d.djvu; set-page-title %s;' % (identifier, n+1, title)
                    cmds.append(cmd)
            cmds.append('save;')
    return cmds


def main():
    if len(sys.argv) == 1:
        if os.path.exists('pages.csv'):
            print(__doc__)
            print('pages.csv exists. abort.')
            sys.exit(1)
        print('create pages.csv?')
        if sys.stdin.readline() == 'y\n':
            with open('pages.csv', 'w') as f:
                f.write('Start,Style,Prefix,Logical,Suffix')
        sys.exit(0)

    fname = sys.argv[1]
    identifier = fname.replace('.djvu', '')
    if len(sys.argv) == 2:
        cmds = page_numbers_json_to_cmd(identifier, reset=False)
    elif len(sys.argv) == 3:
        csv = sys.argv[2]
        if csv == 'reset':
            cmds = page_numbers_json_to_cmd(identifier, reset=True)
        else:
            cmds = csv2cmd(csv)
    cmd = 'djvused "%s" -e \'%s\'' % (fname, ''.join(cmds))
    print(cmd)
    os.system(cmd)

if __name__ == '__main__':
    main()
