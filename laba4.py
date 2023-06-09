import psycopg2
import tkinter as tk
from tkinter import messagebox
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Функция для создания базы данных


def create_connection():
    return (psycopg2.connect("user=postgres password=deeznuts420"))


def create_db_connection(db_name):
    return (psycopg2.connect(("dbname={} user=postgres password=deeznuts420").format(
        db_name)))


def create_functions(db_name, tab_name):
    conn = create_db_connection(db_name)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("CREATE OR REPLACE FUNCTION viewContent(tab_name varchar(30))\r\n" +
                "RETURNS SETOF " + tab_name + "\r\n" +
                "AS\r\n" +
                "$$\r\n" +
                "DECLARE res record;\r\n" +
                "BEGIN\r\n" +
                "FOR res in\r\n" +
                "EXECUTE 'SELECT * FROM ' ||tab_name|| '' loop\r\n" +
                "return next res;\r\n" +
                "end loop;\r\n" +
                "END;\r\n" +
                "$$ LANGUAGE plpgsql;")
    cur.execute("CREATE OR REPLACE FUNCTION createTable(tab_name varchar(30))\r\n" +
                "RETURNS void\r\n" +
                "AS\r\n" +
                "$$\r\n" +
                "BEGIN\r\n" +
                "EXECUTE 'CREATE TABLE IF NOT EXISTS '|| tab_name ||'(\r\n" +
                "id int PRIMARY KEY CHECK (id > 0),\r\n" +
                "name text NOT NULL,\r\n" +
                "address text NOT NULL,\r\n" +
                "pay_percent int CHECK (pay_percent >= 0 AND pay_percent <= 100)\r\n" +
                ")';\r\n" +
                "END;\r\n" +
                "$$ LANGUAGE plpgsql;")

    cur.execute(
        "CREATE OR REPLACE FUNCTION insertTable(tab_name varchar(30), id_val int, name_val varchar(30),\r\n" +
        "									   address_val varchar(30), pay_percent_val int)\r\n" +
        "RETURNS void\r\n" +
        "AS\r\n" +
        "$$\r\n" +
        "BEGIN\r\n" +
        "EXECUTE FORMAT('INSERT INTO %s VALUES (%s, %L, %L, %s)', tab_name, id_val, name_val, address_val, pay_percent_val);\r\n" +
        "END;\r\n" +
        "$$ LANGUAGE plpgsql;")
    cur.execute("CREATE OR REPLACE FUNCTION searchByName(tab_name varchar(30), name_val text)\r\n" +
                "RETURNS SETOF " + tab_name + "\r\n" +
                "AS\r\n" +
                "$$\r\n" +
                "declare\r\n" +
                "    res record;\r\n" +
                "BEGIN\r\n" +
                "FOR res in\r\n" +
                "EXECUTE FORMAT('SELECT * FROM %s WHERE name = %L', tab_name, name_val) loop\r\n" +
                "return next res;\r\n" +
                "end loop;\r\n" +
                "END;\r\n" +
                "$$ LANGUAGE plpgsql;")
    cur.execute(
        "CREATE OR REPLACE FUNCTION updateTuple(tab_name varchar(30), id_val int, name_val varchar(30), \r\n" +
        "									   address_val varchar(30), pay_percent_val int)\r\n" +
        "RETURNS void\r\n" +
        "AS\r\n" +
        "$$\r\n" +
        "BEGIN\r\n" +
        "EXECUTE FORMAT('UPDATE %s SET name = %L, address = %L, pay_percent = %s WHERE id = %s',\r\n" +
        "			  tab_name, name_val, address_val, pay_percent_val, id_val);\r\n" +
        "END;\r\n" +
        "$$ LANGUAGE plpgsql;")
    cur.execute("CREATE OR REPLACE FUNCTION deleteByName(tab_name varchar(30), name_val text)\r\n" +
                "RETURNS void\r\n" +
                "AS\r\n" +
                "$$\r\n" +
                "BEGIN\r\n" +
                "EXECUTE FORMAT('DELETE FROM %s WHERE name = %L', tab_name, name_val);\r\n" +
                "END;\r\n" +
                "$$ LANGUAGE plpgsql;")
    print("done creating sql functions")


