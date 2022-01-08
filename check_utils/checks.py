#!/usr/bin/python3 -u
# Copyright 2020 Darius Neatu (neatudarius@gmail.com)

import os
import pathlib
import subprocess
import time

from .parser import get_config
from .utils import *


def update_grade_vmr(config, points, reason):
    if not config.grade_vmr:
        config.grade_vmr = [
            '##### autogenerated output - default grade 100p',
        ]

    config.grade_vmr.append('#####{}: {}'.format(points, reason))


def update_grade(config, points):
    assert config is not None

    config.grade += points
    if points < 0:
        log('{} points penalty applied!\n'.format(points))


def check_deps(config):
    assert config is not None

    log('+++++ check_deps ...')
    deps = config.deps

    child = subprocess.run(['uname', '-a', ], shell=False,
                           stdin=subprocess.DEVNULL,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.DEVNULL,
                           )
    assert child.returncode == 0, child.stderr
    log('{:20s} - Linux'.format('system'))
    log('\t config: {}'.format(extract_stdout(child).split('\n')[0]))

    for dep in deps:
        child = subprocess.run(['which', dep, ], shell=False,
                               stdin=subprocess.DEVNULL,
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL,
                               )
        if child.returncode != 0:
            log('{} needs to be installed!'.format(dep))
            return child.returncode
        log('{:20s} - installed'.format(dep))

        child = subprocess.run([dep, '--version', ], shell=False,
                               stdin=subprocess.DEVNULL,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               )
        if child.returncode != 0:
            log(extract_stderr(child))
            return child.returncode
        log('\tversion: {}'.format(extract_stdout(child).split('\n')[0]))

    log('----- check_deps\n')
    return 0


def make_build(config):
    assert config is not None

    log('+++++ make_build ...')
    makefile = 'Makefile'
    if not pathlib.Path(makefile).is_file():
        reason = '{} is missing!'.format(makefile)
        log(reason)
        update_grade_vmr(config, -100, reason)
        return -1

    try:
        child = subprocess.run(['make', 'build', ], shell=False,
                               stdin=subprocess.DEVNULL,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               )
    except Exception as e:
        log('----- make_build - UPS: {}'.format(str(e)))
        unindent_log()
        return -1

    if child.returncode != 0:
        reason = 'Compile ERRORS found. STOP. Please fix them.'
        log(reason)
        log('{}'.format(extract_stderr(child)))

        update_grade_vmr(config, -100, reason)
        return child.returncode

    if config.penalty_warnings and config.penalty_warnings > 0:
        warnings = child.stderr.decode("utf-8")
        if len(warnings) > 0:
            reason = 'WARNINGS found. Please fix them.'
            log(reason)
            log('{}'.format(warnings))

            update_grade(config, -config.penalty_warnings)
            update_grade_vmr(config, -config.penalty_warnings, reason)

    for task in config.tasks:
        if not pathlib.Path(task.id).is_file() or not os.access(os.path.join('.', task.id), os.X_OK):
            log('[WARNING] Executable \'{}\' not found!'.format(task.id))

    log('----- make_build')
    return 0


def make_clean(config):
    assert config is not None

    log('+++++ make_clean ...')

    try:
        child = subprocess.run(['make', 'clean', ], shell=False,
                               stdin=subprocess.DEVNULL,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               )
    except Exception as e:
        log('----- make_clean - UPS: {}'.format(str(e)))
        unindent_log()
        return -1

    if child.returncode != 0:
        reason = '\'make clean\' failed. Fix it!'
        log(reason)
        update_grade(config, -config.grade)
        update_grade_vmr(config, -config.grade, reason)

        log('{}'.format(extract_stdout(child)))
        return child.returncode

    log('----- make_clean')
    return 0


def check_readme(config):
    if config.penalty_readme <= 0:
        return 0  # check not enable

    log('+++++ running check_readme ({:g}p) ...'.format(config.penalty_readme))

    readme = pathlib.Path('README')
    readme_points = 0
    if not readme.is_file():
        reason = '\'{}\' is missing!'.format(readme.name)
        log(reason)
        update_grade_vmr(config, -config.penalty_readme, reason)
    elif readme.stat().st_size == 0:
        reason = 'Empty \'{}\'!'.format(readme.name)
        log(reason)
        update_grade_vmr(config, -config.penalty_readme, reason)
    elif readme.stat().st_size < 64:
        reason = '\'{}\' too short! Nice try! :p'.format(readme.name)
        log(reason)
        update_grade_vmr(config, -config.penalty_readme, reason)
    else:
        log('Found \'{}\' ... Final points are given after manual grading!'.format(
            readme.name))
        readme_points = config.penalty_readme

    update_grade(config, readme_points)
    log('----- running check_readme - grade {:g}/{:g}\n'.format(
        readme_points, config.penalty_readme))
    return 0


