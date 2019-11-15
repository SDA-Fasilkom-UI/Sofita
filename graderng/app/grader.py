import os

from filebrowser.sites import site

from app.sandbox import JavaSandbox


def grade_submission(sub):
    try:
        sandbox = JavaSandbox()
        sandbox.init_isolate()

        grade, feedback = compile_and_run(sandbox, sub)
        return grade, feedback

    finally:
        sandbox.cleanup_isolate()


def compile_and_run(sandbox, sub):

    sandbox.add_file_from_string(sub.content, sub.filename)

    status_code, error = sandbox.compile(sub.filename)

    if status_code != 0:
        return 0, convert_compilation_error(error)

    problems_path = get_problems_path()
    cases_path = os.path.join(problems_path, sub.problem_name, "cases")

    if not os.path.isdir(cases_path):
        return 0, directory_not_found_error()

    sandbox.add_dir(cases_path)

    dirs = os.listdir(cases_path)
    num_files = len(dirs)
    tc_len = num_files - num_files // 2

    valid = True
    verdict_list = []

    filename, _ = os.path.splitext(sub.filename)
    time_limit = sub.time_limit
    memory_limit = sub.memory_limit

    for i in range(1, tc_len + 1):
        in_filename = "{}.in".format(i)
        out_filename = "{}.out".format(i)
        input_path = os.path.join(cases_path, in_filename)
        output_path = os.path.join(cases_path, out_filename)

        if (in_filename not in dirs) or (out_filename not in dirs):
            valid = False
            break

        status, time = sandbox.run_testcase(
            filename,
            time_limit,
            memory_limit,
            input_path,
            output_path
        )
        verdict_list.append((status, float(time)))

    if not valid:
        return 0, directory_not_valid_error()

    score = [x for x in verdict_list if x[0] == "AC"]
    grade = len(score) * 100 / len(verdict_list)

    return grade, convert_verdict_result(grade, verdict_list)


def get_problems_path():
    location = site.storage.location
    directory = site.directory
    return os.path.join(location, directory)


def directory_not_valid_error():
    html = "<p><b>Error | Attempt Grade: 0</b></p>"
    html += "<p>Problem directory is not valid, contact assistant</p>"
    return html


def directory_not_found_error():
    html = "<p><b>Error | Attempt Grade: 0</b></p>"
    html += "<p>Problem directory is not found, contact assistant</p>"
    return html


def convert_compilation_error(error):
    html = "<p><b>Compile Error | Attempt Grade: 0</b></p>"
    html += "<p><b>First 20 Lines Compilation Output:</b></p>"
    html += '<table style="border: 1px solid black"><tr><td><tt>'
    for line in error.split("\n")[: 20]:
        html += "{} <br />".format(line)
    html += "</tt></td></tr></table>"
    return html


def convert_verdict_result(grade, verdict_list):
    html = "<p><b>Attempt Grade: {:.2f}</b></p>".format(grade)
    html += "<p><b>Summary:</b></p>"
    html += '<table style="border-collapse: collapse">'

    ln = len(verdict_list)
    hf = ln - ln // 2

    for i in range(hf):
        content1 = "{}: {} ({:.3f}s)".format(
            i + 1, verdict_list[i][0], verdict_list[i][1])

        content2 = ""
        if hf + i < ln:
            content2 = "{}: {} ({:.3f}s)".format(
                hf + i + 1, verdict_list[hf+i][0], verdict_list[hf+i][1])

        html += "<tr>"
        html += '<td style="border: 1px solid black; text-align=left; padding: 4px;"><tt>{}</tt></td>'.format(
            content1)
        html += '<td style="border: 1px solid black; text-align=left; padding: 4px;"><tt>{}</tt></td>'.format(
            content2)
        html += "</tr>"

    html += "</table><br />"
    html += "<p><tt>AC : Accepted<br />WA : Wrong Answer<br />RTE: Runtime Error<br />TLE: Time Limit Exceeded<br />XX : Unknown Error</tt></p>"
    return html