def view_database(database_name, table_name):
    conn = create_db_connection(database_name)
    print(database_name)
    print(table_name)
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    cur.execute("select * FROM viewContent(%s)",
                (table_name,))
    results = []  # Define the results variable as an empty list
    for row in cur:
        print(row)
        results.append(row)  # Append the row to the results list
    return (results)
    cur.close()
    conn.close()


def create_database(database_name):
    conn = create_connection()
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute(sql.SQL("CREATE DATABASE {}").format(
        sql.Identifier(database_name)))
    cur.close()
    conn.close()


def create_table(database_name, table_name):
    conn = create_db_connection(database_name)
    conn.set_session(autocommit=True)
    cur = conn.cursor()

    cur.execute("select createTable(%s)", (table_name,))

    cur.close()
    conn.close()


# Функция для удаления базы данных


def drop_database(database_name):
    conn = create_connection()
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute(sql.SQL((f"drop_database({database_name})")))
    cur.close()
    conn.close()

# Функция для очистки таблицы


def truncate_table(database_name, table_name):
    conn = create_db_connection(database_name)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.callproc('truncate_table_function', [table_name])
    cur.close()
    conn.close()

# Функция для добавления новых данных


def insert_data(database_name, table_name, data):
    conn = create_db_connection(database_name)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("select insertTable(%s, %s, %s, %s, %s)",
                (table_name, data[0], data[1], data[2], data[3]))
    cur.close()
    conn.close()

# Функция для поиска по текстовому полю


def search_data(database_name, table_name, search_query):
    conn = create_db_connection(database_name)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("select * FROM searchByName(%s, %s)",
                (table_name, search_query))
    results = []  # Define the results variable as an empty list
    for row in cur:
        print(row)
        results.append(row)  # Append the row to the results list
    return (results)
    cur.close()
    conn.close()

# Функция для обновления кортежа


def update_data(database_name, table_name, data):
    conn = create_db_connection(database_name)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    string = data.replace(" ", "")

    # Split the string by commas
    splitData = string.split(",")
    print(splitData)
    cur.execute("select updateTuple(%s, %s, %s, %s, %s)",
                (table_name, splitData[0], splitData[1], splitData[2], splitData[3]))
    cur.close()
    conn.close()

# Функция для удаления по текстовому полю


def delete_data(database_name, table_name, value):
    conn = create_db_connection(database_name)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("select deleteByName(%s, %s)", (table_name, value))
    cur.close()
    conn.close()


def create_login_gui():
    def check_admin_password(username, password):
        if username == "postgres" and password == "deeznuts420":
            return True
        else:
            return False

    def check_guest_password(username, password):
        if username == "guest" and password == "guestpswd":
            return True
        else:
            return False

    # Function to handle the login button click event

    def login():
        username = username_entry.get()
        password = password_entry.get()
        if check_admin_password(username, password):
            messagebox.showinfo("Login Successful", "Login successful!")
            admin_gui()
        elif check_guest_password(username, password):
            guest_gui()
        else:
            messagebox.showerror(
                "Login Failed", "Invalid username or password!")

    # Create the login GUI
    login_window = tk.Tk()
    login_window.title("Login")

    username_label = tk.Label(login_window, text="Username:")
    username_label.pack()
    username_entry = tk.Entry(login_window)
    username_entry.pack()

    password_label = tk.Label(login_window, text="Password:")
    password_label.pack()
    password_entry = tk.Entry(login_window, show="*")
    password_entry.pack()

    login_button = tk.Button(login_window, text="Login", command=login)
    login_button.pack()

    login_window.mainloop()


