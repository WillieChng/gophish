var groups = []

// Risk profile configuration mapping icons and colors
var riskConfig = {
    risk_urgency: { icon: 'fa-clock-o', label: 'Urgency' },
    risk_suspicious_links: { icon: 'fa-link', label: 'Suspicious Links' },
    risk_generic_greeting: { icon: 'fa-user', label: 'Generic Greeting' },
    risk_suspicious_sender: { icon: 'fa-envelope', label: 'Suspicious Sender' },
    risk_attachments: { icon: 'fa-paperclip', label: 'Attachments' },
    risk_spelling_errors: { icon: 'fa-text-width', label: 'Spelling Errors' }
}

var riskColors = {
    low: '#5cb85c',
    medium: '#f0ad4e',
    high: '#d9534f'
}

// Generate risk profile blocks visualization
function generateRiskBlocks(item) {
    var html = '<div style="display: flex; gap: 4px; flex-wrap: wrap;">'
    var risks = ['risk_urgency', 'risk_suspicious_links', 'risk_generic_greeting',
                 'risk_suspicious_sender', 'risk_attachments', 'risk_spelling_errors']

    risks.forEach(function(risk) {
        var level = item[risk] || 'medium'
        var config = riskConfig[risk]
        var color = riskColors[level]
        html += '<div style="background-color: ' + color + '; width: 28px; height: 28px; border-radius: 4px; ' +
                'display: flex; align-items: center; justify-content: center; color: white;" ' +
                'title="' + config.label + ': ' + level.charAt(0).toUpperCase() + level.slice(1) + '">' +
                '<i class="fa ' + config.icon + '" style="font-size: 12px;"></i></div>'
    })

    html += '</div>'
    return html
}

// Save attempts to POST or PUT to /groups/
function save(id) {
    var targets = []
    $.each($("#targetsTable").DataTable().rows().data(), function (i, target) {
        targets.push({
            first_name: unescapeHtml(target[0]),
            last_name: unescapeHtml(target[1]),
            email: unescapeHtml(target[2]),
            position: unescapeHtml(target[3])
        })
    })
    var group = {
        name: $("#name").val(),
        targets: targets,
        risk_urgency: $('[data-risk="risk_urgency"].active').data('value') || 'medium',
        risk_suspicious_links: $('[data-risk="risk_suspicious_links"].active').data('value') || 'medium',
        risk_generic_greeting: $('[data-risk="risk_generic_greeting"].active').data('value') || 'medium',
        risk_suspicious_sender: $('[data-risk="risk_suspicious_sender"].active').data('value') || 'medium',
        risk_attachments: $('[data-risk="risk_attachments"].active').data('value') || 'medium',
        risk_spelling_errors: $('[data-risk="risk_spelling_errors"].active').data('value') || 'medium'
    }
    // Submit the group
    if (id != -1) {
        // If we're just editing an existing group,
        // we need to PUT /groups/:id
        group.id = id
        api.groupId.put(group)
            .success(function (data) {
                successFlash("Group updated successfully!")
                load()
                dismiss()
                $("#modal").modal('hide')
            })
            .error(function (data) {
                modalError(data.responseJSON.message)
            })
    } else {
        // Else, if this is a new group, POST it
        // to /groups
        api.groups.post(group)
            .success(function (data) {
                successFlash("Group added successfully!")
                load()
                dismiss()
                $("#modal").modal('hide')
            })
            .error(function (data) {
                modalError(data.responseJSON.message)
            })
    }
}

function dismiss() {
    $("#targetsTable").dataTable().DataTable().clear().draw()
    $("#name").val("")
    $("#modal\\.flashes").empty()
    // Reset risk buttons to medium
    resetRiskButtons()
}

function resetRiskButtons() {
    $('.risk-btn').removeClass('active')
    $('.risk-btn[data-value="medium"]').addClass('active')
}

