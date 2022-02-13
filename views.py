# from odf.opendocument import load
import settings
import utilities
import models
from flask import Flask
from odf.odf2xhtml import ODF2XHTML
import io
from os import path
from bs4 import BeautifulSoup
from flask_stache import render_template
from flask import request
from serverequestedcontent import ServeRequestedContent
from pandas_ods_reader import read_ods

app = Flask(__name__)

@app.route('/ods')
def index_ods():
    slug = "ods"
    is_404 = False
    db = models.DocuwebDb()
    dbsession = db.sessionmaker()
    menu = utilities.menu_items(dbsession=dbsession, slug=slug)
    newdoc = dict(style='', body='', nav='', title='', status=200, is_front=False, menu_items=menu)
    filepath = "{}/{}".format(settings.DOCUMENT_DIRECTORY, settings.INDEX_ODS)
    # load a sheet based on its name
    sheet_name = "pages"  # pages|config
    df = read_ods(filepath, sheet_name)
    newdoc['body'] = "<pre>{}</pre>".format(df.to_string())
    return render_template('base', **newdoc)

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
        odhandler = ODF2XHTML()
        # convert OpenDocument to XHTML with python3-odfpy
        result = odhandler.odf2xhtml(fullfilepath)
        outf.write(result.encode('utf-8'))
        html_doc = outf.getvalue().decode('utf-8')
        # Parse the HTML document to get body and style.
        # Different results based on Accept: text/html | application/json
        print(request.headers['Accept'])
        rqc = ServeRequestedContent(
            soup=BeautifulSoup(html_doc, 'html.parser'),
            request_headers=request.headers['Accept'].split(',')[0].split(';')[0],
            docdict=newdoc,
            is_404=is_404
        )
        return rqc.render()
    except TypeError:
        # document not specified, error
        newdoc['status'] = 500
        return render_template('base', **newdoc)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
