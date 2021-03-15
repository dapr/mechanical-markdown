# Mechanical Markdown

[![codecov](https://codecov.io/gh/dapr/mechanical-markdown/branch/main/graph/badge.svg)](https://codecov.io/gh/dapr/mechanical-markdown)

If you are using markdown to create tutorials for your users, these markdown files will often be a series of shell commands that a user will copy and paste into their shell of choice, along with detailed text description of what each command is doing.

If you are regularly releasing software and having to manually verify your tutorials by copy pasting commands into a terminal every time you create a release, this is the package for you.

The mechanical-markdown package is a Python library and corresponding shell script that allow you to run annotated markdown tutorials in an automated fashion. It will execute your markdown tutorials and verify the output according to expected stdout/stderr that you can embed directly into your markdown tutorials. 

# Installing 

This package requires a working python3 environment. You can install it using pip:

```bash
pip install mechanical-markdown
```

This will install the Python module, and create the ```mm.py``` CLI script.

# Quick Start

Check out the [examples](./examples) for some quick and easy examples.

# Usage

## CLI

A command line utility called ```mm.py``` is included with this package.

```bash
% mm.py --help
usage: mm.py [-h] [--dry-run] [--manual] [--shell SHELL_CMD] markdown_file

Auto validate markdown documentation

positional arguments:
  markdown_file

optional arguments:
  -h, --help            show this help message and exit
  --dry-run, -d         Print out the commands we would run based on markdown_file
  --manual, -m          If your markdown_file contains manual validation steps, pause for user input
  --shell SHELL_CMD, -s SHELL_CMD
                        Specify a different shell to use
```

## API

Creating a MechanicalMarkdown instance from a string which contains a markdown document:
```python
from mechanical_markdown import MechanicalMarkdown

mm = MechanicalMarkdown(markdown_string)
```

MechanicalMarkdown methods 

```python
# Returns a string describing the commands that would be run
output = mm.dryrun(default_shell='bash -c')
print(ouput)

# Run the commands in the order they were specified and return a boolean for succes or failure
# Also returns a report summarizing what was run and stdout/sterr for each command
success, report = exectute_steps(manual, default_shell='bash -c', validate_links=False, link_retries=3)
print(report)


```

# Contributing

Issues and contributions are always welcome! Please make sure your submissions have appropriate unit tests (see [tests](tests/)).

This project was created to support [dapr/quickstarts](https://github.com/dapr/quickstarts). We're sharing it with the hope that it might be as usefull for somebody else as it was for us.
