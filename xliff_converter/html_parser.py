"""
HTML document parser module

It provides functions for extracting translatable strings from a HTML document
and creating an XLIFF 1.2 document that can be translated in most offline
and online CAT tools: SDL Trados, Deja Vu, memoQ, Transifex, SmartCAT
and many others.
"""

import re
import logging
import types
from base64 import b64encode
from html import escape, unescape
from html.parser import HTMLParser
from xml.dom.minidom import Document, parseString
from nltk.tokenize import sent_tokenize
from nltk import download
# Check if punkt tokenizer is available
try:
    sent_tokenize('Test.')
except LookupError:
    download('punkt')

__all__ = ['convert_html', 'detect_encoding']

INLINE_TAGS = (
    'a', 'abbr', 'acronym', 'applet', 'b', 'bdo', 'big', 'blink',
    'cite', 'code', 'del', 'dfn', 'em', 'embed', 'face', 'font', 'i',
    'iframe', 'img', 'ins', 'kbd', 'map', 'nobr', 'object',
    'param', 'q', 'rb', 'rbc', 'rp', 'rt', 'rtc', 'ruby', 's', 'samp', 'select',
    'small', 'span', 'spacer', 'strike', 'strong', 'sub', 'sup', 'symbol',
    'tt', 'u', 'var', 'wbr'
)

SELF_CLOSING_TAGS = (
    'area',
    'base',
    'br',
    'col',
    'command',
    'embed',
    'hr',
    'img',
    'input',
    'keygen',
    'link',
    'meta',
    'param',
    'source',
    'track',
    'wbr',
)

IGNORE_BLOCK_TAGS = ('script', 'style')

charset_re = re.compile(rb'<meta[^>]+charset="?([\w-]+)"[^>]*>', re.I)
whitespace_re = re.compile(r'^\s+$')
tag_string_re = re.compile(r'^(<[^>]*>)$')
tag_re = re.compile(r'(<[^>]+>)')
open_tag_re = re.compile(r'<(\w+)[^>]*>')
close_tag_re = re.compile(r'</(\w+)>')
entity_re = re.compile(r'(&#?\w+?;)')
pre_code_re = re.compile(r'^<pre[^>]*>\s*?<code[^>]*>', re.I)


class ContentParser(HTMLParser):
    """
    Extracts translatable blocks of text from HTML markup
    """
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self._content_list = []
        self._current_block = ''
        self._ignore_block = False

    @property
    def content_list(self):
        return self._content_list

    def handle_starttag(self, tag, attrs):
        if (tag in INLINE_TAGS and self._current_block) or tag == 'pre':
            self._current_block += self.get_starttag_text()
        elif tag in IGNORE_BLOCK_TAGS:
            self._ignore_block = True
        elif tag == 'br':
            self._finish_block()
        elif tag in ('meta', 'img'):
            self._process_translatable_attrs(attrs)

    def handle_startendtag(self, tag, attrs):
        if tag in INLINE_TAGS and self._current_block:
            self._current_block += self.get_starttag_text()
        elif tag == 'br':
            self._finish_block()
        elif tag in ('meta', 'img'):
            self._process_translatable_attrs(attrs)

    def handle_endtag(self, tag):
        if tag in INLINE_TAGS or tag == 'pre':
            self._current_block += '</{}>'.format(tag)
            if tag == 'pre':
                self._finish_block()
        elif tag in IGNORE_BLOCK_TAGS:
            self._ignore_block = False
        elif self._current_block:
            self._finish_block()

    def handle_data(self, data):
        if not self._ignore_block and not whitespace_re.search(data):
            self._current_block += data

    def handle_charref(self, name):
        if self._current_block:
            self._current_block += '&#' + name + ';'

    def handle_entityref(self, name):
        if self._current_block:
            self._current_block += '&' + name + ';'

    def error(self, message):
        logging.error(message)

    def _finish_block(self):
        self._content_list.append(self._current_block.strip(' \r\n'))
        self._current_block = ''

    def _process_translatable_attrs(self, attrs):
        attrs_dict = dict(attrs)
        if attrs_dict.get('description'):
            self._current_block += attrs_dict['description']
            self._finish_block()
        elif attrs_dict.get('keywords'):
            self._current_block += attrs_dict['keywords']
            self._finish_block()
        elif attrs_dict.get('http-equiv') == 'keywords':
            self._current_block += attrs_dict['content']
            self._finish_block()
        elif attrs_dict.get('alt'):
            self._current_block += attrs_dict['alt']
            self._finish_block()


def detect_encoding(html):
    """
    Try to detect encoding in HTML code

    :param html: HTML code
    :type html: bytes
    :return: encoding code or ``None``
    :rtype: str
    """
    match = charset_re.search(html)
    if match is not None:
        return match.group(1).decode('ascii').lower()
    return None


def segment_html(html):
    """
    Extract translatable segments from a HTML document

    :param html: HTML document
    :type html: str
    :return: generator of translatable segments
    :rtype: types.GeneratorType
    """
    parser = ContentParser()
    parser.feed(html)
    for item in parser.content_list:
        # Skip <pre><code> blocks
        if pre_code_re.search(item) is None:
            for segment in sent_tokenize(item):
                if not tag_string_re.search(segment):
                    yield segment


