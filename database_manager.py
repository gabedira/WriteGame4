import sqlite3
from datetime import datetime
import csv
import os
import pickle

connection = sqlite3.connect("my_database")
# TODO: Figure out foreign key constraint

#connection.execute("DROP TABLE IF EXISTS starred;")
#connection.execute("DROP TABLE IF EXISTS words;")
#connection.execute("DROP TABLE IF EXISTS sets;")
#connection.execute("DROP TABLE IF EXISTS users;")


'''
connection.execute("CREATE TABLE IF NOT EXISTS users (user_id INT PRIMARY KEY, user_name STRING UNIQUE);")

connection.execute("CREATE TABLE IF NOT EXISTS sets(set_id INT PRIMARY KEY, user_id INT, set_name STRING, num_terms INT, created DATE, FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE);")

connection.execute("CREATE TABLE IF NOT EXISTS words(word_id INT PRIMARY KEY, set_id INT, word STRING, defn STRING, FOREIGN KEY (set_id) REFERENCES sets(set_id) ON DELETE CASCADE);")

connection.execute("CREATE TABLE IF NOT EXISTS starred( user_id INT, set_id INT, word_id INT, FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE, FOREIGN KEY (set_id) REFERENCES sets(set_id) ON DELETE CASCADE, FOREIGN KEY (word_id) REFERENCES words(word_id) ON DELETE CASCADE);") 
'''

'''
connection.execute("CREATE TABLE IF NOT EXISTS paused(user_id INT, name STRING, played DATE, filename STRING, FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE);")
'''



#connection.execute("DELETE FROM sets")
#connection.execute("DELETE FROM words")
#connection.commit()
'''
print(connection.execute("SELECT * FROM sets").fetchall())
print(connection.execute("SELECT word, word_id, set_id FROM words").fetchall())

'''


