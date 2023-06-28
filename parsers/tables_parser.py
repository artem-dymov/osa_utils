import asyncio
from osa_utils.db_api.database import create_db, drop_connection
from osa_utils.db_api import db_commands
from osa_utils.db_api.models import User, Teacher, Group

import sys
import os
from config import faculties, faculties_ukr
import csv

async def type_determine(teacher_type: str):
    teacher_type = teacher_type.lower().strip()
    match teacher_type:
        case '+':
            return 'both'
        case 'л':
            return 'lecture'
        case 'п':
            return 'practice'
        case _:
            return ''

async def main():

    #
    # # groups = await db_commands.get_all_groups('fbme')
    # # for group in groups:
    # #     print(group.name)
    #
    # await drop_connection()

    if len(sys.argv) > 3:
        print("Error. Too much arguments!")
    elif len(sys.argv) == 1:
        # in and out info print
        pass

    elif len(sys.argv) > 1:

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

        elif sys.argv[1] == '--in':

            one_iteration = False
            if len(sys.argv) == 3:
                one_iteration = True
            # await db_commands.delete_all_faculty_data('fbme')

            for faculty in faculties:
                faculty = sys.argv[2]
                faculty_ukr = faculties_ukr[faculties.index(faculty)]

                if faculty_ukr in os.listdir('csv_tables/in'):
                    print(f'{faculty_ukr} in db')
                    await db_commands.delete_all_faculty_data(faculty)
                    print('Faculty data deleted')

                    if 'Групи.csv' in os.listdir(f'csv_tables/in/{faculty_ukr}') and \
                        'Викладачі.csv' in os.listdir(f'csv_tables/in/{faculty_ukr}'):

                        # Open groups csv file
                        with open(f'csv_tables/in/{faculty_ukr}/Групи.csv') as csv_file_g:
                            csv_reader_g = csv.reader(csv_file_g, delimiter=',')

                            # Open teacher csv file
                            csv_teachers_rows = []
                            with open(f'csv_tables/in/{faculty_ukr}/Викладачі.csv') as csv_file_t:
                                csv_reader_t = csv.reader(csv_file_t, delimiter=',')

                                saved_groups = []  # list with groups names

                                first_line = True
                                for teacher_row in csv_reader_t:
                                    csv_teachers_rows.append(teacher_row)
                                    if (not first_line) and teacher_row[0] != '':
                                        if len(teacher_row) > 1:
                                            await db_commands.add_teacher(faculty, teacher_row[0].strip(),
                                                                          await type_determine(teacher_row[1]))
                                        else:
                                            print(f'Warning! Row not > 1. Row skipped. {teacher_row}')
                                    else:
                                        first_line = False

                            print('Teachers saved')

                            # Main in logic
                            teachers: list[Teacher] = await db_commands.get_all_teachers(faculty)
                            first_line = True
                            # iterating groups rows and skipping first row
                            for group_row in csv_reader_g:
                                group_teachers: list[Teacher] = []
                                if not first_line:

                                    if group_row is not None and len(group_row) > 0:

                                        if group_row[0] != '':

                                            group_name = group_row[0].strip().lower()

                                            for teacher_row in csv_teachers_rows:

                                                for el in teacher_row:

                                                    # If certain group in some teacher groups list
                                                    if el.strip().lower() == group_name.strip().lower():

                                                        teacher = await db_commands.get_teacher_by_name(faculty,
                                                                                                        teacher_row[0].strip())
                                                        if teacher is not None:
                                                            group_teachers.append(teacher)
                                                        else:
                                                            print(f'Error adding teacher {teacher_row[0]} to the group'
                                                                  f' {group_name}')

                                            # [{id: ..., full_name: ...}, ...]
                                            group_teachers_to_save = []
                                            for teacher in group_teachers:
                                                group_teachers_to_save.append({'id': teacher.id, 'full_name': teacher.full_name})

                                            # print(f'{group_name} -- {group_teachers} -- {group_teachers_to_save}')

                                            await db_commands.add_group(faculty, group_name, None,
                                                                        group_teachers_to_save)

                                else:
                                    first_line = False
                    else:
                        print('Problem with files presence in faculty folder/')

                else:
                    print(f'No {faculty_ukr} data in folder. Program will skip this faculty.')
                    print(os.listdir('csv_tables/in'))

                if one_iteration:
                    break
        elif sys.argv[1] == '--test':
            group = await db_commands.get_group(847, 'fbme')

            for teacher in group.teachers:
                print(teacher['id'], teacher['full_name'])
        await drop_connection()


asyncio.get_event_loop().run_until_complete(main())
