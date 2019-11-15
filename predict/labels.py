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
        .order_by(predict.models.Label.cve_id,predict.models.Label.edit_date)
        .limit(10)
        .all()
    ) or []
    """
    Itertools groupby usage example:
    Input: list= ["a","a", "b", "b", "c", "a"]
    Output:
        group a: "a", "a"
        group b: "b", "b"
        group c: "c"
        group a: "a"
    Hence need to order labels before passing it in
    """
    return itertools.groupby(labels, key=lambda l: l.cve_id)


def load_labels(cve_id, username):
    """Loads the label with the given information grouped by repository.

    Args:
        cve (str): The CVE ID to find
        username (str): The username to find
    """
    labels = predict.db.Session.query(predict.models.Label).filter_by(
        cve_id=cve_id,
        username=username,
    ).all()

    return itertools.groupby(labels, key=lambda l: (l.group_num, l.repo_user, l.repo_name))


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
            group_num=label["group_num"],
            label_num=label["label_num"],
            repo_user=label.get("repo_user"),
            repo_name=label.get("repo_name"),
            fix_file=label.get("fix_file"),
            fix_hash=label.get("fix_hash"),
            intro_file=label.get("intro_file"),
            intro_hash=label.get("intro_hash"),
            comment=label.get("comment"),
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
    for i in range(1,6):
        labels = [{
            "group_num": 0,
            "label_num": 0,
            "repo_user": str(i),
            "repo_name": str(i + 1),
            "fix_file": str(i + 2),
            "fix_hash": str(i + 3),
            "intro_file": str(i + 4),
            "intro_hash": str(i + 5),
            "comment": str(i + 6),
        }]

        if i % 2 == 0:
            labels.append({
                "group_num": 1,
                "label_num": 0,
                "repo_user": str(2 * i),
                "repo_name": str(2 * i + 1),
                "fix_file": str(2 * i + 2),
                "fix_hash": str(2 * i + 3),
                "intro_file": str(2 * i + 4),
                "intro_hash": str(2 * i + 5),
                "comment": str(2 * i + 6),
            })
        
        process_labels(
            cve_id=f"CVE-2019-000{i}",
            username=username,
            labels=labels,
            edit_date=datetime.datetime.now(),
        )
