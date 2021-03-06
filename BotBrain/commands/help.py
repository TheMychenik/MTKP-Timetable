from .. import command_system


def help_(*_):
    message = ''
    for command in command_system.command_list:
        message += f'[{command.keys[0].capitalize()}] - {command.description}\n\n'
    return message, ('text',)


help_command = command_system.Command()

help_command.keys = ['помощь', 'начать', '?']
help_command.description = 'Выведу список команд c описанием.'
help_command.process = help_
