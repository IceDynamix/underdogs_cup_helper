from ucBot import ucBot


def token() -> str:
    with open("token.secret") as tokenFile:
        return tokenFile.read()


if __name__ == "__main__":
    ucBot.run(token())
