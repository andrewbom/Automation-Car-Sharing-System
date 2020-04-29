from flask import Flask, render_template, request, redirect, url_for, session
import pymysql  # MySQLdb  # pymysql


class DatabaseUtils:
    app = Flask(__name__)
    
    HOST = "35.201.23.126"  # google cloud IP address
    USER = "root"  # google cloud sql user name
    PASSWORD = "andrewishandsome"  # google cloud sql password
    DATABASE = "Pythonlogin"

    def __init__(self, connection=None):
        if connection is None:
            connection = pymysql.connect(DatabaseUtils.HOST, DatabaseUtils.USER,
                                         DatabaseUtils.PASSWORD, DatabaseUtils.DATABASE)
        self.connection = connection
        
    def close(self):
        self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def create_account_table(self):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `accounts` (
                    `id` int(11) NOT NULL AUTO_INCREMENT,
                    `username` varchar(50) NOT NULL,
                    `password` varchar(255) NOT NULL,
                    `email` varchar(100) NOT NULL,
                    PRIMARY KEY (`id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
            """)

        self.connection.commit()
        
        
    def insert_account(self, username, password, email):
        with self.connection.cursor() as cursor:
            cursor.execute("INSERT INTO accounts VALUES (NULL, %s, %s, %s)", (username, password, email,))
        self.connection.commit()

        return cursor.rowcount == 1

    def check_exist_username(self, username):
        with self.connection.cursor() as cursor:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))

        return cursor.fetchone()

    def login_account(self, username, password):
        with self.connection.cursor() as cursor:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT * FROM accounts WHERE username = %s AND password = %s", (username, password,))

        return cursor.fetchone()

    def get_account(self, id):
        with self.connection.cursor() as cursor:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT * FROM accounts WHERE id = %s", (id,))

        return cursor.fetchone()

    def delete_account(self, id):
        with self.connection.cursor() as cursor:
            cursor.execute("delete from accounts where id = %s", id)
        self.connection.commit()
