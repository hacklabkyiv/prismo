from slack_sdk import WebClient

from app.config import get_setting, slack_token_key, slack_backup_channel_key, database_file


def backup_data_base():
    slack_token = get_setting(slack_token_key)
    channel_id = get_setting(slack_backup_channel_key)

    if (slack_token is None) or (channel_id is None):
        return

    client = WebClient(token=slack_token)

    response = client.files_upload_v2(
        channel=channel_id,
        file=open(database_file, "rb").read(),
        title="Database backup",
        initial_comment="Here is the latest version of the database.",
    )

    print(response)