def check_style(config):
    if config.coding_style <= 0:
        return 0  # check not enable

    log('+++++ running check_style ({:g}p)...'.format(config.coding_style))

    cmd = './cs/cs.sh . 2>&1'

    try:
        child = subprocess.run(cmd, shell=True,
                               stdin=subprocess.DEVNULL,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL,
                               )
    except Exception as e:
        log('----- running check_style - UPS: {}'.format(str(e)))
        unindent_log()
        return -1

    if child.returncode != 0 or len(extract_stdout(child)) != 0:
        coding_style_grade = 0

        reason = 'Coding style errors automatically detected.'
        update_grade_vmr(config, -config.coding_style, reason)
    else:
        coding_style_grade = (1.0 * max(min(config.grade, 70), 0) /
                              (config.tests_points - 20)) * config.coding_style
        if coding_style_grade < config.coding_style:

            reason = 'No coding style errors automatically detected (tests points {}/{})'.format(config.grade, config.tests_points)
            update_grade_vmr(config, coding_style_grade - config.coding_style, reason)
        else:
            reason = 'No coding style errors automatically detected. Final points are given after manual grading.'
            update_grade_vmr(config, 0, reason)

    should_play_sound = config.grade == config.tests_points and coding_style_grade < config.coding_style
    config.grade += coding_style_grade

    log('{}\n'.format(extract_stdout(child)))

    if not 'ONLINE_JUDGE' in os.environ and should_play_sound:
        os.system('./check_utils/.surprise/play_cs.sh')

    # log('Note: The coding style points are uniformly distributed per task.')
    log('----- running check_style - grade {:g}/{:g}\n'.format(
        coding_style_grade, config.coding_style))

    return 0


def run_test(task, test, use_valgrind=False, ):
    indent_log()
    stage_name = 'test' if not use_valgrind else 'valgrind'
    log('running {:10s} ...'.format(stage_name))

    cmd = None
    if not use_valgrind:
        # man timeout: 124 if command times out
        expected_error_code = 124
        cmd = f"make run_{task.id}"
    else:
        # choose an error to be returned by valgrind
        expected_error_code = 69

        cmd = 'valgrind '              \
            '--leak-check=full '       \
            '--show-reachable=no '     \
            '--show-leak-kinds=all '   \
            '--error-exitcode={} '     \
            '--log-file={} '           \
            '{}'.format(expected_error_code, test.log_valgrind, task.binary)

    set_mem_bytes(task.memory)

    try:
        child = subprocess.run(['make', '-s', f'run_{task.id}'], shell=False if not use_valgrind else True,
                               stdin=open(
                                   test.input, 'r') if task.use_stdin else subprocess.DEVNULL,
                               stdout=open(
                                   test.output, 'w') if task.use_stdout else subprocess.DEVNULL,
                               stderr=subprocess.PIPE,
                               timeout=task.timeout if not use_valgrind else 500,
                               cwd=os.getcwd(),
                               preexec_fn=limit_process_memory if task.memory and not use_valgrind else None,
                               )
    except subprocess.TimeoutExpired as e:
        log_replace('running {:10s} - TLE: {}'.format(stage_name, str(e)))
        unindent_log()
        return -1
    except Exception as e:
        log_replace('running {:10s} - UPS: {}'.format(stage_name, str(e)))
        unindent_log()
        return -1

    if child.returncode != 0:
        if not use_valgrind:
            log_replace(
                'running {:10s} - UPS: exit code = {}'.format(stage_name, child.returncode))
        elif child.returncode == expected_error_code:
            log_replace('running {:10s} - MEM_UPS'.format(stage_name))

        unindent_log()
        return child.returncode

    log_replace('running {:10s} - OK'.format(stage_name))
    unindent_log()
    return 0

def run_test_with_env_deps(task, test, use_valgrind=False, ):
    if task.use_env_deps:
        backup_cwd = os.getcwd()

        in_deps = '{}/in'.format(test.deps)
        out_deps = '{}/out'.format(test.deps)

        os.system('rm -rf {}/* 2>&1 1>/dev/null'.format(out_deps))
        os.system('mkdir -p {} 2>&1 1>/dev/null'.format(out_deps))
        os.system('cp {}/* {}'.format(in_deps, out_deps))

        os.chdir(out_deps)
        # log('cwd = {}'.format(os.getcwd()))


    ret = run_test(task, test, use_valgrind)

    if task.use_env_deps:
        os.chdir(backup_cwd)

    return ret

