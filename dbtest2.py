from database_manager import DataBaseManager

dbm = DataBaseManager("my_database")

#dbm.insert_user("Gabriel")
#ret = dbm.insert_set("Test_set", 1)
#print(ret)
#dbm.read_from_csv("vocab set 1.csv", "vocab_1", 1)

print(dbm.list_sets(1))



#print(type(dbm.get_max_user_id()))