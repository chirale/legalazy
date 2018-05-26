import settings
import utilities
from flask_stache import render_template
from flask import jsonify


class ServeRequestedContent:

    def __init__(self, **kwargs):
        """
        Class to render response based on accept header
        :param kwargs:

        """
        print('init')
        self.soup = kwargs.get('soup', None)
        self.request_headers = kwargs.get('request_headers', None)
        self.keep_document_styles = kwargs.get('keep_document_styles', True)
        self.docdict = kwargs.get('docdict', True)
        self.is_404 = kwargs.get('is_404', True)
        self.is_html = True if self.request_headers == 'text/html' else False
        self.funcname_suffix = self.request_headers.replace("/", "_")
        """
        print(self.funcname_suffix)
        self.varname_keep_document_styles = "KEEP_DOCUMENT_STYLES_{}".format(self.funcname_suffix.upper())
        local_keep_document_styles = getattr(settings, self.varname_keep_document_styles.upper(), None)
        self.keep_document_styles = local_keep_document_styles if local_keep_document_styles else self.keep_document_styles
        """
        self.keep_document_styles = settings.KEEP_DOCUMENT_STYLES
        print(self.request_headers)
        print("get_content_{}".format(self.funcname_suffix))

    def render(self):
        """
        :return: the Flask response, ready to be served by a route-decorated function
        """
        function_name = "get_content_{}".format(self.funcname_suffix)
        try:
            render_function = getattr(self, function_name, '')
        except AttributeError:
            render_function = self.get_content_text_html
        return render_function()

    def get_content_text_html(self):
        for element in self.soup.select('body > *'):
            self.docdict['body'] += str(element)
        if not self.is_404 and self.keep_document_styles:
            # Do not use styles for 404
            if settings.AUTODETECT_EXTERNAL_FONTS:
                auto_generated_css = self.soup.head.select('style')[0].text
                self.docdict['external_fonts'] = \
                    [settings.GOOGLE_FONTS_PATTERN.format(item.replace(' ', settings.GOOGLE_FONTS_WHITESPACE))
                        for item in utilities.sift_gfonts(utilities.extract_fonts(auto_generated_css))]
            self.docdict['style'] = utilities.css_wrap_doc_container_id(auto_generated_css)
        else:
            self.docdict['status'] = 404
        return render_template('base', **self.docdict)

    def get_content_application_json(self):
        print(self.docdict)
        return jsonify(dict(
            body=self.soup.body.get_text(),
            title=self.docdict['title']
        ))
        # return jsonify(self.soup.get_text())
