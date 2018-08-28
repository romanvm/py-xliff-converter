import pytest
from xliff_converter import html_rebuilder as hr

HTML_RU = '''<!DOCTYPE html>
<html lang="ru-ru">
<head>
  <meta charset="UTF-8">
  <title>Титул страницы</title>
</head>
<body>
<h1>Заголовок страницы</h1>
<p>Содержимое страницы с <strong>форматированием текста</strong>.</p>
</body>
</html>'''

XLIFF = '<?xml version="1.0" encoding="utf-8"?>' \
        '<xliff version="1.2">' \
        '<file datatype="html" original="example.html" source-language="en" target-language="ru-RU">' \
        '<header><tool tool-id="py-xliff-converter" tool-name="Python XLIFF Converter" />' \
        '<skl><internal_file form="base64">' \
        'PCFET0NUWVBFIGh0bWw+CjxodG1sIGxhbmc9ImVuIj4KPGhlYWQ+CiAgPG1ldGEgY2hhcnNldD0iVVRGLTgiPgogIDx0aXRsZT57eyUxJX19PC90aXRsZT4KPC9oZWFkPgo8Ym9keT4KPGgxPnt7JTIlfX08L2gxPgo8cD57eyUzJX19PC9wPgo8L2JvZHk+CjwvaHRtbD4=' \
        '</internal_file></skl></header>' \
        '<body>' \
        '<trans-unit id="1" xml:space="preserve">' \
        '<source>Page Title</source>' \
        '<target>Титул страницы</target>' \
        '</trans-unit>' \
        '<trans-unit id="2" xml:space="preserve">' \
        '<source>Page Header</source>' \
        '<target>Заголовок страницы</target>' \
        '</trans-unit>' \
        '<trans-unit id="3" xml:space="preserve">' \
        '<source>Page body with <bpt id="1">&lt;strong&gt;</bpt>text formatting<ept id="1">&lt;/strong&gt;</ept>.</source>' \
        '<target>Содержимое страницы с <bpt id="1">&lt;strong&gt;</bpt>форматированием текста<ept id="1">&lt;/strong&gt;</ept>.</target>' \
        '</trans-unit></body></file></xliff>'

XLIFF_BROKEN = '<?xml version="1.0" encoding="utf-8"?>' \
               '<xliff version="1.2">' \
               '<file datatype="html" original="example.html" source-language="en">' \
               '<header></header>' \
               '<body></body>' \
               '</file></xliff>'

XLIFF_INCOMPLETE = '<?xml version="1.0" encoding="utf-8"?>' \
                   '<xliff version="1.2">' \
                   '<file datatype="html" original="example.html" source-language="en" target-language="ru-RU">' \
                   '<header><tool tool-id="py-xliff-converter" tool-name="Python XLIFF Converter" />' \
                   '<skl><internal_file form="base64">' \
                   'PCFET0NUWVBFIGh0bWw+CjxodG1sIGxhbmc9ImVuIj4KPGhlYWQ+CiAgPG1ldGEgY2hhcnNldD0iVVRGLTgiPgogIDx0aXRsZT57eyUxJX19PC90aXRsZT4KPC9oZWFkPgo8Ym9keT4KPGgxPnt7JTIlfX08L2gxPgo8cD57eyUzJX19PC9wPgo8L2JvZHk+CjwvaHRtbD4=' \
                   '</internal_file></skl></header>' \
                   '<body>' \
                   '<trans-unit id="1" xml:space="preserve">' \
                   '<source>Page Title</source>' \
                   '<target>Титул страницы</target>' \
                   '</trans-unit>' \
                   '<trans-unit id="2" xml:space="preserve">' \
                   '<source>Page Header</source>' \
                   '<target>Заголовок страницы</target>' \
                   '</trans-unit>' \
                   '<trans-unit id="3" xml:space="preserve">' \
                   '<source>Page body with <bpt id="1">&lt;strong&gt;</bpt>text formatting<ept id="1">&lt;/strong&gt;</ept>.</source>' \
                   '</trans-unit></body></file></xliff>'

HTML1 = '<html lang="en"><head></head><body></body></html>'
HTML2 = '<html><head><meta http-equiv="content-language" value="en"></head><body></body></html>'
HTML3 = '<html><head></head><body></body></html>'


def test_rebuild_html():
    html_doc = hr.rebuild_html(XLIFF)
    assert html_doc.filename == 'example_ru-RU.html'
    assert html_doc.html == HTML_RU


def test_rebuild_partial_xliff():
    html_doc = hr.rebuild_html(XLIFF_INCOMPLETE, False)
    assert 'Page body with' in html_doc.html


def test_broken_xliff():
    with pytest.raises(hr.InvalidXliffError):
        hr.rebuild_html(XLIFF_BROKEN)
    with pytest.raises(hr.InvalidXliffError):
        hr.rebuild_html(XLIFF_INCOMPLETE, strict=True)


def test_set_language():
    html = hr.set_language(HTML1, 'uk-UA')
    assert 'lang="uk-ua"' in html
    html = hr.set_language(HTML2, 'ru-RU')
    assert 'value="ru-ru"' in html
    html = hr.set_language(HTML3, 'fr-FR')
    assert 'lang="fr-fr"' in html
