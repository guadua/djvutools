#!/usr/bin/env python3
import os
import sys
import pandas as pd
from pdb import set_trace

def to_sexp(csv, offset=0):
    with open(csv, 'r') as f:
        header = f.read()
        if header.lower().startswith('depth'):
            header = 0
        else:
            header = None
    df = pd.read_csv(csv, sep=";", header=header)
    df.columns = [0,1,2,3]

    sexp = '(bookmarks \n'
    for index, row in df.iterrows():
        depth = row[0]
        next_depth = df[0].shift(-1, fill_value=1)[index]

        title = row[2]
        page = int(row[3])
        sexp += ' ' * depth * 2 + '("%s" "#%s"' % (title, page+offset)
        sexp += ')' * (depth - next_depth +1)
        sexp += '\n'
    # close
    sexp += ')'
    print(sexp)
    return df, sexp

def flatten(offset=0):
    import itertools
    from sexpdata import loads
    with open('bookmarks.txt', 'r') as f:
        sexp = loads(f.read())

    # https://stackoverflow.com/questions/952914/how-to-make-a-flat-list-out-of-list-of-lists
    flat_list = []
    depth = 1
    for sublist in sexp[1:]: # skip Symbol(bookmarks)
        if len(sublist) == 2:
            flat_list.append([depth] + sublist)
        else:
            flat_list.append([depth] + sublist[:2])
            for item in sublist[2:]:
                flat_list.append([depth+1] + item)
    df = pd.DataFrame(flat_list)
    df[3] = df[2] # page
    df[2] = df[1] # title
    df[1] = 0     # open
    # page
    df[3] = df[3].apply(lambda x: int(x.replace('#', ''))-offset)

    df.to_csv('bookmarks.csv', sep=";", header=None, index=None)
    print('wrote to bookmarks.csv')

def main():
    djvu, csv, offset = sys.argv[1], sys.argv[2], int(sys.argv[3])
    txt = csv.replace('.csv', '.txt')
    df, sexp = to_sexp(csv, offset=offset)
    with open(txt, 'w') as f:
        f.write(sexp)
    print('wrote to %s' % txt)
    cmd = 'djvused %s -e "set-outline %s; save"' % (djvu, txt)
    print(cmd)
    os.system(cmd)

if __name__ == '__main__':
    if sys.argv[1] == '-1':
        offset = int(sys.argv[2])
        flatten(offset)
    else:
        main()