def admin_gui():
    window = tk.Tk()
    window.title("Database Operations")

    view_database_label = tk.Label(window, text="View Database:")
    view_database_label.pack()
    view_database_entry = tk.Entry(window)
    view_database_entry.pack()
    view_table_entry = tk.Entry(window)
    view_table_entry.pack()

    def view_database_action():
        database_name = str(view_database_entry.get())
        table_name = str(view_table_entry.get())
        try:
            results = view_database(database_name, table_name)
            messagebox.showinfo("Table", results)
        except psycopg2.Error as e:
            messagebox.showerror("Error", str(e))
    view_database_button = tk.Button(
        window, text="View", command=view_database_action)
    view_database_button.pack()

    def create_database_action():
        database_name = database_entry.get()
        try:
            create_database(database_name)
            messagebox.showinfo("Success", "Database created successfully!")
        except psycopg2.Error as e:
            messagebox.showerror("Error", str(e))

    # Create Database
    create_database_label = tk.Label(window, text="Create Database:")
    create_database_label.pack()
    database_entry = tk.Entry(window)
    database_entry.pack()
    create_database_button = tk.Button(
        window, text="Create", command=create_database_action)
    create_database_button.pack()

    # create table
    create_table_label = tk.Label(window, text="Create Table:")
    create_table_label.pack()
    create_table_database_entry = tk.Entry(window)
    create_table_database_entry.pack()
    create_table_table_entry = tk.Entry(window)
    create_table_table_entry.pack()

    def create_table_action():
        database_name = create_table_database_entry.get()
        table_name = create_table_table_entry.get()
        try:
            create_table(database_name, table_name)
            messagebox.showinfo("Success", "Table created successfully!")
        except psycopg2.Error as e:
            messagebox.showerror("Error", str(e))

    create_table_button = tk.Button(
        window, text="Create", command=create_table_action)
    create_table_button.pack()

    # Drop Database
    drop_database_label = tk.Label(window, text="Drop Database:")
    drop_database_label.pack()
    drop_database_entry = tk.Entry(window)
    drop_database_entry.pack()

    def drop_database_action():
        database_name = drop_database_entry.get()
        try:
            drop_database(database_name)
            messagebox.showinfo("Success", "Database dropped successfully!")
        except psycopg2.Error as e:
            messagebox.showerror("Error", str(e))
    drop_database_button = tk.Button(
        window, text="Drop", command=drop_database_action)
    drop_database_button.pack()

    # Truncate Table
    truncate_table_label = tk.Label(window, text="Truncate Table:")
    truncate_table_label.pack()
    truncate_database_entry = tk.Entry(window)
    truncate_database_entry.pack()
    truncate_table_entry = tk.Entry(window)
    truncate_table_entry.pack()

    def truncate_table_action():
        database_name = truncate_database_entry.get()
        table_name = truncate_table_entry.get()
        try:
            truncate_table(database_name, table_name)
            messagebox.showinfo("Success", "Table truncated successfully!")
        except psycopg2.Error as e:
            messagebox.showerror("Error", str(e))
    truncate_table_button = tk.Button(
        window, text="Truncate", command=truncate_table_action)
    truncate_table_button.pack()

    # Insert Data
    insert_data_label = tk.Label(window, text="Insert Data:")
    insert_data_label.pack()
    insert_database_entry = tk.Entry(window)
    insert_database_entry.pack()
    insert_table_entry = tk.Entry(window)
    insert_table_entry.pack()
    insert_data_values = tk.Entry(window)
    insert_data_values.pack()

    def insert_data_action():
        database_name = insert_database_entry.get()
        table_name = insert_table_entry.get()
        data_values = insert_data_values.get()
        data = tuple(data_values.split(","))
        try:
            insert_data(database_name, table_name, data)
            messagebox.showinfo("Success", "Data inserted successfully!")
        except psycopg2.Error as e:
            messagebox.showerror("Error", str(e))
    insert_data_button = tk.Button(
        window, text="Insert", command=insert_data_action)
    insert_data_button.pack()

    # Search Data
    search_data_label = tk.Label(window, text="Search Data:")
    search_data_label.pack()
    search_database_entry = tk.Entry(window)
    search_database_entry.pack()
    search_table_entry = tk.Entry(window)
    search_table_entry.pack()
    search_query_entry = tk.Entry(window)
    search_query_entry.pack()

    def search_data_action():
        database_name = search_database_entry.get()
        table_name = search_table_entry.get()
        search_query = search_query_entry.get()
        try:
            results = search_data(database_name, table_name,
                                  search_query)

            # print(results)
            messagebox.showinfo("Search Results", results)
        except psycopg2.Error as e:
            messagebox.showerror("Error", str(e))
    search_data_button = tk.Button(
        window, text="Search", command=search_data_action)
    search_data_button.pack()

    # Update Data
    update_data_label = tk.Label(window, text="Update Data:")
    update_data_label.pack()
    update_database_entry = tk.Entry(window)
    update_database_entry.pack()
    update_table_entry = tk.Entry(window)
    update_table_entry.pack()
    update_new_value_entry = tk.Entry(window)
    update_new_value_entry.pack()

    def update_data_action():
        database_name = update_database_entry.get()
        table_name = update_table_entry.get()
        new_value = update_new_value_entry.get()
        try:
            update_data(database_name, table_name, new_value)
            messagebox.showinfo("Success", "Data updated successfully!")
        except psycopg2.Error as e:
            messagebox.showerror("Error", str(e))
    update_data_button = tk.Button(
        window, text="Update", command=update_data_action)
    update_data_button.pack()

    # Delete Data
    delete_data_label = tk.Label(window, text="Delete Data:")
    delete_data_label.pack()
    delete_database_entry = tk.Entry(window)
    delete_database_entry.pack()
    delete_table_entry = tk.Entry(window)
    delete_table_entry.pack()
    delete_value_entry = tk.Entry(window)
    delete_value_entry.pack()

    def delete_data_action():
        database_name = delete_database_entry.get()
        table_name = delete_table_entry.get()
        value = delete_value_entry.get()
        try:
            delete_data(database_name, table_name, value)
            messagebox.showinfo("Success", "Data deleted successfully!")
        except psycopg2.Error as e:
            messagebox.showerror("Error", str(e))
    delete_data_button = tk.Button(
        window, text="Delete", command=delete_data_action)
    delete_data_button.pack()

    window.mainloop()


