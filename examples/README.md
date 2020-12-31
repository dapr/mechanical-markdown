
# Mechanical markdown by example

## Prerequisites

Be sure you have mechanical markdown [installed](../README.md#installing) and that the mm.py utility is in your $PATH. These examples were written with basic bash commands in mind, but any bash like shell should work. See [Shells](#shells) below for alternatives.

## Using this guide

All markdown files in examples/ (including this one!) are annotetated and can be executed and validated with:

```bash
mm.py filename.md
```

This guide automatically executed as part of this project's continuous integration pipeline. It serves as both user guide and integration test suite for this package. If you use it run through it, hopefully you will see what a powerful concept self executing documentation can be.

## How mechanical-markdown works

One of the beautiful features of markdown is that it is both human and machine readable. A human can read a user guide and copy paste steps into their terminal. A machine can do the same and do some extra validation on the steps to make sure they executed correctly. Also, most markdown engines support embedded HTML comments ```<!-- -->```. We can use these HTML comments to embed extra information to tell our validation program what output we expect from a command. The ```mm.py``` utility will automatically extract this information, allong with the commands to execute from our markdown files.

## Annotation format

To tell mechanical-markdown what parts of your document need to be executed as code, you must add an HTML comment that begins with the token ```STEP```. After this token, mechanical-markdown will interpret the rest of the comment as a yaml document with instructions for how the code blocks should be executed and verified. All fields in this yaml document are optional. Finish the comment to denote then end of the yaml document and the beginning of your exectuable markdown code. Finally, finish with an html comment like this: ```<!-- END_STEP -->``` to denote the end of a step. Let's look at a basic example:

    <!-- STEP 
    name: Hello World
    expected_stdout_lines:
      - "Hello World!"
    -->
    
    You can use regular markdown anywhere during a step. It will be ignored. Only denoted as bash or sh will be executed.
    
    ```bash
    echo "Hello World!"
    ```
    
    This python code block will not be executed:
    
    ```python
    print("This python script will not be run")
    ```
        
    <!-- END_STEP -->
    
    This unannotated command will not be run:
    
    ```bash
    echo "A command that will not be run"
    ```

Here's how the above will render in your markdown interpreter.

----

<!-- STEP 
name: Hello World
expected_stdout_lines:
  - "Hello World!"
-->

You can use regular markdown anywhere during a step. It will be ignored. Only code blocks denoted as bash or sh will be executed.

```bash
echo "Hello World!"
```

This python code block will not be executed:

```python
print("This python script will not be run")
```

<!-- END_STEP -->
    
This unannotated command will not be run:

```bash
echo "A command that will not be run"
```

----

Let's breakdown what this embedded yaml annotation is doing. There are two fields in our yaml document ```name``` and ```expected_stdout_lines```. The name field simply provides a name for the step that will be printed to the report that mm.py generates. The expected_stdout_lines field is actually telling mm.py what it should be looking for from stdout when it executes our code block(s). For more on this, checkout [io.md](io.md). 

## CLI

### Help
For a list of options:

<!-- STEP 
name: CLI help
expected_stdout_lines:
  - "usage: mm.py [-h] [--dry-run] [--manual] [--shell SHELL_CMD] [--version]"
  - "             [MARKDOWN_FILE]"
  - "Auto validate markdown documentation"
  - "optional arguments:"
  - "  -h, --help            show this help message and exit"
  - "  --version, -v         Print version and exit"
  - "  MARKDOWN_FILE         The annotated markdown file to run/execute"
  - "  --dry-run, -d         Print out the commands we would run based on"
  - "                        markdown_file"
  - "  --manual, -m          If your markdown_file contains manual validation"
  - "                        steps, pause for user input"
  - "  --shell SHELL_CMD, -s SHELL_CMD"
  - "                        Specify a different shell to use"
-->

```bash
mm.py --help
```

<!-- END_STEP -->

```
usage: mm.py [-h] [--dry-run] [--manual] [--shell SHELL_CMD] [--version]
             [MARKDOWN_FILE]

Auto validate markdown documentation

optional arguments:
  -h, --help            show this help message and exit
  --version, -v         Print version and exit

  MARKDOWN_FILE         The annotated markdown file to run/execute
  --dry-run, -d         Print out the commands we would run based on
                        markdown_file
  --manual, -m          If your markdown_file contains manual validation
                        steps, pause for user input
  --shell SHELL_CMD, -s SHELL_CMD
                        Specify a different shell to use
```

### Version

<!-- STEP 
name: CLI version
expected_stderr_lines:
  - "mm.py version:"
-->

```bash
mm.py --version
```

<!-- END_STEP -->

### Dry Run
You can do a dry run to print out exactly what commands will be run using the '-d' flag.

<!-- STEP 
name: CLI dry run
expected_stdout_lines:
  - "Would run the following validation steps:"
  - "Step: Hello World"
  - "Step: CLI help"
  - "Step: CLI dry run"
  - "Step: Pause for manual validation"
-->

```bash
mm.py -d README.md
```

<!-- END_STEP -->

This will print out all the steps that would be run, without actually running them. Output looks something like this

```
Would run the following validation steps:
Step: Hello World
	commands to run with 'bash -c':
		`echo "Hello World!"`
	Expected stdout:
		Hello World!
	Expected stderr:

...
```

### Run and Validate

Now you can run the steps and verify the output:

```bash
mm.py start.md
```

The script will parse the markdown, execute the annotated commands, and then print a report like this:

```
Running shell 'bash -c' with command: `echo "Hello World!"`
Running shell 'bash -c' with command: `mm.py --help`
Running shell 'bash -c' with command: `mm.py -d README.md`

Step: Hello World
	command: `echo "Hello World!"`
	return_code: 0
	Expected stdout:
		Hello World!
	Actual stdout:
		Hello World!
		
	Expected stderr:
	Actual stderr:
...
```

If anything unexpected happens, you will get report
of what went wrong, and mm.py will return non-zero.

### Shells

The default shell used to execute scripts is ```bash -c```. You can use a different shell interpreter by specifying one via the cli:

```bash
mm.py -s 'zsh -c' README.md
```

### Manual validation

You can add manual validation steps to your document. A manual validation step is just a pause message to allow the user to take some manual step like opening a browser. These steps normally get ignored, as ```mm.py``` is designed to do automated validation by default. If you run the following, it will enable mm.py to pause for user input. (View raw markdown for an example of what a manual_pause_message looks like):


<!-- STEP
name: Pause for manual validation
manual_pause_message: "Waiting for user input"
-->

<!-- We will pause here and print the above message when mm.py is run with '-m'. Otherwise, this step does nothing -->

<!-- END_STEP -->

```bash
mm.py -m README.md 
```

# More examples:

- For more details on checking stdout/stderr: [I/O Validation](io.md)
- For more details on setting up the execution environment: [Environment Variables](env.md) and [Working Directory](working_dir.md)
- For controlling timeouts, backgrounding, and adding delay between steps: [Sleeping, Timeouts, and Backgrounding](background.md)
