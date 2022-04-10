import importlib

commands = {
    'apply': 'apply',
    'check': 'check',
    'import': 'import_files',
    'plan': 'plan',
    'plan_export': 'plan_export',
    'version': 'version'
    #'export':       'export_files'
}
def allowed(command):

    return command in commands
def execute(command, options, print_results=True):

    if not command in commands:
        raise ValueError("Unknown command %s" % command)

    module = importlib.import_module('.%s' % commands[command], __name__)

    return module.execute(options, print_results=print_results)
