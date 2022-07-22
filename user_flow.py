from database_manager import DataBaseManager
from os.path import exists
from write import Write
import os


class UserFlow:
    def __init__(self, db_name):
        self.__user_id = -1
        self.__user_name = ""
        self.__dbm = DataBaseManager(db_name)

    def start_flow(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.__get_user_name()
        self.__main_flow()
        print("Goodbye")

    def __get_user_name(self):
        user_name = input("Enter user name: ")

        if self.__dbm.get_user_id(user_name) != -1:
            print("Welcome back " + user_name + ".")
        else:
            print("Welcome " + user_name + ".")
            self.__dbm.insert_user(user_name)

        self.__user_id = self.__dbm.get_user_id(user_name)
        self.__user_name = user_name
        print()

    def __main_flow(self):
        while True:
            option = self.__list_options()
            if option == 'q':
                return

            if option == '1':
                self.__add_set_option()
            elif option == '2':
                self.__list_sets_option()
            elif option == '3':
                self.__play_game_option()
            elif option == '4':
                self.__load_game_option()
            else:
                print("Invalid option.")

    def __load_game_option(self):
        pause_points = self.__dbm.list_pause_points(self.__user_id)
        if len(pause_points) == 0:
            print("No pause points. Press any button to return to menu")
            input()
            return
        
        for i in range(len(pause_points)):
            print(str(i+1) + ". " + pause_points[i][0])

        index = input("Select the pause point to load.")
        print()
        if not index.isdigit() or index >= len(pause_points):
            return
        filename = pause_points[int(index)-1][1]

        write = self.__dbm.load_pause_point(filename)
        write.play_game()
        

            
    def __list_options(self):
        while True:
            valid_options = ['1', '2', '3', '4', 'q']
            os.system('cls' if os.name == 'nt' else 'clear')
            print("Hello " + self.__user_name)
            print()
            print("=========================")
            print("| 1. Add a set          |")
            print("| 2. List your sets     |")
            print("| 3. Play new  game     |")
            print("| 4. Load previous game |")
            print("| Or enter 'q' to quit  |")
            print("=========================")
            print()
            option = input()
            if option not in valid_options:
                print("Invalid option\n")
            else:
                break
        return option

    def __add_set_option(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        filename = input("Enter file name: ")
        if not exists(filename):
            print("Invalid file, exiting")
            return
        if filename.strip()[-3:] != "csv":
            print("This is only supported for .csv files. Exiting")
            return

        set_name = input("Enter desired set name: ")
        delete = input("Delete this csv [y/n]: ")
        delete = (delete == 'y')

        self.__dbm.read_from_csv(filename,
                                 set_name,
                                 self.__user_id,
                                 delete_file=delete)

    def __list_sets(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        ret = self.__dbm.list_sets(0)
        ret.extend(self.__dbm.list_sets(self.__user_id))
        if len(ret) == 0:
            print("No sets found.")
            return 0

        print("   | Name \t\t | # of terms | Created on")
        print("===|=============|============|============")
        i = 1
        for row in ret:
            print("%2d" % i + " | " + row[2] + '\t | ' + "%3d" % int(row[3]) +
                  "\t\t  | " + row[4])
            i = i + 1
        return i - 1

    def __list_words(self, words, defns):
        print()
        print("    | word          | definition ")
        print("====|===============|" + "=" * 41)
        for i in range(len(words)):
            n = 40
            chunks = [defns[i][j:j + n] for j in range(0, len(defns[i]), n)]

            print("%3d" % (i + 1) + " | " + words[i].ljust(13) + ' | ' +
                  chunks[0])
            for j in range(len(chunks) - 1):
                print(" " * 4 + "|" + " " * 15 + "| " + chunks[j + 1])

    def __list_sets_option(self):
        n = self.__list_sets()
        if n == 0:
            return

        ret = self.__dbm.list_sets(0)
        ret.extend(self.__dbm.list_sets(self.__user_id))
        
        set_ids = []
        for row in ret:
            set_ids.append(int(row[0]))
        print()
        i = input("Enter the set you want to expand: ")
        if not (i.isdigit() and int(i) <= len(set_ids)):
            print("Invalid number. Exiting.")
            return

        set_id = set_ids[int(i) - 1]
        print()
        words, defns = self.__dbm.get_words(set_id)

        self.__list_words(words, defns)

        input("\nEnter any key to exit.")

    def __play_game_option(self):
        self.__list_sets()
        ret = self.__dbm.list_sets(0)
        ret.extend(self.__dbm.list_sets(self.__user_id))
        set_ids = []
        for row in ret:
            set_ids.append(int(row[0]))

        if len(set_ids) == 0:
            return

        words = []
        defns = []
        print()
        choices = input("Enter the sets you want to study: ")
        choices = choices.split(", ")
        for choice in choices:
            if not (choice.isdigit() and int(choice) > 0
                    and int(choice) <= len(set_ids)):
                print("Invalid choice: '" + choice + "'. Exiting.")
                return
            set_id = set_ids[int(choice) - 1]
            words.extend(self.__dbm.get_words(set_id)[0])
            defns.extend(self.__dbm.get_words(set_id)[1])

        self.__list_words(words, defns)
        print()
        rounds = input("Enter the number of rounds you want to play.")
        if not rounds.isdigit():
            rounds = 2
        else:
            rounds = int(rounds)
        print("Press any key to start playing with these " + str(len(words)) +
              " words.")
        input("During the game, press 'q' to quit at any time.")
        write = Write(words, defns, rounds)
        ret = write.play_game()
        if ret == -2:
            self.__dbm.pickle(self.__user_id, write)