def guest_gui():
    window = tk.Tk()
    window.title("Database Operations")

    view_database_label = tk.Label(window, text="View Database:")
    view_database_label.pack()
    view_database_entry = tk.Entry(window)
    view_database_entry.pack()
    view_table_entry = tk.Entry(window)
    view_table_entry.pack()

    def view_database_action():
        database_name = str(view_database_entry.get())
        table_name = str(view_table_entry.get())
        try:
            results = view_database(database_name, table_name)
            messagebox.showinfo("Table", results)
        except psycopg2.Error as e:
            messagebox.showerror("Error", str(e))
    view_database_button = tk.Button(
        window, text="View", command=view_database_action)
    view_database_button.pack()

    # Search Data
    search_data_label = tk.Label(window, text="Search Data:")
    search_data_label.pack()
    search_database_entry = tk.Entry(window)
    search_database_entry.pack()
    search_table_entry = tk.Entry(window)
    search_table_entry.pack()
    search_query_entry = tk.Entry(window)
    search_query_entry.pack()

    def search_data_action():
        database_name = search_database_entry.get()
        table_name = search_table_entry.get()
        search_query = search_query_entry.get()
        try:
            results = search_data(database_name, table_name,
                                  search_query)

            # print(results)
            messagebox.showinfo("Search Results", results)
        except psycopg2.Error as e:
            messagebox.showerror("Error", str(e))
    search_data_button = tk.Button(
        window, text="Search", command=search_data_action)
    search_data_button.pack()

    window.mainloop()


create_functions('laba2', 'bruh')

# Run the GUI
create_login_gui()
