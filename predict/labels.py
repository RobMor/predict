import datetime
import itertools

import predict.db


def load_recent(username):
    """Loads the 10 most recent labels by the given user

    Args:
        username: A string value of the current user
    Returns:
        A dictionary mapping CVE IDs to labels
    """
    labels = (
        predict.db.Session.query(predict.models.Label)
        .filter_by(username=username)
        .order_by(predict.models.Label.edit_date)
        .limit(10)
        .all()
    ) or []

    return itertools.groupby(labels, key=lambda l: l.cve_id)


def load_label(cve_id, username, repo_user, repo_name, fix_file, intro_file):
    """Loads the label with the given primary key information.

    Possibly returns labels that have no intro file. This is meant to allow for
    replacement of the intro files in these labels.

    Args:
        cve (str): The CVE ID to find
        username (str): The username to find
        repo_user (str): The repository user to find
        repo_name (str): The repository name to find
        intro_file (str): The intro file to find
        fix_file (str): The fix file to find
    """
    query = predict.db.Session.query(predict.models.Label).filter_by(
        cve_id=cve_id,
        username=username,
        repo_user=repo_user,
        repo_name=repo_name,
        fix_file=fix_file,
    )

    label = query.filter_by(intro_file=intro_file).first()
    if label is not None:
        return label
    else:
        return query.filter_by(intro_file=None).first()


def process_labels(cve_id, username, labels, edit_date):
    """Creates or updates a label.

    Args:
        cve_id (str): The CVE ID for these labels
        username (str): The username for these labels
        labels (list of dicts): The labels to process
        edit_date (datetime): The edit date for these labels

    Returns:
        True - The label was created or updated
        False - The label could not be created
    """
    # Delete the users current labels.
    predict.db.Session.query(predict.models.Label).filter_by(cve_id=cve_id, username=username).delete()

    # Replace them with the new labels.
    for label in labels:
        new_label = predict.models.Label(
            cve_id=cve_id,
            username=username,
            repo_user=label["repo_user"],
            repo_name=label["repo_name"],
            fix_file=label["fix_file"],
            fix_hash=label["fix_hash"],
            intro_file=label["intro_file"],
            intro_hash=label["intro_hash"],
            comment=label["comment"],
            edit_date=edit_date,
        )

        predict.db.Session.add(new_label)
        predict.db.Session.commit()

    return True


def create_test_labels(username):
    """Creates a list of label objects in database if it doesn't exist already

    Args:
        username (str): The username to create dummy labels for
    """
    for i in range(5):
        process_labels(
            cve_id=f"CVE-2019-000{i}",
            username=username,
            labels=[{
                "repo_user": str(i),
                "repo_name": str(i + 1),
                "fix_file": str(i + 2),
                "fix_hash": str(i + 3),
                "intro_file": str(i + 4),
                "intro_hash": str(i + 5),
                "comment": str(i + 6),
            }],
            edit_date=datetime.datetime.now(),
        )
        if i % 2 == 0:
            process_labels(
                cve_id=f"CVE-2019-000{i}",
                username=username,
                labels=[{
                    "repo_user": str(2 * i),
                    "repo_name": str(2 * i + 1),
                    "fix_file": str(2 * i + 2),
                    "fix_hash": str(2 * i + 3),
                    "intro_file": str(2 * i + 4),
                    "intro_hash": str(2 * i + 5),
                    "comment": str(2 * i + 6),
                }],
                edit_date=datetime.datetime.now(),
            )
