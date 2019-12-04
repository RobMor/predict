import requests


URL = "http://localhost:5000"


def register(session, username, password="password"):
    return session.post(URL + "/register", data={
        "username": username,
        "password": password,
        "confirm": password,
    })


def login(session, username, password="password"):
    return session.post(URL + "/login", data={
        "username": username,
        "password": password,
    })


def label(session, cve_id, labels):
    return session.put(URL + "/label", json={
        "cve_id": cve_id,
        "labels": labels,
    })


if __name__ == "__main__":
    sessions = []
    for i in range(1, 21):
        s = requests.Session()
        username = "test{:02}".format(i)
        print("Loading", username)
        register(s, username)
        login(s, username)
        print("Loaded", username)

        sessions.append(s)

    for i in range(100):
        print("Starting round of queries {}".format(i+1))
        for j, s in enumerate(sessions):
            label(s, "CVE-{:04}-{:04}".format(i, i),
                [{
                    "group_num": 0,
                    "label_num": 0,
                    "repo_name": i+j,
                    "repo_user": i+j,
                    "intro_file": i+j,
                    "intro_hash": i+j,
                    "fix_file": i+j,
                    "fix_hash": i+j,
                }]
            )