class DataBaseManager:
    def __init__(self, db_name):
        
        self.__connection = sqlite3.connect(db_name)
        self.__today = datetime.now()

    
    def get_max_user_id(self):
        statement = "SELECT user_id FROM users ORDER BY user_id DESC LIMIT 1"
        ret = self.__connection.execute(statement)
        
        ret = ret.fetchall()
        if len(ret) > 0:
            return ret[0][0]
        else:
            return 0

    
    def get_user_id(self, user_name):
        statement = "SELECT user_id FROM users WHERE user_name='" + user_name + "'"
        ret = self.__connection.execute(statement)
        
        ret = ret.fetchall()
        if len(ret) > 0:
            return ret[0][0]
        else:
            return -1

    
    def get_max_set_id(self):
        statement = "SELECT set_id FROM sets ORDER BY set_id DESC LIMIT 1"
        ret = self.__connection.execute(statement)
        
        ret = ret.fetchall()
        if len(ret) > 0:
            return ret[0][0]
        else:
            return 0

            
    def get_max_word_id(self):
        statement = "SELECT word_id FROM words ORDER BY word_id DESC LIMIT 1"
        ret = self.__connection.execute(statement)
        
        ret = ret.fetchall()
        if len(ret) > 0:
            return ret[0][0]
        else:
            return 0

            
    def list_users(self):
        statement = "SELECT * FROM users ORDER BY user_id"
        ret = self.__connection.execute(statement)
        return dict(ret.fetchall())

    
    def list_sets(self, user_id = None):
        statement = "SELECT * FROM sets"
        if user_id != None:
            statement += " WHERE user_id =" + str(user_id)
                
        ret = self.__connection.execute(statement)
        return ret.fetchall()

    
    def list_words(self, set_id = None):
        statement = "SELECT * FROM words"

        if set_id != None:
            statement += "WHERE set_id =" + str(set_id)
        
        ret = self.__connection.execute(statement)
        return ret.fetchall()

    
    def insert_user(self, user_name):
        user_id = self.get_max_user_id() + 1
        try:
            statement = "INSERT INTO users(user_id, user_name) VALUES(" + str(user_id) + ", '" + user_name + "');"
            
            self.__connection.execute(statement)
            self.__connection.commit()
            return True

        except sqlite3.IntegrityError:
            return False

    
    def insert_set(self, set_name, user_id, created = None, terms = 0):
        if created == None:
            created = self.__today.strftime("%m/%d/%y")
        
        set_id = self.get_max_set_id() + 1
        try:
            statement = "INSERT INTO sets(set_id, user_id, set_name, num_terms, created) VALUES(" + str(set_id) + ", " + str(user_id) + ", '" + set_name + "', " + str(terms) + ", '" + created + "');"
            self.__connection.execute(statement)
            self.__connection.commit()
            return set_id

        except Exception as e:
            print(e)
            return -1

    
    def insert_word(self, word, defn, word_id = None, set_id = 0):
        if word_id == None:
            word_id = self.get_max_word_id() + 1

        word = word.replace("'", "''")
        defn = defn.replace("'", "''")
        
        try:
            statement = "INSERT INTO words(word_id, set_id, word, defn) VALUES(" + str(word_id) + ", " + str(set_id) + ", '" + word + "', '" + defn+"');"
            self.__connection.execute(statement)
            self.__connection.commit()
            return set_id

        except Exception as e:
            print(e)
            return -1
        

    def read_from_csv(self, file_name, set_name, user_id, date = None, delete_file= False):
        set_id =  self.insert_set(set_name, user_id, created = date)
            
        if set_id == -1:
            return -1

        word_id = self.get_max_word_id() + 1
        num_words = 0
        
        with open(file_name, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in reader:
                word = row[0].strip()
                defn = row[1].strip()
                verif = self.insert_word(word, defn, word_id + num_words, set_id)
                if verif == -1:
                    print("Error inserting " + word)
                num_words += 1

            statement = "SELECT COUNT(*) FROM words WHERE set_id="+str(set_id)
            num_successful = self.__connection.execute(statement).fetchall()[0][0]
            
            statement = "UPDATE sets SET num_terms = " + str(num_successful) + " WHERE set_id  = " + str(set_id)
            self.__connection.execute(statement)

        if delete_file:
            os.remove(file_name)

        self.__connection.commit()
            
    
    def delete_set(self, set_id):
        statement1 = "DELETE FROM sets WHERE set_id = " + set_id
        statement2 = "DELETE FROM words WHERE set_id = " + set_id

        self.__connection.execute(statement1)
        self.__connection.execute(statement2)

        self.__connection.commit()


    def get_words(self, set_id):
        statement = "SELECT word, defn FROM words WHERE set_id = " + str(set_id)
        ret = self.__connection.execute(statement).fetchall()
        #print(ret)
        words, defns = zip(*ret)
        return words, defns

    def pickle(self, user_id, write):
        try:
            played = self.__today.strftime("%m/%d/%y")
            filename = "pausepoint_"+self.__today.strftime("%m_%d_%y_%H_%M_%S")
            statement = "INSERT INTO paused(user_id, name, played, filename) VALUES(" + str(user_id) + ", '" + filename + "', '" + played + "', '" + filename+"');"
            self.__connection.execute(statement)
            self.__connection.commit()

            with open(filename, 'wb') as f:
                pickle.dump(write,f)
                f.close()
        
        except Exception as e:
            print(e)
            return -1

    def list_pause_points(self, user_id):
        try:
            statement = "SELECT played, filename FROM paused WHERE user_id = " + str(user_id)
            
            ret = self.__connection.execute(statement)
            return ret.fetchall()
            
        
        except Exception as e:
            print(e)
            return -1

        
    def load_pause_point(self, filename):
        try:
            with open(filename, 'rb') as f:
                write = pickle.load(f)
                f.close()
                os.remove(filename)
                statement = "DELETE FROM paused WHERE filename = '"+filename+"'"
                self.__connection.execute(statement)
                self.__connection.commit()
                return write
                
        
        except Exception as e:
            print(e)
            return -1
    
    '''   

    def star_word(self, user_id, word_id)

    def star_words(self, user_id, word_ids)
'''
    

