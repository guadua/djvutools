# djvutools

- `bookmarks.py [djvu_file] [toc.csv] [shift]`
- `set_page_title.py [djvu_file] [pages.csv]`
- `add_toc.py [pdf_file|djvu_file]`
  - if `pdf_file`, search `_toc.csv` and add toc using PyMuPDF
  - if `djvu_file`, search `_toc.csv` and create `outline.txt` and apply for `djvu_file` using `'set-outline'` command

`toc.csv` and `pages.csv` should be *jpdftweak* style formatted. 
