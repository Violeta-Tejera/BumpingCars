from time import sleep

def main():
  count = 1
  while True:
    print(f"Printed {count} times")
    sleep(1)
    
    count += 1


if __name__ == "__main__":
  print() # \n

  main()