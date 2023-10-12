# import json

faculties =     ('fbme', 'ipp', 'fel', 'its', 'ipt', 'fbt', 'fsl', 'tef', 'imz')
faculties_ukr = ('ФБМІ', 'ВПІ', 'ФЕЛ', 'ІТС', 'ФТІ', 'ФБТ', 'ФСП', 'ІАТЕ', 'ІМЗ')

DATABASE_URL = 'postgresql://postgres:password@localhost:5432/database'

# def _get_data():
#     with open('settings.json', 'r') as file:
#         global DATABASE_URL

#         py_data = json.load(file)

#         DATABASE_URL = py_data['DATABASE_URL']

# try:
#     _get_data()
# except FileNotFoundError:
#     import os
#     os.chdir('../..')
#     _get_data()
# except Exception as e:
#     print(e)
