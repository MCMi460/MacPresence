# Made by Deltaion Lee (MCMi460) on GitHub
from . import *

def main():
    cli:Client = Client(int(input('Enter your Client ID\n> ')))

    example_presence:Presence = Presence(
        state = input('Your state\n> '),
        details = input('Your details\n> '),
        instance = True,
    )

    while True:
        print(cli.update(example_presence))
        time.sleep(5)

if __name__ == '__main__':
    main()
