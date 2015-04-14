#!/usr/bin/env python3

import sys
import os
from textwrap import indent
from .flatten import flatten
from .run_command import run
from .run_file import run_file

def indent4(string):
	return indent(string, '    ')

def markdownify(hw_number, username, spec, output_type=None, to=None):
	cwd = os.getcwd()
	results = []

	for input, contents in spec.get('inputs', {}).items():
		with open(cwd + '/' + input, 'w') as outfile:
			outfile.write(contents)

	files = [(filename, steps) for file in spec['files'] for filename, steps in file.items()]

	for file, steps in files:
		steps = steps if type(steps) is list else [steps]

		file_loc = cwd + '/' + file
		output = []

		header = '### ' + file

		output.extend([header, '\n'])
		file_status, file_contents = run(['cat', file])

		if file_status:
			output.append('**file %s does not exist**\n' % file)
			output.append('`ls .` says that these files exist:\n')
			output.append(indent4('\n'.join(os.listdir('.'))))
			results.append('\n'.join(output))
			continue


		output.extend(['**contents of %s**\n' % (file), indent4(file_contents)])
		output.append('\n')

		any_step_failed = False
		no_test = False
		for step in steps:
			if step:
				command = step.replace('$@', file)
				status, compilation = run(command.split())
				if status:
					any_step_failed = True
					break

				if compilation:
					warnings_header = '**warnings: `%s`**' % (command)
					output.extend([warnings_header, indent4(compilation)])
				else:
					warnings_header = '**no warnings: `%s`**' % (command)
					output.extend([warnings_header])

				output.append('\n')
			else:
				no_test = True
				break

		if not steps or any_step_failed or no_test:
			results.append('\n'.join(output))
			continue

		inputs = spec.get('inputs', {})

		tests = spec['tests'].get(file, [])
		tests = tests if type(tests) is list else [tests]

		for test in tests:
			test = test.replace('$@', file)
			output.append('**results of %s**\n' % (file))
			if os.path.exists(file_loc):
				if any([input in test for input in inputs]):
					for input, contents in inputs.items():
						status, result = run_file(file_loc + '.exec', input=contents)
						output.extend(["`%s`\n" % test, indent4(result)])
				else:
					status, result = run_file(file_loc + '.exec')
					output.extend(["`%s`\n" % test, indent4(result)])
			else:
				output.append('%s could not be found.\n' % file)

			output.append('\n')

		output.extend(["\n\n"])

		results.append('\n'.join(output))

	[run(['rm', '-f', file + '.exec']) for file, steps in files]
	[os.remove(cwd + '/' + input) for input in spec.get('inputs', {})]

	return '# %s — %s \n%s' % (
		hw_number,
		username,
		''.join(results))


if __name__ == '__main__':
	hw = sys.argv[1]
	user = sys.argv[2]
	print(markdownify(hw, user))
