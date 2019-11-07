import predict.db
import datetime
def load_recent_labels(username):
    """
        Loads from the database up to 10 of the most recent labels by the current user

        Args:
            username: A string value of the current user
        Returns:
            labels: A sql query output
            None: None
    """
    if username is not None:
        labels = (
            predict.db.Session.query(predict.models.Label)
            .filter_by(username=username)
            .order_by(predict.models.Label.edit_date)
            .limit(10)
            .all()
        )
        return labels
    else:
        return None

def load_label(cve,username,intro_file, fix_file):
    """
        Loads the label with the input primary key from database, primary keys
        are unique so no two labels with same primary key will exist

        Args:
            cve: A string of the cve name
            username: A string of the username
            intro_file: A string of intro_file
            fix_file: A string of fix_file
    """
    current_label = (
        predict.db.Session.query(predict.models.Label)
        .filter_by(cve = cve)
        .filter_by(username = username)
        .filter_by(intro_file = intro_file)
        .filter_by(fix_file = fix_file)
        .scalar()
    )
    return current_label

def create_label(args):
    """
        Creates the label with args if it doesn't exist already in database

        Args:
            args: A dictionary with keys to properties of Label model object
                Example - {"cve": "sample_cve_id", "username":"sample_name"}

        Returns:
            True - The label did not exist and was created
            False - The label was not created
    """

    # The 4 parts of primary key here
    cve = args.get("cve", "")
    username = args.get("username", "")
    intro_file = args.get("into_file", "")
    fix_file = args.get("fix_file", "")

    # Other properties
    intro_hash = args.get("intro_hash", "")
    fix_hash = args.get("fix_hash", "")
    repo_name = args.get("repo_name", "")
    repo_user = args.get("repo_user", "")
    edit_date = args.get("edit_date", datetime.datetime.now())

    # Going to see if label with primary key already exists
    current_label = load_label(cve,username,intro_file,fix_file)

    if current_label is None:
        new_label = predict.models.Label()
        new_label.cve = cve
        new_label.username = username
        new_label.intro_file = intro_file
        new_label.fix_file = fix_file
        new_label.intro_hash = intro_hash
        new_label.fix_hash = fix_hash
        new_label.repo_name = repo_name
        new_label.repo_user = repo_user
        new_label.edit_date = edit_date
        predict.db.Session.add(new_label)
        predict.db.Session.commit()
        print("Created new_label: "+ str(new_label))
        return True
    else:
        return False

def create_test_labels(args_list):
    """
        Creates a list of label objects in database if it doesn't exist already

        Input:
            args_list: A list of args. Each arg is a dictionary of label properties
                Example - [{"cve":"124", "username":"namerandom"}, {"cve":"bobs"}]
        Returns:
            prints out "Created test labels"
    """
    for i in range(0,len(args_list)):
        create_label(args_list[i])

    print("Created test labels")
