from mechanical_markdown import MechanicalMarkdown

import sys
import argparse


def main():
    parse_args = argparse.ArgumentParser(description='Auto validate markdown documentation')
    parse_args.add_argument('markdown_file', metavar='markdown_file', nargs=1, type=argparse.FileType('r'))
    parse_args.add_argument('--dry-run', '-d',
                            dest='dry_run',
                            action='store_true',
                            help='Print out the commands we would run based on markdown_file')
    parse_args.add_argument('--manual', '-m',
                            dest='manual',
                            action='store_true',
                            help='If your markdown_file contains manual validation steps, pause for user input')
    parse_args.add_argument('--shell', '-s',
                            dest='shell_cmd',
                            default='bash -c',
                            help='Specify a different shell to use')
    args = parse_args.parse_args()

    body = args.markdown_file[0].read()
    r = MechanicalMarkdown(body)
    success = True

    if args.dry_run:
        print("Would run the following validation steps:")
        print(r.dryrun(args.shell_cmd))
        sys.exit(0)

    success, report = r.exectute_steps(args.manual, args.shell_cmd)
    print(report)
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
