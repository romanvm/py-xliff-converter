"""
Converts a HTML document into translatable XLIFF 1.2 format
"""

import os
from argparse import ArgumentParser
from .html_parser import convert_html


def parse_arguments():
    parser = ArgumentParser(
        description='Converts a HTML file into XLIFF 1.2'
    )
    parser.add_argument('path', nargs=1, help='Path to a HTML file')
    parser.add_argument('-o', '--output',
                        help='Output filename (default: <scource_filename>.xlf)',
                        required=False)
    parser.add_argument('-d', '--datatype', default='html',
                        help='XLIFF data type (default: "html")')
    return parser.parse_args()


def main():
    print('Converting HTML to XLIFF 1.2...')
    args = parse_arguments()
    with open(args.path[0], 'rb') as fo:
        html = fo.read()
    html_filename = os.path.basename(args.path[0])
    xliff = convert_html(html, html_filename, args.datatype)
    if args.output:
        xliff_filename = args.output
    else:
        xliff_filename = os.path.splitext(html_filename)[0] + '.xlf'
    with open(xliff_filename, 'wb') as fo:
        fo.write(xliff)
    print('Conversion done.')
