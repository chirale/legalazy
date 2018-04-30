# from odf.opendocument import load
import settings
import utilities
import models
from flask import Flask
from odf.odf2xhtml import ODF2XHTML
import io
from os import path
from bs4 import BeautifulSoup
from flask_stache import render_view, render_template

app = Flask(__name__)

"""
@app.route('/')
def pages(slug):
    db = models.DocuwebDb()
    dbsession = db.sessionmaker()
    newdoc = dict(style='', body='', nav='', title='', status=200)
    front_page = dbsession.query(models.Page).get(settings.FRONT_SLUG)
    newdoc = dict(title=front_page.title)
"""


@app.route('/')
def front():
    slug = '~'
    return pages(slug)


@app.route('/<slug>')
def pages(slug):
    """
    export FLASK_APP=views.py
    flask run

    Per rimuovere dipendenze:
    pip-autoremove pyquery


    :return:
    """
    is_404 = False
    db = models.DocuwebDb()
    dbsession = db.sessionmaker()
    menu = utilities.menu_items(dbsession=dbsession, slug=slug)
    newdoc = dict(style='', body='', nav='', title='', status=200, is_front=False, menu_items=menu)
    try:
        # exclude special path
        assert slug not in [settings.SLUG_404, settings.FRONT_SLUG]  # settings.FRONT_SLUG,
        # get current page from slug from database
        current_page = dbsession.query(models.Page).get(slug)
        assert current_page
    except AssertionError:
        if slug == settings.FRONT_SLUG:
            newdoc['is_front'] = True
            current_page = dbsession.query(models.Page).get(settings.FRONT_SLUG)
        else:
            is_404 = True
            current_page = dbsession.query(models.Page).get(settings.SLUG_404)
    newdoc['title'] = utilities.head_title(page=current_page, dbsession=dbsession)
    try:
        outf = io.BytesIO()
        docs_directory = settings.DOCUMENT_DIRECTORY
        filename = current_page.file
        # get the full document file path
        fullfilepath = path.join(docs_directory, filename)
        #####################
        """
        @TODO https://docs.python.org/3/library/html.parser.html
        OPPURE
        https://www.crummy.com/software/BeautifulSoup/bs4/doc/
            https://stackoverflow.com/a/11918151
        """
        odhandler = ODF2XHTML()
        # convert OpenDocument to XHTML with python3-odfpy
        result = odhandler.odf2xhtml(fullfilepath)
        outf.write(result.encode('utf-8'))
        html_doc = outf.getvalue().decode('utf-8')
        # parse the HTML document to get body and style
        soup = BeautifulSoup(html_doc, 'html.parser')
        for element in soup.select('body > *'):
            newdoc['body'] += str(element)
        if not is_404 and settings.KEEP_DOCUMENT_STYLES:
            # Do not use styles for 404
            newdoc['style'] = utilities.css_wrap_doc_container_id(soup.head.select('style')[0].text)
        else:
            newdoc['status'] = 404
    except TypeError:
        # document not specified, empty fallback
        pass
    return render_template('base', **newdoc)
