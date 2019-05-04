# IG5-web

It's simple, really:

1. add/update data for another year (\*.JSON files in data/)
  - schools
  - sponsors
  - summary


2. add static files
  - photos
    - static/img/summary/
  - docs
    - static/doc/

then run `python3 ig5_web/freeze.py` and copy content of `build/` to hosting.

You may want to set `minify_html = False` in `ig5_web/app.py` before freezing
the flask app.

3. do a backup of build/ (just in case)


## TODO

- [ ] add existing helper scripts
  - for parsing route coordinates, resizing and adding watermark to images, ...
- [ ] move photos to a hosted photo-gallery
- [ ] add multi-language support
