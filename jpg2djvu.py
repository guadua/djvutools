#!/usr/bin/env python3
import os
import pdb
import subprocess as sp
import pandas as pd
density = 300
NJOBS = 4
OCRODJVU_CMD = '/home/hajime/Git/ocrodjvu/ocrodjvu'

def find_product(row):
    pbm = row[0].replace('.jpg', '.pbm')
    djvu = row[0].replace('.jpg', '.djvu')
    return pd.Series([pbm, djvu])

def has_text(djvu):
    ret = sp.check_output("djvused %s -e 'select 1; print-txt'" % djvu, shell=True)
    return ret.startswith(b'(page 0 0 0 0') == False

def main():
    cwd = os.getcwd().split('/')[-1] + '.djvu'
    # merge
    djvm_cmd = 'djvm -c %s.djvu ????.djvu' % cwd
    jpg_files = sorted([x for x in os.listdir('.') if x.endswith('.jpg')])
    df = pd.DataFrame(jpg_files)
    df[['pbm', 'djvu']] = df.apply(find_product, axis=1)

    cmds = []
    for index, row in df.iterrows():
        jpg, pbm, djvu = row
    
        if not os.path.exists(pbm) or os.stat(pbm).st_size == 0:
            cmds.append('convert -density %s %s %s ' % (density, jpg, pbm))
        if not os.path.exists(djvu) or os.stat(pbm).st_size == 0:
            cmds.append('cjb2 -clean %s %s' % (pbm, djvu))
        if os.path.exists(djvu):
            has_text(djvu)
            cmds.append('%s -j %s --in-place -l eng %s' % (OCRODJVU_CMD, NJOBS, djvu))
    cmds.append(djvm_cmd)
    for cmd in cmds:
        print(cmd)
        os.system(cmd)


if __name__ == '__main__':
    main()
