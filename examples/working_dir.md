# Working directory example

## Using this example
To see a summary of what commands will be run:

```bash
mm.py -d env.md
```

To run this file and validate the expected output:

```bash
mm.py
```

Be sure to checkout the raw version of this file to see the annotations.

> **Note:** This example requires that the current working directory be writable

## Changing the working directory

The current working directory of the scripts will default to whatever the working directory the mm.py utility was called with. You can always change the working directory using a shell command, but as with setting environment variables, it will only remain to the end of the code block:

<!-- STEP 
name: Default working directory
expected_stdout_lines:
  - file contents
  - File Not Found
-->

```bash
pwd
mkdir working_dir_test
cd working_dir_test
pwd
echo "file contents" > test_file
cat test_file
```

The next code block will revert back to the default working directory:
 
```bash
pwd
cat test_file || echo "File Not Found"
```

<!-- END_STEP -->

Adding the ```working_dir``` directive to your step annotations will change the default working directory for the duration of the step. 

<!-- STEP 
name: Custom default working directory
working_dir: working_dir_test
expected_stdout_lines:
  - file contents
  - file contents
-->
 
```bash
pwd
cat test_file || echo "File Not Found"
cd ..
pwd
```

Other code blocks will revert back to the custom default within this step:

```bash
pwd
cat test_file || echo "File Not Found"
rm -v test_file
cd ..
rmdir working_dir_test
```

<!-- END_STEP -->

# Navigation

* Back to [Environment Variables](env.md)
* On to [Sleeping, Timeouts, and Backgrounding](background.md)
