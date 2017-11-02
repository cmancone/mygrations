import importlib

commands = {
    'import':       'import_files',
    'check':        'check',
    'plan':         'plan',
    'plan_export':  'plan_export'
    #'export':       'export_files'
}

def allowed( command ):

    return command in commands

def execute( command, options ):

    if not command in commands:
        raise ValueError( "Unknown command %s" % command )

    module = importlib.import_module( '.%s' % commands[command], __name__ )

    module.execute( options )
