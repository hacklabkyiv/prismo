from slack_sdk import WebClient

client = WebClient(token='xoxb-156594252659-6059712941424-4SnYb71awW0Mo0iV7Y9bm4Jb')

if __name__ == '__main__':
    response = client.files_upload_v2(
        channel="C8Z6P3QRF",
        file="../database.db",
        title="Database backup",
        initial_comment="Here is the latest version of the database.",
    )

    print(response)
