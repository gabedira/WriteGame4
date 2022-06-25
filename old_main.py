import os
import csv
from write import Write

def main(): 
  files = []
  
  for file in os.listdir():
    if file.endswith(".csv"):
      files.append(file)
  
  files.sort()
  print("Available Files: ")
  for i, file in enumerate(files):
    print(str(i+1) + ": " + file)
  
  choice = input("\nSelect the ones you want to study: ")
  choices = choice.split(", ")
  words = []
  defns = []
  
  for choice in choices:
    i = int(choice)
    with open(files[i-1], newline='') as csvfile:
      reader = csv.reader(csvfile, delimiter=',', quotechar='"')
      for row in reader:
        words.append(row[0].strip())
        defns.append(row[1].strip())
  
  N = len(words)
  print("Starting write with " + str(N) + " words: ")
  print()
  input("Type 's' if you misspell a word to not lose progress. Press any key to go on.")
  
  write = Write(words, defns)
  write.play_game()
  return 0
