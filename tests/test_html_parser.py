import os
import sys
from xliff_converter import html_parser as hp

HTML5 = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta description="HTML5 test sample">
    <meta keywords="html5, sample">
    <meta http-equiv="keywords" content="sample, html5" />

    <title>This is title</title>

    <style>.foo { color: blue; }</style>
    <script>console.log('Hello World!');</script>
</head>
<body>
    <h1>This is header</h1>
    <img src="http://via.placeholder.com/350x150" alt="Image caption">
    <p>Simple paragraph.</p>
    <p>
        Multiline paragraph<br>
        Second line<br />
        Third line
    </p>
    <p>Paragraph <span class="foo">with</span> <em>inline tags</em>.</p>
    <p>Paragraph <a href="http://example.com">with a link</a>.</p>
    <p><strong>Paragraph with enclosing inline tags.</strong></p>
    <p>Paragraph with entity&nbsp;reference.</p>
    <p>Paragraph with character&#160;reference.</p>
    <p>First sentence. Second sentence. Third sentence</p>
    <p>Inline image: <img src="http://via.placeholder.com/350x150" /></p>
    <pre><code>import this</code></pre>
</body>
</html>'''

this_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(this_dir)
sys.path.append(base_dir)


def test_detect_encoding():
    with open(os.path.join(base_dir, 'samples', 'sample_html4.html'), 'rb') as fo:
        html = fo.read()
        assert hp.detect_encoding(html) == 'iso-8859-1'
    with open(os.path.join(base_dir, 'samples', 'sample_html5.html'), 'rb') as fo:
        html = fo.read()
        assert hp.detect_encoding(html) == 'utf-8'
    assert hp.detect_encoding(b'<html></html>') is None


def test_content_parser_html5():
    parser = hp.ContentParser()
    parser.feed(HTML5)
    cont_list = parser.content_list
    assert len(cont_list) == 18
    assert 'HTML5 test sample' in cont_list
    assert 'html5, sample' in cont_list
    assert 'Image caption' in cont_list
    assert 'Paragraph <span class="foo">with</span><em>inline tags</em>.' in cont_list
    assert 'Second line' in cont_list and 'Third line' in cont_list
    assert 'Paragraph with enclosing inline tags.</strong>' in cont_list
    assert 'Paragraph with entity&nbsp;reference.' in cont_list
    assert 'Paragraph with character&#160;reference.' in cont_list
    assert 'Inline image: <img src="http://via.placeholder.com/350x150" />' in cont_list
    assert '.foo { color: blue; }' not in cont_list
    assert 'console.log(\'Hello World!\');' not in cont_list


def test_segment_html():
    segments = list(hp.segment_html(HTML5))
    assert len(segments) == 19


def test_add_t_tags():
    string = '<b><i>String with <span>various open</span>,<br>close and isolated tags.</em></b>'
    segment = hp.add_t_tags(string)
    print(segment)
    assert segment == '<bpt id="1">&lt;b&gt;</bpt><it id="2">&lt;i&gt;</it>' \
                      'String with <bpt id="3">&lt;span&gt;</bpt>various open' \
                      '<ept id="3">&lt;/span&gt;</ept>,<it id="4">&lt;br&gt;</it>' \
                      'close and isolated tags.<it id="5">&lt;/em&gt;</it>' \
                      '<ept id="1">&lt;/b&gt;</ept>'


def test_create_skeleton():
    html = '<html><head><title>Page title</title></head><body><p>Page body</p></body></html>'
    segments = ['Page title', 'Page body']
    skl = '<html><head><title>{{%1%}}</title></head><body><p>{{%2%}}</p></body></html>'
    assert hp.create_skeleton(segments, html) == skl


def test_create_xliff():
    segments = ['Page title', 'Page&nbsp;body']
    skl = '<html>' \
          '<head><title>{{%1%}}</title></head>' \
          '<body>' \
          '<p>{{%2%}}</p>' \
          '</body></html>'
    xliff = b'<?xml version="1.0" encoding="utf-8"?>' \
            b'<xliff version="1.2">' \
            b'<file datatype="html" original="index.html" source-language="en">' \
            b'<header>' \
            b'<tool tool-id="py-xliff-converter" tool-name="Python XLIFF Converter"/>' \
            b'<skl><internal_file form="base64">' \
            b'PGh0bWw+PGhlYWQ+PHRpdGxlPnt7JTElfX08L3RpdGxlPjwvaGVhZD48Ym9keT48cD57eyUyJX19PC9wPjwvYm9keT48L2h0bWw+' \
            b'</internal_file></skl>' \
            b'</header>' \
            b'<body>' \
            b'<trans-unit id="1" xml:space="preserve"><source>Page title</source>' \
            b'</trans-unit><trans-unit id="2" xml:space="preserve"><source>Page\xc2\xa0body</source></trans-unit>' \
            b'</body></file></xliff>'
    assert hp.create_xliff(segments, skl, 'index.html') == xliff
