from .. import command_system
from .. import sql as sqlapi


def mailing_(user_id, _):
    with sqlapi.mysqlapiwrapper() as db:
        current_status = bool(db.userdata.get_mailing_status())

        db.userdata.update_mailing_status(user_id, int(not current_status))

        message = '❌ Рассылка отключена' if current_status else '✅ Рассылка включена'
        return message, ('text',)


mailing_command = command_system.Command()

mailing_command.keys = ['рассылка']
mailing_command.description = 'Включает и выключает рассылку новых замен . Рассылка будет производиться ' \
                              'по сохраненной группе и если замены для вашей группы есть.'
mailing_command.process = mailing_
