from .. import command_system


def scabs_(*_):
    path = ''
    return path, ('sendphoto',)


scabs_command = command_system.Command()

scabs_command.keys = ['cхема']
scabs_command.description = 'Схема техникума'
scabs_command.process = scabs_
