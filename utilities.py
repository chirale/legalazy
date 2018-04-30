import settings
import models
import sass


def is_front(page):
    """
    :param page: Page row.
    :return: True if page is front page, False if it's not.
    """
    return settings.FRONT_SLUG == page.slug


def head_title(**kwargs):
    """
    Display the page title with suffix if settings.MENU_INCLUDE_FRONT_NAME
    is True. Used in the html > head > title tag.

    :param kwargs: Active dbsession; Original title
    :return: Original title plus optional suffix.
    """
    dbsession = kwargs.get('dbsession', False)
    page = kwargs.get('page', None)
    try:
        assert dbsession
    except AssertionError:
        return page.title
    front_page = dbsession.query(models.Page).get(settings.FRONT_SLUG)
    title_suffix = "{}{}".format(settings.MENU_FRONT_NAME_SEPARATOR, front_page.title)\
        if settings.MENU_INCLUDE_FRONT_NAME and not is_front(page) else ''
    return "{}{}".format(page.title, title_suffix)


def menu_items(**kwargs):
    """
    Generator of menu_items.

    :param kwargs: Current page slug; active dbsession.
    :return: Generator of menu items dictionaries.
    """
    slug = kwargs.get('slug', settings.SLUG_404)
    dbsession = kwargs.get('dbsession', False)
    try:
        assert dbsession
    except AssertionError:
        return
    for row in dbsession.query(models.Page).\
            filter(models.Page.in_nav==True).\
            order_by(models.Page.nav_order):
        title = row.title
        yield dict(
            title=title,
            href="/{}".format(row.slug)
        )


def css_wrap_doc_container_id(css_code):
    """
    Wrap CSS generated from Document conversion to XHTML with the
    settings.DOC_CONTAINER_ID identifier.

    :param css_code: Plain CSS code.
    :return: CSS code wrapped with #settings.DOC_CONTAINER_ID
    """
    wrapped_sass_code = "#%(id)s{%(css)s}" % dict(id=settings.DOC_CONTAINER_ID, css=css_code)
    return sass.compile(string=wrapped_sass_code)
