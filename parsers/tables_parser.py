import asyncio
from osa_utils.db_api.database import create_db, drop_connection
from osa_utils.db_api import db_commands
from osa_utils.db_api.models import User, Teacher, Group

import sys
import os
from config import faculties, faculties_ukr
import csv


async def main():

    #
    # # groups = await db_commands.get_all_groups('fbme')
    # # for group in groups:
    # #     print(group.name)
    #
    # await drop_connection()

    if len(sys.argv) > 2:
        print("Error. Too much arguments!")
    elif len(sys.argv) == 2:

        await create_db()

        if sys.argv[1] == '--out':
            os.makedirs('csv_tables', exist_ok=True)
            os.makedirs('csv_tables/out', exist_ok=True)

            for faculty in faculties:
                faculty_ukr = faculties_ukr[faculties.index(faculty)]
                os.makedirs(f'csv_tables/out/{faculty_ukr}', exist_ok=True)

                groups = []
                # Groups
                with open(f'csv_tables/out/{faculty_ukr}/Групи.csv', 'w+') as csv_file:

                    csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    csv_writer.writerow(['Групи'])

                    groups = await db_commands.get_all_groups(faculty)
                    for group in groups:
                        csv_writer.writerow([group.name])

                # Teachers
                with open(f'csv_tables/out/{faculty_ukr}/Викладачі.csv', 'w+') as csv_file:
                    csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    csv_writer.writerow(['ПІБ', 'Тип', 'Група 1', 'Група 2', 'Група N'])

                    teachers = await db_commands.get_all_teachers(faculty)
                    for teacher in teachers:
                        row = []
                        for char in teacher.full_name:
                            if char == ',':
                                print(f'ALERT!! Comma in this teacher name:\nid = {teacher.id},'
                                      f' name = {teacher.full_name}, faculty = {faculty_ukr}')
                        row.append(teacher.full_name)

                        teacher_type = None
                        match teacher.type:
                            case 'both':
                                teacher_type = '+'
                            case 'lecture':
                                teacher_type = 'л'
                            case 'practice':
                                teacher_type = 'п'
                            case _:
                                teacher_type = ''

                        row.append(teacher_type)

                        for group in groups:
                            for group_teacher in group.teachers:
                                if group_teacher['id'] == teacher.id:
                                    row.append(group.name)

                        csv_writer.writerow(row)


        await drop_connection()



asyncio.get_event_loop().run_until_complete(main())
