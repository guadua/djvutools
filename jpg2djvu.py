#!/usr/bin/env python3
'''
usage: jpg2djvu.py [clean|jpg|png|...]
    - clean : rm ????.jpg ????.djvu
'''

import os
import sys
import subprocess as sp
import pandas as pd
import numpy as np
from scipy import ndimage as nd
from PIL import Image
from pdb import set_trace

density = 300
NJOBS = 4
OCRODJVU_CMD = '/home/hajime/Git/ocrodjvu/ocrodjvu'

def clean(jpg):
    img = Image.open(jpg)
    bin = img.convert('L')
    arr = np.array(img)
    arr_bin = np.array(bin)
    without_pen = arr_bin < 100
    with_pen = arr_bin < 200
    pen = np.subtract(with_pen, without_pen, dtype=np.int).astype(np.bool)

    Image.fromarray(nd.binary_dilation(nd.binary_erosion(pen, iterations=2), iterations=2)).show()
    set_trace()

def find_product(row, ext):
    pbm = row[0].replace(ext, '.pbm')
    djvu = row[0].replace(ext, '.djvu')
    return pd.Series([pbm, djvu])

def has_text(djvu):
    ret = sp.check_output("djvused %s -e 'select 1; print-txt'" % djvu, shell=True)
    return ret.startswith(b'(page 0 0 0 0') == False

def main():
    ext = '.' + sys.argv[1]

    # for using the current directory name
    cwd = os.getcwd().split('/')[-1]

    # merge
    djvm_cmd = 'djvm -c %s.djvu ????.djvu' % cwd

    jpg_files = sorted([x for x in os.listdir('.') if x.endswith(ext)])
    df = pd.DataFrame(jpg_files)
    df[['pbm', 'djvu']] = df.apply(find_product, ext=ext, axis=1)

    if len(sys.argv) > 2:
         start, stop = (int(x) for x in sys.argv[2].split('-'))
         df = df[start:stop+1]

    cmds = []
    for index, row in df.iterrows():
        jpg, pbm, djvu = row

        if not jpg.endswith('.jpg'):
            cmd = "convert %s %s" % (jpg, jpg.replace(ext, '.jpg'))
            cmds.append(cmd)
            jpg = jpg.replace(ext, '.jpg') # change extension after convert
        if not os.path.exists(pbm) or os.stat(pbm).st_size == 0:
            cmd = "c44 -dpi %s %s" % (density, jpg)
            cmds.append(cmd)
        #     cmds.append('convert -density %s %s %s ' % (density, jpg, pbm))
        # if not os.path.exists(djvu) or os.stat(pbm).st_size == 0:
        #     cmds.append('cjb2 -clean %s %s' % (pbm, djvu))
        # if os.path.exists(djvu):
        #     if not has_text(djvu):
        #         cmds.append('%s -j %s --in-place -l eng %s' % (OCRODJVU_CMD, NJOBS, djvu))
    cmds.append(djvm_cmd)
    for cmd in cmds:
        print(cmd)
        os.system(cmd)


if __name__ == '__main__':
    if sys.argv[1] == "clean":
        cmd = 'rm ????.jpg ????.djvu'
        print(cmd)
        os.system(cmd)
    elif sys.argv[1] == 'ocr':
        cmd = 'ocrodjvu -j4 --in-place --render all %s' % sys.argv[2]
        print(cmd)
        os.system(cmd)
    else:
        main()
