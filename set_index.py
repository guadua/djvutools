#!/usr/bin/env python3
import os
import re
import sys
import time
import argparse

import djvu.const
import djvu.decode
import djvu.sexpr

import pandas as pd

import pdb

EMPTY_TEXT_SEXPR = djvu.sexpr.Expression([djvu.const.TEXT_ZONE_PAGE, 0, 0, 0, 0, ''])

class ArgumentParser(argparse.ArgumentParser):

    def __init__(self):
        argparse.ArgumentParser.__init__(self)
        self.add_argument('-p', '--pages', dest='pages', action='store', help='pages to process')
        self.add_argument('path', metavar='DJVU-FILE', action='store', help='DjVu file to process')

    def parse_args(self):
        options = argparse.ArgumentParser.parse_args(self)
        try:
            if options.pages is not None:
                pages = []
                for rng in options.pages.split(','):
                    if '-' in rng:
                        x, y = map(int, options.pages.split('-', 1))
                        pages += range(x, y+1)
                    else:
                        pages += [int(rng)]
                options.pages = pages
        except (TypeError, ValueError):
            self.error('Unable to parse page numbers')
        return options

def get_index(sexpr):
    mapareas = []
    columns = sexpr[5:]
    for col in columns:
        paragraphs = col[5:]
        for para in paragraphs:
            if not isinstance(para[5], djvu.sexpr.StringExpression):
                if djvu.const.get_text_zone_type(para[5:][0][0].value) is djvu.const.TEXT_ZONE_LINE:
                    lines = para[5:]
                    for l in lines:
                        if not isinstance(l, djvu.sexpr.StringExpression):
                            words = l[5:]
                            for maparea in get_mapareas(words):
                                mapareas.append(maparea)
                elif djvu.const.get_text_zone_type(para[5:][0][0].value) is djvu.const.TEXT_ZONE_WORD:
                    words = para[5:]
                    for maparea in get_mapareas(words):
                        mapareas.append(maparea)
    return mapareas

def get_mapareas(words):
    mapareas = []
    pattern = r'(\d+)(,|F|f|ff|)'
    pattern2 = r'(\d+)\-(\d+),'
    for w in words:
        if not isinstance(w, djvu.sexpr.StringExpression):
            p = None
            m2 = re.match(pattern2, w[5].value)
            if m2 is not None:
                p = m2.groups()[0]

            m1 = re.match(pattern, w[5].value)
            if m1 is not None:
                p = m1.groups()[0]

            if p is not None:
                url = djvu.sexpr.Expression('#' + p)
                width = djvu.sexpr.Expression(w[3].value-w[1].value)
                height = djvu.sexpr.Expression(w[4].value-w[2].value)
                rect = djvu.sexpr.Expression([djvu.const.MAPAREA_SHAPE_RECTANGLE, w[1], w[2], width, height])
                xor = djvu.const.MAPAREA_BORDER_XOR
                maparea = djvu.sexpr.Expression([djvu.const.ANNOTATION_MAPAREA, url, djvu.sexpr.Expression(''), rect, [xor]])
                mapareas.append(maparea)
    return mapareas



class Context(djvu.decode.Context):
    def handle_message(self, message):
        if isinstance(message, djvu.decode.ErrorMessage):
            print(message, file=sys.stderr)
            os._exit(1)
    def process_page(self, page):
        print('- Page #{0}'. format(page.n + 1), file=sys.stderr)
        page.get_info()
        #TODO
        df = get_index(page.text.sexpr)
        return df

    def process(self, path, pages=None):
        print('Processing {path!r}:'.format(path=path), file=sys.stderr)
        document = self.new_document(djvu.decode.FileURI(path))
        document.decoding_job.wait()

        if pages is None:
            pages = iter(document.pages)
        else:
            pages = (document.pages[i - 1] for i in pages)
        for page in pages:
            ant = 'page%04d.ant' % (page.n+1)
            with open(ant, 'w') as f:
                for maparea in self.process_page(page):
                    maparea.print_into(f)
            cmd = 'djvused %s -e "select %s; set-ant %s; save"' % (path, page.n+1, ant)
            os.system(cmd)
            time.sleep(0.1)

def main():
    parser = ArgumentParser()
    options = parser.parse_args()
    context = Context()
    context.process(options.path, options.pages)

if __name__ == '__main__':
    main()
