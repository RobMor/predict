// TODO
function getLine(node) {
    if (node.nodeType === Node.ELEMENT_NODE) {
        return node.closest("tr.line")
    } else {
        return node.parentElement.closest("tr.line")
    }
}

// TODO
function catchSelection(event) {
    selection = window.getSelection();

    anchorLine = getLine(selection.anchorNode)
    focusLine = getLine(selection.focusNode)
}

// TODO
document.addEventListener("selectionchange", catchSelection)

function introducesVulnerability(cve_id, repo_name, repo_user, intro_file, intro_hash) {
    // TODO need to prompt user for fix file and fix hash here...
    createLabel(cve_id, repo_name, repo_user, null, null, intro_file, intro_hash, null)
}

function fixesVulnerability(cve_id, repo_name, repo_user, fix_file, fix_hash) {
    createLabel(cve_id, repo_name, repo_user, fix_file, fix_hash, null, null, null)
}


function createLabel(cve_id, repo_name, repo_user, fix_file, fix_hash, intro_file, intro_hash, comment) {
    params = new FormData()
    params.append("cve_id", cve_id)
    params.append("repo_name", repo_name)
    params.append("repo_user", repo_user)
    params.append("fix_file", fix_file)
    params.append("fix_hash", fix_hash)
    params.append("intro_file", intro_file)
    params.append("intro_hash", intro_hash)
    params.append("comment", comment)

    request = new XMLHttpRequest();
    request.open("POST", "/create/label")
    
    request.onreadystatechange = labelCreated(request);
    
    request.send(params)
}

function labelCreated(request) {
    return function () {
        if (request.readyState == XMLHttpRequest.DONE) {
            if (request.status = 200) {
                labelCreationSucceeded(request)
            } else {
                labelCreationFailed(request)
            }
        }
    }
}

function labelCreationSucceeded(request) {
    data = JSON.parse(request.responseText)

    data.forEach(function (label) {
        console.log(label)
    })
}

function labelCreationFailed(request) {
    alert("Failed to create label")
}
