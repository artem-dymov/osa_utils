import asyncio
from osa_utils.db_api.database import create_db, drop_connection
from osa_utils.db_api import db_commands
from osa_utils.db_api.models import User, Teacher, Group


async def main():
    await create_db()

    groups = await db_commands.get_all_groups('fbme')
    for group in groups:
        print(group.name)

    await drop_connection()

asyncio.get_event_loop().run_until_complete(main())
