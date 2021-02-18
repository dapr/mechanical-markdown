
"""
Copyright (c) Microsoft Corporation.
Licensed under the MIT License.
"""

import mechanical_markdown

import sys
import argparse


def main():
    parse_args = argparse.ArgumentParser(description='Auto validate markdown documentation')
    group = parse_args.add_argument_group()
    group.add_argument('markdown_file',
                       metavar='MARKDOWN_FILE',
                       nargs='?',
                       type=argparse.FileType('r'),
                       help="The annotated markdown file to run/execute")
    group.add_argument('--dry-run', '-d',
                       dest='dry_run',
                       action='store_true',
                       help='Print out the commands we would run based on markdown_file')
    group.add_argument('--manual', '-m',
                       dest='manual',
                       action='store_true',
                       help='If your markdown_file contains manual validation steps, pause for user input')
    group.add_argument('--shell', '-s',
                       dest='shell_cmd',
                       default='bash -c',
                       help='Specify a different shell to use')
    parse_args.add_argument('--version',
                            dest='print_version',
                            action='store_true',
                            help='Print version and exit')
    parse_args.add_argument('--validate-links', '-l',
                            dest='validate_links',
                            default=False,
                            action='store_true',
                            help='Check for broken links to external URLs')
    args = parse_args.parse_args()

    if args.print_version:
        parse_args.exit(status=0, message='{} version:\nv{}'.format(parse_args.prog, mechanical_markdown.__version__))

    if args.markdown_file is None:
        parse_args.error('You must provide exactly one markdown file to operate on.\n\
                         Try "{} -h" for more info'.format(parse_args.prog))

    body = args.markdown_file.read()
    r = mechanical_markdown.MechanicalMarkdown(body)
    success = True

    if args.dry_run:
        print("Would run the following validation steps:")
        print(r.dryrun(args.shell_cmd))
        sys.exit(0)

    success, report = r.exectute_steps(args.manual, args.shell_cmd, validate_links=args.validate_links)
    print(report)
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