function setRiskButton(riskType, value) {
    $('.risk-btn[data-risk="' + riskType + '"]').removeClass('active')
    $('.risk-btn[data-risk="' + riskType + '"][data-value="' + value + '"]').addClass('active')
}

function edit(id) {
    targets = $("#targetsTable").dataTable({
        destroy: true, // Destroy any other instantiated table - http://datatables.net/manual/tech-notes/3#destroy
        columnDefs: [{
            orderable: false,
            targets: "no-sort"
        }]
    })
    $("#modalSubmit").unbind('click').click(function () {
        save(id)
    })
    if (id == -1) {
        $("#groupModalLabel").text("New Group");
        resetRiskButtons()
        var group = {}
    } else {
        $("#groupModalLabel").text("Edit Group");
        api.groupId.get(id)
            .success(function (group) {
                $("#name").val(group.name)

                // Load risk profile values
                setRiskButton('risk_urgency', group.risk_urgency || 'medium')
                setRiskButton('risk_suspicious_links', group.risk_suspicious_links || 'medium')
                setRiskButton('risk_generic_greeting', group.risk_generic_greeting || 'medium')
                setRiskButton('risk_suspicious_sender', group.risk_suspicious_sender || 'medium')
                setRiskButton('risk_attachments', group.risk_attachments || 'medium')
                setRiskButton('risk_spelling_errors', group.risk_spelling_errors || 'medium')

                targetRows = []
                $.each(group.targets, function (i, record) {
                  targetRows.push([
                      escapeHtml(record.first_name),
                      escapeHtml(record.last_name),
                      escapeHtml(record.email),
                      escapeHtml(record.position),
                      '<span style="cursor:pointer;"><i class="fa fa-trash-o"></i></span>'
                  ])
                });
                targets.DataTable().rows.add(targetRows).draw()
            })
            .error(function () {
                errorFlash("Error fetching group")
            })
    }
    // Handle file uploads
    $("#csvupload").fileupload({
        url: "/api/import/group",
        dataType: "json",
        beforeSend: function (xhr) {
            xhr.setRequestHeader('Authorization', 'Bearer ' + user.api_key);
        },
        add: function (e, data) {
            $("#modal\\.flashes").empty()
            var acceptFileTypes = /(csv|txt)$/i;
            var filename = data.originalFiles[0]['name']
            if (filename && !acceptFileTypes.test(filename.split(".").pop())) {
                modalError("Unsupported file extension (use .csv or .txt)")
                return false;
            }
            data.submit();
        },
        done: function (e, data) {
            $.each(data.result, function (i, record) {
                addTarget(
                    record.first_name,
                    record.last_name,
                    record.email,
                    record.position);
            });
            targets.DataTable().draw();
        }
    })
}

var downloadCSVTemplate = function () {
    var csvScope = [{
        'First Name': 'Example',
        'Last Name': 'User',
        'Email': 'foobar@example.com',
        'Position': 'Systems Administrator'
    }]
    var filename = 'group_template.csv'
    var csvString = Papa.unparse(csvScope, {})
    var csvData = new Blob([csvString], {
        type: 'text/csv;charset=utf-8;'
    });
    if (navigator.msSaveBlob) {
        navigator.msSaveBlob(csvData, filename);
    } else {
        var csvURL = window.URL.createObjectURL(csvData);
        var dlLink = document.createElement('a');
        dlLink.href = csvURL;
        dlLink.setAttribute('download', filename)
        document.body.appendChild(dlLink)
        dlLink.click();
        document.body.removeChild(dlLink)
    }
}


var deleteGroup = function (id) {
    var group = groups.find(function (x) {
        return x.id === id
    })
    if (!group) {
        return
    }
    Swal.fire({
        title: "Are you sure?",
        text: "This will delete the group. This can't be undone!",
        type: "warning",
        animation: false,
        showCancelButton: true,
        confirmButtonText: "Delete " + escapeHtml(group.name),
        confirmButtonColor: "#428bca",
        reverseButtons: true,
        allowOutsideClick: false,
        preConfirm: function () {
            return new Promise(function (resolve, reject) {
                api.groupId.delete(id)
                    .success(function (msg) {
                        resolve()
                    })
                    .error(function (data) {
                        reject(data.responseJSON.message)
                    })
            })
        }
    }).then(function (result) {
        if (result.value){
            Swal.fire(
                'Group Deleted!',
                'This group has been deleted!',
                'success'
            );
        }
        $('button:contains("OK")').on('click', function () {
            location.reload()
        })
    })
}

