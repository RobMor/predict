function updateLabels(cve_id, labels, successCallback, failureCallback) {
    data = {
        cve_id: cve_id,
        labels: labels,
    }

    $.ajax({
        type: "PUT",
        url: rootUrl + "label", 
        data: JSON.stringify(data),
        contentType: "application/json",
        success: successCallback,
        error: failureCallback
    })
}
