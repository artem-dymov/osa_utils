import asyncio
import os
import sys

from osa_utils.db_api import db_commands
from config import faculties, faculties_ukr
from osa_utils.db_api.database import create_db, drop_connection


async def main():
    await create_db()

    os.chdir('photos')

    for faculty_ukr in os.listdir():
        if faculty_ukr != 'default_picture':
            os.chdir(f'{faculty_ukr}')

            for teacher_photo in os.listdir():
                file_name = teacher_photo
                teacher_photo = teacher_photo.split('.')
                if teacher_photo.__len__() > 1:
                    if teacher_photo[-1] == 'jpg' or teacher_photo[-1] == 'png' or \
                            teacher_photo[-1] == 'jpeg' or teacher_photo[-1] == 'webp':
                        teacher_photo.pop()

                        full_name = ''
                        for i in teacher_photo:
                            full_name = full_name + i

                        print(full_name)

                        try:
                            int(full_name)
                        except TypeError and ValueError:
                            faculty = faculties[faculties_ukr.index(faculty_ukr)]
                            teacher = await db_commands.get_teacher_by_name(faculty, full_name)

                            if teacher is not None:
                                new_file_name = str(teacher.id) + '.jpg'
                                os.rename(file_name, new_file_name)
                            else:
                                suggest_text = ''
                                suggest_list = {}
                                suggest = await db_commands.search_teachers_by_name(faculty, full_name.split(' ')[0])
                                if suggest:
                                    if suggest.__len__() > 0:
                                        suggest_list.update({suggest[0].id: suggest[0].full_name})
                                        if suggest.__len__() > 1:
                                            suggest_list.update({suggest[1].id: suggest[1].full_name})
                                            if suggest.__len__() > 2:
                                                suggest_list.update({suggest[2].id: suggest[2].full_name})

                                    for id, name in suggest_list.items():
                                        suggest_text += f'{id} --- {name}    '

                                answer = input(
                                    f'--------------------------------------------\n'
                                    f'Програма не знайшла співпадіння для викладача - {full_name} - {faculty_ukr}.\n'
                                    
                                    f'Результати швидкого авто пошуку: {suggest_text}\n'
                                    
                                    f'Нічого не пишіть і натисніть ENTER, щоб пропустити, або введіть'
                                    f' id цього викладача в базі та натисніть ENTER.\n')


                                if answer.strip() == '':
                                    pass
                                else:
                                    teacher = await db_commands.get_teacher(faculty, int(answer.strip()))
                                    if teacher is not None:
                                        new_file_name = answer + '.jpg'
                                        os.rename(file_name, new_file_name)
                                    else:
                                        print('Такого вилкдача немає. Фото пропущено')
            os.chdir('..')
    await drop_connection()


asyncio.get_event_loop().run_until_complete(main())
