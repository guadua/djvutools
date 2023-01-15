#!/usr/bin/env python3
import os, sys
import pandas as pd

def get_csv(f):
    if f.endswith('.pdf'):
        csv = f.replace('.pdf', '_toc.csv')
    else:
        csv = f.replace('.djvu', '_toc.csv')
    if not os.path.exists(csv):
        raise FileNotFoundError('%s not found' % csv)
    df = pd.read_csv(csv, sep=';', header=None)
    return df

def add_toc_pdf(pdf):
    import fitz
    df = get_csv(pdf)
    toc = []
    for index, row in df.iterrows():
        toc.append((row[0], str(row[2]), row[3]))

    print(toc)
    doc = fitz.open(pdf)
    doc.set_toc(toc)
    doc.save(pdf, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)

def add_toc_djvu(f):
    df = get_csv(f)
    toc = ['(bookmarks']
    _level = 1
    for index, row in df.iterrows():
        level = row[0]
        if level == _level:
            pass
        elif level == _level + 1:
            toc[-1] = toc[-1][:-1]
        elif level > _level + 1:
            raise ValueError('level jump at %s' % index)
        elif level < _level:
            toc[-1] = toc[-1] + ')'*(_level-level)
        s = ' '*level
        title = row[2]
        page = '#' + row[3]
        s += '("{title}" "{page}")'.format(title=title, page=page)
        toc.append(s)

        _level = level

    toc.append(')'*(_level-1))
    toc.append(')') # closing (bookmarks
    ss = '\n'.join(toc)
    print(ss)
    with open('outline.txt', 'w') as ff:
        ff.write(ss)
    cmd = 'djvused %s -e "set-outline outline.txt; save"' % f
    print(cmd)
    os.system(cmd)

if __name__ == '__main__':
    if sys.argv[1].endswith('pdf'):
        pdf = sys.argv[1]
        add_toc_pdf(pdf)
    elif sys.argv[1].endswith('djvu'):
        f = sys.argv[1]
        add_toc_djvu(f)

