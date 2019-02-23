import logging
from os import path
from cs251tk.common import chdir
from cs251tk.student.markdownify import markdownify


def record(student, *, specs, to_record, basedir, debug, interact, web, ci, skip_web_compile):
    recordings = []
    if not to_record:
        return recordings

    directory = student if not ci else '.'
    with chdir(directory):
        for one_to_record in to_record:
            logging.debug("Recording  {}'s {}".format(student, one_to_record))
            if path.exists(one_to_record):
                with chdir(one_to_record):
                    recording = markdownify(one_to_record,
                                            username=student,
                                            spec=specs[one_to_record],
                                            basedir=basedir,
                                            debug=debug,
                                            interact=interact,
                                            student=student,
                                            web=web,
                                            ci=ci,
                                            skip_web_compile=skip_web_compile)
            else:
                recording = {
                    'spec': one_to_record,
                    'student': student,
                    'first_submit': "",
                    'warnings': {'no submission': True},
                }

            recordings.append(recording)

    return recordings
