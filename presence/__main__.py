# Made by Deltaion Lee (MCMi460) on GitHub
from . import Client, Presence, ActivityType, StatusDisplayType
from time import time, sleep


def main():
    cli: Client = Client(int(input("Enter your Client ID\n> ")))

    example_presence: Presence = Presence(
        state=input("Your state\n> "),
        details=input("Your details\n> "),
        details_url="https://google.com/",
        large_url="https://google.com/",
        start=time() - 300,  # Five minutes ago
        end=time() + 300,  # In five minutes
        large_image="https://github.com/fluidicon.png",
        large_text="Awesome GitHub logo",
        type=ActivityType.PLAYING,
        status_display_type=StatusDisplayType.STATE,
        party_id="RANDOM PARTY STRING",
        party_size=(1, 2),
        join="JOIN SECRET",
        # buttons = [{
        #    'label': 'This is Google!',
        #    'url': 'https://google.com/',
        # },],
        instance=True,
    )

    def handle_join_request(header, data):
        print(header)
        print(data)

    cli.IPC._subscribe("ACTIVITY_JOIN_REQUEST", handle_join_request)
    # cli.IPC._unsubscribe('ACTIVITY_JOIN_REQUEST')

    while True:
        print(cli.update(example_presence))
        sleep(5)
    print(cli.update(None))


if __name__ == "__main__":
    main()
