# Readme Grader Next Generation

## Manual untuk menjalankan Grader Next Generation

1. Masuk ke dalam direktori /gradernew

2. Buat sebuah virtual environment python3 menggunakan command berikut, `python3 -m venv env`

3. Bila anda menggunakan linux, aktivasi environment python3 yang baru saja anda buat dengan cara menjalankan command, `source env/bin/activate`.

4. Kemudian install semua requirement yang berada di dalam `gradernew/requirement.txt` dengan cara menjalankan command berikut, `pip3 install -r requirement.txt`.

5. Bila terdapat error di beberapa command, mohon beri tahu developer agar bisa ditroubleshoot dan dokumentasi.

6. Setelah itu, mohon buat sebuah file .env di dalam /gradernew. Di dalam file ini, adalah definisi environment variable yang akan digunakan oleh flask. Di antara environment variable tersebut adalah,

Nama Environment Variable | Deskripsi Value
---|---
FLASK_APP | Diisi dengan nama file yang ada di dalam direktori /gradernew yang akan menjadi entry point dari flask. Misalnya, `FLASK_APP=main.py`.

7. Untuk menjalankan aplikasi, buka bash/command prompt dengan environment sedang menyala (`source env/bin/activate` di atas), dan jalankan `flask run`.


## Environment Variables used

Name | Description | Example
---|---|---
FLASKAPP | The entry point for the application. |FLASK_APP=main.py
POSTGRES_URL | URL for the postgres database. |POSTGRES_URL=localhost:32768
POSTGRES_DATABASE_NAME | The name of the database being used. | POSTGRES_DATABASE_NAME=postgres
POSTGRES_USERNAME | Username used to access the database. | POSTGRES_USERNAME=postgres
POSTGRES_PASSWORD | The password used with the username to access the database. | POSTGRES_PASSWORD=lmao123