def check_test(task, test):
    indent_log()
    stage_name = 'check'
    log('running {:10s} ...'.format(stage_name))
    cmd = '{} {} {} {} {}'.format(
        task.grader, test.input, test.output, test.ref, test.points)

    grade_file = '.check.grade'
    if pathlib.Path(grade_file).is_file():
        pathlib.Path(grade_file).unlink()

    try:
        child = subprocess.run(cmd, shell=True,
                               stdin=subprocess.DEVNULL,
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.PIPE,
                               )
    except Exception as e:
        log_replace('running {:10s} - UPS: {}'.format(stage_name, str(e)))
        unindent_log()
        return -1

    if child.returncode != 0:
        log_replace(
            'running {:10s} - WA: {}'.format(stage_name, extract_stderr(child)))
        unindent_log()
        return child.returncode

    assert pathlib.Path(grade_file).is_file(), grade_file
    test.grade = 0
    with open(grade_file, 'r') as f:
        test.grade = float(f.readlines()[0].rstrip())
    pathlib.Path(grade_file).unlink()

    warnings = extract_stderr(child)
    log_replace('running {:10s} - OK{}'.format(stage_name, (': {}'.format(warnings)
                                                            if len(warnings) > 0 else '')))
    unindent_log()
    return 0


def run_task(config, task):
    indent_log()
    log('+++++ running task {} ({:g}p) ...\n'.format(task.id, task.points))

    for test in task.tests:
        indent_log()
        log('+++++ running test {}'.format(test.id))

        stages = [
            lambda: run_test_with_env_deps(task, test),
            lambda: check_test(task, test),
        ]

        if task.use_valgrind or test.use_valgrind:
            stages.append(lambda: run_test_with_env_deps(task, test, use_valgrind=True))

        code = 0
        for stage in stages:
            code, seconds = run_and_measure(stage)

            indent_log(2)
            log('stage time: {}'.format(seconds))
            unindent_log(2)

            if code != 0:
                break

        if code != 0:
            test.grade = 0

        task.grade += test.grade
        log('----- running test {} - grade {:g}/{:g}\n'.format(test.id,
                                                               test.grade, test.points))
        unindent_log()

    log('----- running task {} - grade {:g}/{:g}\n'.format(task.id,
                                                           task.grade, task.points))
    unindent_log()

    if  task.grade < task.points:
        update_grade_vmr(config, task.grade - task.points, 'Failed tests for task {}'.format(task.id))

    return 0


def run_tasks(config):
    log('+++++ running all tasks')

    if not 'ONLINE_JUDGE' in os.environ:
        os.system('./check_utils/.surprise/play_testing.sh &')
        time.sleep(1)
        log('\n\n\n')
        sys.stdout.flush()

    for task in config.tasks:
        run_task(config, task)
        config.grade += task.grade

    if not 'ONLINE_JUDGE' in os.environ:
        os.system('kill $(pidof mpg123) 2>&1 >/dev/null')

    log('----- running all tasks\n')
    return 0


def print_grade_vmr(config):
    if 'ONLINE_JUDGE' in os.environ and config.grade_vmr:
        log('+++++ generating grade.vmr')

        with open('grade.vmr', 'w') as grade_vmr:
            for line in config.grade_vmr:
                log('{}'.format(line))
                grade_vmr.write('{}\n'.format(line))

        log('----- genrating grade.vmr')


def checker_run():
    config = get_config()
    assert config is not None

    checks = [
        lambda: check_deps(config),
        lambda: make_build(config),
        lambda: run_tasks(config) or config.grade == 0,
        lambda: check_style(config),
        lambda: check_readme(config),
        lambda: make_clean(config),
        lambda: print_grade_vmr(config),
    ]

    for check in checks:
        ret = check()
        if ret != 0:
            break

    # don't give negative grades
    config.grade = config.grade if config.grade > 0 else 0

    log('\n\t\t\tFinal grade: {:g}'.format(config.grade))
    log('TOTAL: {:g}/100'.format(config.grade))

    if not 'ONLINE_JUDGE' in os.environ and config.grade >= 100:
        os.system('./check_utils/.surprise/play_final.sh')
