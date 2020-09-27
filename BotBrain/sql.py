import mysql.connector

from settings import sqldata


class __connection:
    def __enter__(self):
        self.conn = mysql.connector.connect(host=sqldata['sqlhost'],
                                            database=sqldata['sqldatabase'],
                                            user=sqldata['sqluser'],
                                            password=sqldata['sqlpassword'])
        self.cursor = self.conn.cursor(buffered=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.cursor.close()
        except:
            pass
        try:
            self.conn.close()
        except:
            pass


class mysqlapiwrapper(__connection):
    def __init__(self):
        super().__init__()
        self.tablename = None

    @property
    def sysdata(self):
        self.tablename = 'sysdata'
        return self

    @property
    def userdata(self):
        self.tablename = 'userdata'
        return self

    @property
    def changes(self):
        self.tablename = 'changes'
        return self

    @property
    def schedule(self):
        self.tablename = 'schedule'
        return self

    # ------------------------------------------------------------------------------------------------------------------
    #                                          sysdata
    # ------------------------------------------------------------------------------------------------------------------

    def get_changes_date(self):
        self.cursor.execute(f"SELECT changesdate FROM {self.tablename};")
        date = self.cursor.fetchone()[0]
        return date

    def update_changes_date(self, date):
        self.cursor.execute(f"UPDATE {self.tablename} SET changesdate='{date}';")
        self.conn.commit()

    def get_changes_last_url(self):
        self.cursor.execute(f"SELECT changeslasturl FROM {self.tablename};")
        url = self.cursor.fetchone()[0]
        return url

    def update_changes_last_url(self, url):
        self.cursor.execute(f"UPDATE {self.tablename} SET changeslasturl='{url}';")
        self.conn.commit()

    def get_schedule_last_url(self):
        self.cursor.execute(f"SELECT schedulelasturl FROM {self.tablename};")
        url = self.cursor.fetchone()[0]
        return url

    def update_schedule_last_url(self, url):
        self.cursor.execute(f"UPDATE {self.tablename} SET schedulelasturl='{url}';")
        self.conn.commit()

    # ------------------------------------------------------------------------------------------------------------------
    #                                          userdata
    # ------------------------------------------------------------------------------------------------------------------
    def get_saved_group(self, user_id):
        try:
            self.cursor.execute(f"SELECT savedgroup FROM userdata WHERE userid='{user_id}';")
            group = self.cursor.fetchone()[0]
            return group
        except TypeError:
            return False

    def update_saved_group(self, user_id, group):
        self.cursor.execute(f"INSERT INTO userdata (userid) VALUES ('{user_id}') "
                            f"ON DUPLICATE KEY UPDATE savedgroup='{group}';")
        self.conn.commit()

    def get_mailing_status(self, user_id):
        self.cursor.execute(f"SELECT mailing FROM userdata WHERE userid='{user_id}';")
        status = self.cursor.fetchone()[0]
        return status

    def update_mailing_status(self, user_id, status):
        self.cursor.execute(f"UPDATE userdata SET mailing='{status}' WHERE userid='{user_id}';")
        self.conn.commit()

    def get_all_mailing(self):
        self.cursor.execute(f"SELECT userid, savedgroup FROM userdata WHERE mailing='1';")
        status = self.cursor.fetchall()
        return status

    # ------------------------------------------------------------------------------------------------------------------
    #                                          changes
    # ----------------------------------------==========----------------------------------------------------------------
    #                                          schedule
    # ------------------------------------------------------------------------------------------------------------------

    def get(self, group, isupper=True, day=None):
        if self.tablename == 'schedule':
            self.cursor.execute(f"SELECT * FROM schedule WHERE groupname='{group}' "
                                f"and isupper='{isupper}' and weekday='{day}';")
        elif self.tablename == 'changes':
            self.cursor.execute(f"SELECT * FROM changes WHERE groupname='{group}';")
        lessons = self.cursor.fetchone()
        return lessons

    def insert(self, group, islef, lessons, day=None, isupper=None):
        # (list) lessons: ключ - номер пары, кортеж - имя пары, кабинет
        if self.tablename == 'schedule':
            self.cursor.execute(f"""
                                INSERT INTO schedule
                                        (groupname, islef, isupper, weekday, 
                                        lesson_1, lesson_1_room, lesson_2, lesson_2_room,
                                        lesson_3, lesson_3_room, lesson_4, lesson_4_room,
                                        lesson_5, lesson_5_room, lesson_6, lesson_6_room)
                                VALUES ('{group}', '{islef}', '{isupper}', '{day}', 
                                        '{lessons[0][0]}', '{lessons[0][1]}', '{lessons[1][0]}', '{lessons[1][1]}',
                                        '{lessons[2][0]}', '{lessons[2][1]}', '{lessons[3][0]}', '{lessons[3][1]}',
                                        '{lessons[4][0]}', '{lessons[4][1]}', '{lessons[5][0]}', '{lessons[5][1]}');""")
            self.conn.commit()
        elif self.tablename == 'changes':
            self.cursor.execute(f"""
                                INSERT INTO changes
                                        (groupname, islef,
                                        lesson_1, lesson_1_room, lesson_2, lesson_2_room,
                                        lesson_3, lesson_3_room, lesson_4, lesson_4_room,
                                        lesson_5, lesson_5_room, lesson_6, lesson_6_room)
                                VALUES ('{group}', '{islef}',
                                        '{lessons[0][0]}', '{lessons[0][1]}', '{lessons[1][0]}', '{lessons[1][1]}',
                                        '{lessons[2][0]}', '{lessons[2][1]}', '{lessons[3][0]}', '{lessons[3][1]}',
                                        '{lessons[4][0]}', '{lessons[4][1]}', '{lessons[5][0]}', '{lessons[5][1]}');""")
            self.conn.commit()

    def get_all_groups(self):
        allgroups = []
        for row in self.cursor.execute(f"SELECT DISTINCT groupname FROM {self.tablename};"):
            allgroups.append(row[0])
        return allgroups

    def clear(self):
        if self.tablename not in ['sysdata', 'userdata']:
            self.cursor.execute(f"DELETE FROM {self.tablename};")
            self.conn.commit()

    # ------------------------------------------------------------------------------------------------------------------
    #                                          config
    # ------------------------------------------------------------------------------------------------------------------

    def create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS 
        sysdata (
        changesdate VARCHAR(20) NULL DEFAULT '',
        changeslasturl VARCHAR(255) NULL DEFAULT '',
        allgroups VARCHAR(255) NULL DEFAULT '',
        schedulelasturl VARCHAR(255) NULL DEFAULT ''
        );""")
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS 
        userdata (
        userid INT(11) NOT NULL,
        savedgroup VARCHAR(10) NULL DEFAULT NULL,
        mailing TINYINT(1) DEFAULT '0',
        UNIQUE INDEX userid (userid ASC)
        );""")
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS
        changes (
        groupname VARCHAR(10) NOT NULL,
        islef TINYINT(1) DEFAULT '0',
        lesson_1 VARCHAR(255) DEFAULT '',
        lesson_1_room VARCHAR(255) DEFAULT '',
        lesson_2 VARCHAR(255) DEFAULT '',
        lesson_2_room VARCHAR(255) DEFAULT '',
        lesson_3 VARCHAR(255) DEFAULT '',
        lesson_3_room VARCHAR(255) DEFAULT '',
        lesson_4 VARCHAR(255) DEFAULT '',
        lesson_4_room VARCHAR(255) DEFAULT '',
        lesson_5 VARCHAR(255) DEFAULT '',
        lesson_5_room VARCHAR(255) DEFAULT '',
        lesson_6 VARCHAR(255) DEFAULT '',
        lesson_6_room VARCHAR(255) DEFAULT '',
        UNIQUE INDEX groupname (groupname ASC)
        );""")
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS
        schedule (
        groupname VARCHAR(10) NOT NULL,
        islef TINYINT(1) DEFAULT '0',
        isupper TINYINT(1) DEFAULT '0',
        weekday TINYINT(1) NOT NULL,
        lesson_1 VARCHAR(255) DEFAULT '',
        lesson_1_room VARCHAR(255) DEFAULT '',
        lesson_2 VARCHAR(255) DEFAULT '',
        lesson_2_room VARCHAR(255) DEFAULT '',
        lesson_3 VARCHAR(255) DEFAULT '',
        lesson_3_room VARCHAR(255) DEFAULT '',
        lesson_4 VARCHAR(255) DEFAULT '',
        lesson_4_room VARCHAR(255) DEFAULT '',
        lesson_5 VARCHAR(255) DEFAULT '',
        lesson_5_room VARCHAR(255) DEFAULT '',
        lesson_6 VARCHAR(255) DEFAULT '',
        lesson_6_room VARCHAR(255) DEFAULT ''
        );""")

        self.cursor.execute("SELECT * FROM sysdata;")
        if self.cursor.fetchone() is None:
            self.cursor.execute("INSERT INTO sysdata (changesdate, changeslasturl) VALUES ('None', 'None');")
            self.conn.commit()
