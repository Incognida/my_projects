import sys
import os
import subprocess
import time

import psycopg2
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'doTogether.settings'
django.setup()
from django.contrib.auth import get_user_model
from social_events.models import Category, Subcategory


def populate():
    User = get_user_model()
    incognida = User.objects.create_user(
        username="incognida", password="123qwe123",
        email="psauxgrepkill@gmail.com", sex="male", age=24
    )
    incognida.is_staff = True
    incognida.is_superuser=True
    incognida.save()
    for i in range(10):
        c = Category.objects.create(title=f"c{i+1}")
        for j in range(4):
            Subcategory.objects.create(title=f"s{i+1}{j+1}",
                                       category=c)
    for i in range(10):
        User.objects.create_user(
            username=f"u{i+1}", password="123qwe123",
            email=f"u{i+1}@gmail.com",
            sex="male", age=18 + i,
        )


def delete_db():
    conn_string = "host='localhost' " \
                  "dbname='vlad_db' user='vlad_user' password='1'"
    try:
        conn = psycopg2.connect(conn_string)
        conn.set_isolation_level(0)
    except:
        print("Unable to connect to the database.")

    cur = conn.cursor()

    try:
        cur.execute(
            "SELECT table_schema,table_name"
            " FROM information_schema.tables"
            " WHERE table_schema = 'public'"
            " ORDER BY table_schema,table_name")
        rows = cur.fetchall()
        for row in rows:
            print(f"dropping table: {row[1]}")
            cur.execute(f"drop table {row[1]} cascade")
        cur.close()
        conn.close()
    except:
        print(f"Error {sys.exc_info()[1]}")


if __name__ == '__main__':
    print('deleting migrations')
    subprocess.Popen(["find", ".", "-path", "*/migrations/*.py", "-not",
                      "-name", "__init__.py", "-delete"])
    time.sleep(1)
    subprocess.Popen(["find", ".", "-path", "*/migrations/*.pyc", "-delete"])
    print('deleted migrations')
    time.sleep(1)
    delete_db()
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            x = subprocess.Popen(['python', 'manage.py', 'makemigrations'])
            x.wait()
            y = subprocess.Popen(['python', 'manage.py', 'migrate'])
            y.wait()
            populate()
