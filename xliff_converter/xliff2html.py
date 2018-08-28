"""
Converts a translated XLIFF 1.2 document back to HTML
"""

from argparse import ArgumentParser
from .html_rebuilder import rebuild_html


def parse_arguments():
    parser = ArgumentParser(
        description='Convert a XLIFF 1.2 document back to HTML'
    )
    parser.add_argument('path', nargs=1, help='Path to a XLIFF file')
    parser.add_argument(
        '-o', '--output', required=False,
        help='Output filename (default: <source filename>_<ll-CC>.<ext>)'
    )
    parser.add_argument(
        '-p', '--allow-partial',
        action='store_true', default=False,
        help='Allow to convert a partially translated XLIFF'
    )
    return parser.parse_args()


def main():
    print('Converting XLIFF 1.2 to HTML...')
    args = parse_arguments()
    with open(args.path[0], 'r', encoding='utf-8') as fo:
        xliff = fo.read()
    html_document = rebuild_html(xliff, not args.allow_partial)
    if args.output:
        html_filename = args.output
    else:
        html_filename = html_document.filename
    with open(html_filename, 'w', encoding='utf-8') as fo:
        fo.write(html_document.html)
    print('Conversion done.')
