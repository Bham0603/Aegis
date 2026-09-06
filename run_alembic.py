import os

env_path = '.env'
with open(env_path, 'r') as f:
    env_content = f.read()

backup = env_content
new_content = backup.replace('postgresql+asyncpg://aegis_user:aegis_pass@localhost:5432/aegis_db', 'sqlite+aiosqlite:///test.db')

with open(env_path, 'w') as f:
    f.write(new_content)

os.system('alembic revision --autogenerate -m "create_policies_table"')

with open(env_path, 'w') as f:
    f.write(backup)
