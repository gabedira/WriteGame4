import random
from colorama import Fore
from colorama import Style
import os


class Write:
    def __init__(self, words, defns):
        self.__num_per_epoch = 7
        self.__N = len(words)
        self.__words = words
        self.__defns = defns
        self.__prog = [0] * self.__N
        self.__state0 = [i for i in range(self.__N)]
        self.__state1 = []
        self.__state2 = []
        self.__total_rounds = 0
        self.__correct_responses = 0
        self.__times_missed = [0] * self.__N
        self.__num_question = 1

    def __play_epoch(self):
        m0 = min(len(self.__state0), self.__num_per_epoch)
        m1 = min(self.__num_per_epoch - m0, len(self.__state1))
        random.shuffle(self.__state0)
        random.shuffle(self.__state1)

        epoch_words = self.__state0[0:m0]
        self.__state0 = self.__state0[m0:]

        epoch_words.extend(self.__state1[0:m1])
        self.__state1 = self.__state1[m1:]
        random.shuffle(epoch_words)

        for i in epoch_words:
            ret = self.__play_round(i)
            if ret == -1:
                return -1

        self.__print_end_of_epoch(epoch_words)

    def __print_end_of_epoch(self, epoch_words):
        os.system('cls' if os.name == 'nt' else 'clear')
        print('=' * 40)
        print("Unseen:   " + str(len(self.__state0)) + " | Learning: " +
              str(len(self.__state1)) + " | Mastered: " +
              str(len(self.__state2)))
        print()

        for i in epoch_words:
            print(f"{Fore.GREEN}●{Style.RESET_ALL}" * self.__prog[i], end="")
            print(f"{Fore.GREEN}○{Style.RESET_ALL}" * (2 - self.__prog[i]),
                  end="")
            print(f"{Fore.GREEN}  {Style.RESET_ALL}", end="")
            if self.__prog[i] == 0:
                print(
                    f"{Fore.RED}{self.__words[i]}\t{self.__defns[i]}{Style.RESET_ALL}"
                )
            else:
                print(
                    f"{Fore.GREEN}{self.__words[i]}\t{self.__defns[i]}{Style.RESET_ALL}"
                )

        print('=' * 40)
        print()
        input("Type any key to go on.")

    def __play_round(self, i):
        os.system('cls' if os.name == 'nt' else 'clear')

        player_word = input(
            str(self.__num_question) + ". " + self.__defns[i] + ':\n').strip()
        self.__num_question += 1
        if player_word == 'q':
            return -1
        if player_word != self.__words[i]:
            player_response = input("Correct answer: " + self.__words[i] +
                                    ': ').strip()
            if player_response != 's':
                self.__prog[i] = 0
                self.__state0.append(i)
                self.__times_missed[i] += 1

                if player_response != self.__words[i]:
                    while True:
                        player_response = input("Write " + self.__words[i] +
                                                ": ").strip()
                        if player_response == self.__words[i]:
                            break

            else:
                player_word = self.__words[i]

        if player_word == self.__words[i]:
            self.__prog[i] += 1
            if self.__prog[i] == 1:
                self.__state1.append(i)
            else:
                self.__state2.append(i)
            self.__correct_responses += 1
        print()
        self.__total_rounds += 1

    def play_game(self):
        while len(self.__state2) != self.__N:
            ret = self.__play_epoch()
            if ret == -1:
                return -1
        self.__end_text()

    def __end_text(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Accuracy: " + str(self.__correct_responses * 100 // self.__total_rounds) + "%")
        
        max_missed = max(self.__times_missed)
        
        sorted_missed = []
        for i in range(max_missed+1):
            sorted_missed.append([])
        
        for i in range(self.__N):
            sorted_missed[self.__times_missed[i]].append(i)
        
        for i in reversed(range(len(sorted_missed))):
            if len(sorted_missed[i]) == 0:
                continue
            
            if i > 1:
                print("\nMissed " + str(i) + " times: ")
            elif i == 1:
                print("\nMissed 1 time:")
            else:
                print("\nNever missed:")

            for j in sorted_missed[i]:
                print(self.__words[j] + '\t' + self.__defns[j])
