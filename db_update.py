#!/usr/bin/python

import config.db_config as config
import MySQLdb
import os

db_cursor = None
db = None

def main():
    
    global db_cursor, db
    
    db = MySQLdb.connect(config.db_config["host"], config.db_config["user"], config.db_config["passwd"], config.db_config["db"])

    # cursor object to execute queries
    db_cursor = db.cursor()

    update_modules()
    update_devices()
    update_applications()

    db_cursor.close()
    db.close()
    
def update_modules():
    
    db_cursor.execute("TRUNCATE modules")
    
    for i in range(len(config.module_directories)):

        module_directory = config.module_directories[i]
        path = config.path_root + module_directory + "/"

        for item in os.listdir(path):
            if not os.path.isfile(os.path.join(path, item)):

                # ignoring include directories
                if item == "include":
                    continue
                    
                description = get_description(path + item + "/", item)
                    
                module_name = get_name(path + item + "/", item)
                
                sql = "INSERT INTO modules (name, path, description, group_identifier) VALUES (%s, %s, %s, %s);"
                db_cursor.execute(sql, (module_name, path + item + "/", description, module_directory))

    db.commit()
    
def update_devices():
    
    db_cursor.execute("TRUNCATE devices")
    
    path = config.path_root + "boards/"

    for item in os.listdir(path):
        if not os.path.isfile(os.path.join(path, item)):
            
            sql = "INSERT INTO devices (display_name, internal_name, flash_program) VALUES (%s, %s, %s);"
            db_cursor.execute(sql, (item, item, "openocd"))
            
    db.commit()
    
def update_applications():
    
    db_cursor.execute("TRUNCATE applications")
    
    for i in range(len(config.application_directories)):

        application_directory = config.application_directories[i]
        path = config.path_root + application_directory + "/"

        for item in os.listdir(path):
            if not os.path.isfile(os.path.join(path, item)):

                # ignoring include directories
                if item == "include":
                    continue
                    
                description = get_description(path + item + "/", item)
                    
                application_name = get_name(path + item + "/", item)
                
                sql = "INSERT INTO applications (name, path, description, group_identifier) VALUES (%s, %s, %s, %s);"
                db_cursor.execute(sql, (application_name, path + item + "/", description, application_directory))

    db.commit()

def get_description(path, item):
    
    def get_description_helper(path):
        
        description = ""
    
        try:
            with open(path) as file:
                for line in file:
                    if "@brief" in line:
                        index = line.find("@brief") + len("@brief")
                        description = line[index:].strip()
                        break


        except IOError:
            # ignore missing doc.txt
            return None

        if description == "":
            description = None
            
        return description
        
    # try rule 1
    description = get_description_helper(path + "doc.txt")

    # try rule 2
    if description is None:
        description = get_description_helper(path + item + ".c")

    # try rule 3
    if description is None:
        description = get_description_helper(path + "main.c")
        
    return description

def get_name(path, application_directory):
    
    name = ""
    
    try:
        with open(path + "Makefile") as makefile:
            for line in makefile:
                
                line = line.replace(" ", "")
                
                if "APPLICATION=" in line:
                    index = line.find("APPLICATION=") + len("APPLICATION=")
                    name = line[index:]
                    break
                    
                elif "PKG_NAME=" in line:
                    index = line.find("PKG_NAME=") + len("PKG_NAME=")
                    name = line[index:]
                    break
    
    except IOError:
        return application_directory
    
    if name == "":
        name = application_directory
    
    # remove \n and stuff like that
    return name.strip()

if __name__ == "__main__":
    main()