function addTarget(firstNameInput, lastNameInput, emailInput, positionInput) {
    // Create new data row.
    var email = escapeHtml(emailInput).toLowerCase();
    var newRow = [
        escapeHtml(firstNameInput),
        escapeHtml(lastNameInput),
        email,
        escapeHtml(positionInput),
        '<span style="cursor:pointer;"><i class="fa fa-trash-o"></i></span>'
    ];

    // Check table to see if email already exists.
    var targetsTable = targets.DataTable();
    var existingRowIndex = targetsTable
        .column(2, {
            order: "index"
        }) // Email column has index of 2
        .data()
        .indexOf(email);
    // Update or add new row as necessary.
    if (existingRowIndex >= 0) {
        targetsTable
            .row(existingRowIndex, {
                order: "index"
            })
            .data(newRow);
    } else {
        targetsTable.row.add(newRow);
    }
}

function load() {
    $("#groupTable").hide()
    $("#emptyMessage").hide()
    $("#loading").show()
    api.groups.summary()
        .success(function (response) {
            $("#loading").hide()
            if (response.total > 0) {
                groups = response.groups
                $("#emptyMessage").hide()
                $("#groupTable").show()
                var groupTable = $("#groupTable").DataTable({
                    destroy: true,
                    columnDefs: [{
                        orderable: false,
                        targets: "no-sort"
                    }]
                });
                groupTable.clear();
                groupRows = []
                $.each(groups, function (i, group) {
                    groupRows.push([
                        escapeHtml(group.name),
                        escapeHtml(group.num_targets),
                        generateRiskBlocks(group),
                        moment(group.modified_date).format('MMMM Do YYYY, h:mm:ss a'),
                        "<div class='pull-right'><button class='btn btn-primary' data-toggle='modal' data-backdrop='static' data-target='#modal' onclick='edit(" + group.id + ")'>\
                    <i class='fa fa-pencil'></i>\
                    </button>\
                    <button class='btn btn-danger' onclick='deleteGroup(" + group.id + ")'>\
                    <i class='fa fa-trash-o'></i>\
                    </button></div>"
                    ])
                })
                groupTable.rows.add(groupRows).draw()
            } else {
                $("#emptyMessage").show()
            }
        })
        .error(function () {
            errorFlash("Error fetching groups")
        })
}

$(document).ready(function () {
    load()
    // Setup the event listeners
    // Handle manual additions
    $("#targetForm").submit(function () {
        // Validate the form data
        var targetForm = document.getElementById("targetForm")
        if (!targetForm.checkValidity()) {
            targetForm.reportValidity()
            return
        }
        addTarget(
            $("#firstName").val(),
            $("#lastName").val(),
            $("#email").val(),
            $("#position").val());
        targets.DataTable().draw();

        // Reset user input.
        $("#targetForm>div>input").val('');
        $("#firstName").focus();
        return false;
    });
    // Handle Deletion
    $("#targetsTable").on("click", "span>i.fa-trash-o", function () {
        targets.DataTable()
            .row($(this).parents('tr'))
            .remove()
            .draw();
    });
    $("#modal").on("hide.bs.modal", function () {
        dismiss();
    });
    $("#csv-template").click(downloadCSVTemplate)

    // Handle risk button clicks
    $(document).on('click', '.risk-btn', function() {
        var riskType = $(this).data('risk')
        $('.risk-btn[data-risk="' + riskType + '"]').removeClass('active')
        $(this).addClass('active')
    })
});