def find_tag(tag_name, tags_stack):
    """
    Find closest opening tag in a tags stack

    Search is done from the end of the stack.

    :param tag_name: tag name
    :type tag_name: str
    :param tags_stack: tags stack
    :type tags_stack: list
    :return: opening tag index or -1
    :rtype: int
    """
    i = len(tags_stack) - 1
    for item in reversed(tags_stack):
        if tag_name == item[0]:
            return i
        i -= 1
    return -1


def add_t_tags(segment):
    """
    Add <bpt> <ept> and <it> tags to translation segment

    Unpaired open and close tags are treated as <it>

    :param segment: translation segments
    :type segment: str
    :return: tagged segment
    :rtype: str
    """
    tags_stack = []
    open_tags = []
    close_tags = []
    isolated_tags = []
    tag_id = 1
    chunks = tag_re.split(segment)
    for i, chunk in enumerate(chunks):
        open_tag_match = open_tag_re.search(chunk)
        if open_tag_match is not None:
            tag_name = open_tag_match.group(1)
            if tag_name in SELF_CLOSING_TAGS:
                isolated_tags.append((i, tag_id))
                tag_id += 1
                continue
            tags_stack.append((tag_name, i, tag_id))
            tag_id += 1
            continue
        close_tag_match = close_tag_re.search(chunk)
        if close_tag_match is not None:
            tag_name = close_tag_match.group(1)
            # If a closing tag does not have a pair in the stack
            # treat it as an isolated tag.
            open_tag_idx = find_tag(tag_name, tags_stack)
            if open_tag_idx == -1:
                isolated_tags.append((i, tag_id))
                tag_id += 1
                continue
            else:
                open_tags.append((tags_stack[open_tag_idx][1], tags_stack[open_tag_idx][2]))
                close_tags.append((i, tags_stack[open_tag_idx][2]))
                tags_stack.pop(open_tag_idx)
    for item in tags_stack:
        # Add unpaired open tags from the stack to isolated tags.
        isolated_tags.append((item[1], item[2]))
    for tag in open_tags:
        chunks[tag[0]] = '<bpt id="{}">{}</bpt>'.format(
            tag[1], escape(chunks[tag[0]])
        )
    for tag in close_tags:
        chunks[tag[0]] = '<ept id="{}">{}</ept>'.format(
            tag[1], escape(chunks[tag[0]])
        )
    for tag in isolated_tags:
        chunks[tag[0]] = '<it id="{}">{}</it>'.format(
            tag[1], escape(chunks[tag[0]])
        )
    return ''.join(chunks)


def create_skeleton(segments, html):
    """
    Create skeleton file

    :param segments: Translation segemnts
    :type segments: list
    :param html: source html document
    :type html: str
    :return: document skeleton
    :rtype: str
    """
    for i, seg in enumerate(segments, 1):
        html = html.replace(seg, '{{{{%{}%}}}}'.format(i), 1)
    return html


def create_xliff(segments, skeleton, filename, datatype='html'):
    """
    Create XLIFF 1.2 file

    :param segments: translation segments
    :type segments: list
    :param skeleton: document skeleton
    :type skeleton: str
    :param filename: document filename
    :type filename: str
    :param datatype: document datatype (html)
    :type datatype: str
    :return: XLIFF file contents
    :rtype: bytes
    """
    doc = Document()
    xliff = doc.createElement('xliff')
    xliff.setAttribute('version', '1.2')
    doc.appendChild(xliff)
    file = doc.createElement('file')
    file.setAttribute('original', filename)
    file.setAttribute('datatype', datatype)
    file.setAttribute('source-language', 'en')
    xliff.appendChild(file)
    header = doc.createElement('header')
    file.appendChild(header)
    tool = doc.createElement('tool')
    tool.setAttribute('tool-id', 'py-xliff-converter')
    tool.setAttribute('tool-name', 'Python XLIFF Converter')
    header.appendChild(tool)
    skl = doc.createElement('skl')
    header.appendChild(skl)
    internal_file = doc.createElement('internal_file')
    internal_file.setAttribute('form', 'base64')
    skl.appendChild(internal_file)
    skl_node = doc.createTextNode(
        b64encode(skeleton.encode('utf-8')).decode('ascii')
    )
    internal_file.appendChild(skl_node)
    body = doc.createElement('body')
    file.appendChild(body)
    for id_, seg in enumerate(segments, 1):
        trans_unit = doc.createElement('trans-unit')
        trans_unit.setAttribute('id', str(id_))
        trans_unit.setAttribute('xml:space', 'preserve')
        body.appendChild(trans_unit)
        source = doc.createElement('source')
        trans_unit.appendChild(source)
        tmp_seg = '<src-root>{}</src-root>'.format(add_t_tags(unescape(seg)))
        tmp_doc = parseString(tmp_seg)
        for node in tmp_doc.firstChild.childNodes:
            source.appendChild(node.cloneNode(True))
    return doc.toxml(encoding='utf-8')


def convert_html(html, filename='index.html', datatype='html'):
    """
    Convert a HTML document into XLIFF 1.2 translatable format

    :param html: HTML document
    :type html: str, bytes
    :param filename: document filename
    :type filename: str
    :param datatype: document datatype (html)
    :type datatype: str
    :return: XLIFF 1.2 document
    :rtype: bytes
    """
    if isinstance(html, bytes):
        enc = detect_encoding(html)
        if enc is None:
            enc = 'utf-8'
        html = html.decode(enc)
    segments = list(segment_html(html))
    skeleton = create_skeleton(segments, html)
    return create_xliff(segments, skeleton, filename, datatype)
