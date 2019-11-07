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


def process_label(
    cve_id,
    username,
    repo_user,
    repo_name,
    fix_file,
    fix_hash,
    intro_file,
    intro_hash,
    comment,
    edit_date,
):
    """Creates or updates a label.

    Args:
        cve_id (str): The CVE ID for this label
        username (str): The username for this label
        fix_file (str): The fix file for this label
        fix_hash (str): The fix hash for this label
        intro_file (str): The intro file for this label
        intro_hash (str): The intro hash for this label
        edit_date (datetime): The edit date for this label

    Returns:
        True - The label was created or updated
        False - The label could not be created
    """
    if None not in [cve_id, username, repo_user, repo_name, fix_file]:
        current_label = load_label(
            cve_id=cve_id,
            username=username,
            repo_user=repo_user,
            repo_name=repo_name,
            fix_file=fix_file,
            intro_file=intro_file,
        )

        if current_label is None:
            new_label = predict.models.Label(
                cve_id=cve_id,
                username=username,
                repo_user=repo_user,
                repo_name=repo_name,
                fix_file=fix_file,
                fix_hash=fix_hash,
                intro_file=intro_file,
                intro_hash=intro_hash,
                comment=comment,
                edit_date=edit_date,
            )

            predict.db.Session.add(new_label)
            predict.db.Session.commit()

            return True
        else:
            current_label.fix_hash = fix_hash
            if intro_file is not None and intro_hash is not None:
                current_label.intro_file = intro_file
                current_label.intro_hash = intro_hash
            current_label.comment = comment
            current_label.edit_date = edit_date

            predict.db.Session.commit()

            return True
    else:
        return False


def create_test_labels(username):
    """Creates a list of label objects in database if it doesn't exist already

    Args:
        username (str): The username to create dummy labels for
    """
    for i in range(5):
        process_label(
            cve_id=f"CVE-2019-000{i}",
            username=username,
            repo_user=str(i),
            repo_name=str(i + 1),
            fix_file=str(i + 2),
            fix_hash=str(i + 3),
            intro_file=str(i + 4),
            intro_hash=str(i + 5),
            comment=str(i + 6),
            edit_date=datetime.datetime.now(),
        )
        if i % 2 == 0:
            process_label(
                cve_id=f"CVE-2019-000{i}",
                username=username,
                repo_user=str(2 * i),
                repo_name=str(2 * i + 1),
                fix_file=str(2 * i + 2),
                fix_hash=str(2 * i + 3),
                intro_file=str(2 * i + 4),
                intro_hash=str(2 * i + 5),
                comment=str(2 * i + 6),
                edit_date=datetime.datetime.now(),
            )
