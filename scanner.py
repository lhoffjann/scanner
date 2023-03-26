"""This is a scan-script which starts the scan program NAPS2 and shows the result with IrfanView.
It also writes the manuscript id to a file to check if it was scanned before.
at the end it creates a Gitlab-issue."""

from __future__ import print_function, unicode_literals
import os
import gitlab
from dotenv import load_dotenv

load_dotenv()
GITLAB_URL = os.getenv('GITLAB_URL')
GITLAB_TOKEN = os.getenv('GITLAB_TOKEN')
GITLAB = gitlab.Gitlab(GITLAB_URL, private_token=GITLAB_TOKEN)
GITLAB.auth()
GITLAB_PROJECT_ID: int = int(os.getenv('GITLAB_PROJECT_ID'))
ms_project = GITLAB.projects.get(GITLAB_PROJECT_ID)
ms_issues = ms_project.issues.list(get_all=False)
ASSIGNEE_ID: int = int(os.getenv('ASSIGNEE_ID'))
SCANNED_DOCUMENTS = os.getenv('SCANNED_DOCUMENTS')
try:
    with open(SCANNED_DOCUMENTS, "x") as f:
        pass
except FileExistsError:
    pass


def main():
    """Starts the main-loop and keeps running till the user stops the program"""
    while True:
        start_scan_process(get_ms_id_from_user())


def get_ms_id_from_user() -> str:
    """
    Gets the MS-ID of the to be scanned manuscript from the user.
    :return: ms_id
    """
    ms_id = input("Which MS_ID do you want to scan?: ")
    return ms_id


def start_scan_process(ms_id: str) -> None:
    """
    Checks if MS-ID was scanned before.
    If it was not scanned it starts scanning, creating the Gitlab Issue,
    and adds the MS-ID to the scanned_documents_file.
    Otherwise, it asks if the file should just be scanned or do nothing.
    :param ms_id:
    :return:
    """
    if not is_document_scanned(ms_id):
        scan_and_show_ms(ms_id)
        create_gitlab_issue(ms_id)
        add_scanned_document(ms_id)
    else:
        val = input("The Issue already exist."
                    " Want to scan it again without creating a gitlab-issue? (y/N): ")
        if val == "y":
            scan_and_show_ms(ms_id)


def scan_and_show_ms(ms_id: str) -> None:
    """
    starts NAPS2 and afterwards IrfanView to check the scan quality.
    Repeats this till the user is satisfied with the result.
    :param ms_id:
    :return:
    """
    while True:
        try:
            print(create_command_to_start_naps2(ms_id))
            os.system(create_command_to_start_naps2(ms_id))
        except Exception:
            print('could not start NAPS.')
        try:
            print(create_command_to_start_irfan_view(ms_id))
            os.system(create_command_to_start_irfan_view(ms_id))
        except Exception:
            print('could not start IrfanView.')

        val = input("is the scan okay? (y/n): ")
        if val == "y":
            break


def create_command_to_start_naps2(ms_id: str) -> str:
    """
    concat the naps command with the ms_id
    :param ms_id:
    :return: naps command
    """
    return """"
        C:\\"Program Files (x86)"\\NAPS2\\NAPS2.Console.exe -o O:\\manuskripte_scans_fuer_digitalisierung\\scans\\MS_""" \
        + ms_id \
        + """\\MS_" + ms_id + "_$(nnnn)_.tif --tiffcomp none --split"""


def create_command_to_start_irfan_view(ms_id: str) -> str:
    """
        concat the irfanView command with the ms_id
        :param ms_id:
        :return: naps command
        """

    return """START C:\\"Program Files"\\IrfanView\\i_view64.exe""" \
        + " O:\\manuskripte_scans_fuer_digitalisierung\\scans\\MS_" \
        + ms_id + "\\MS_" + ms_id + "_0001_.tif"


def create_gitlab_issue(ms_id: str) -> None:
    """
    Creates the Gitlab Issue.
    :param ms_id:
    :return:
    """
    with open("issue_content.txt") as file:
        issue_note = file.read()
    issue_dict = {'title': f'MS_{ms_id}', 'description': issue_note}
    issue = ms_project.issues.create(issue_dict)
    issue.assignee_id = ASSIGNEE_ID
    issue.save()


def add_scanned_document(ms_id: str) -> None:
    """
    adds the ms_id to file that keeps track
    :param ms_id:
    :return:
    """
    with open(SCANNED_DOCUMENTS, "a") as file:
        file.write(ms_id + "\n")


def is_document_scanned(ms_id: str) -> bool:
    """
    checks if the manuscript was already scanned.
    :param ms_id:
    :return:
    """
    with open(SCANNED_DOCUMENTS, "r") as file:
        for line in file:
            if ms_id == line.strip():
                return True
    return False


if __name__ == "__main__":
    main()
