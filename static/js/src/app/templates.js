var templates = []
var icons = {
    "application/vnd.ms-excel": "fa-file-excel-o",
    "text/plain": "fa-file-text-o",
    "image/gif": "fa-file-image-o",
    "image/png": "fa-file-image-o",
    "application/pdf": "fa-file-pdf-o",
    "application/x-zip-compressed": "fa-file-archive-o",
    "application/x-gzip": "fa-file-archive-o",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "fa-file-powerpoint-o",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "fa-file-word-o",
    "application/octet-stream": "fa-file-o",
    "application/x-msdownload": "fa-file-o"
}

// Save attempts to POST to /templates/
function save(idx) {
    var template = {
        attachments: []
    }
    template.name = $("#name").val()
    template.subject = $("#subject").val()
    template.envelope_sender = $("#envelope-sender").val()
    template.html = CKEDITOR.instances["html_editor"].getData();
    // Fix the URL Scheme added by CKEditor (until we can remove it from the plugin)
    template.html = template.html.replace(/https?:\/\/{{\.URL}}/gi, "{{.URL}}")
    // If the "Add Tracker Image" checkbox is checked, add the tracker
    if ($("#use_tracker_checkbox").prop("checked")) {
        if (template.html.indexOf("{{.Tracker}}") == -1 &&
            template.html.indexOf("{{.TrackingUrl}}") == -1) {
            template.html = template.html.replace("</body>", "{{.Tracker}}</body>")
        }
    } else {
        // Otherwise, remove the tracker
        template.html = template.html.replace("{{.Tracker}}</body>", "</body>")
    }
    template.text = $("#text_editor").val()
    // Add the attachments
    $.each($("#attachmentsTable").DataTable().rows().data(), function (i, target) {
        template.attachments.push({
            name: unescapeHtml(target[1]),
            content: target[3],
            type: target[4],
        })
    })

    if (idx != -1) {
        template.id = templates[idx].id
        api.templateId.put(template)
            .success(function (data) {
                successFlash("Template edited successfully!")
                load()
                dismiss()
            })
            .error(function (data) {
                modalError(data.responseJSON.message)
            })
    } else {
        // Submit the template
        api.templates.post(template)
            .success(function (data) {
                successFlash("Template added successfully!")
                load()
                dismiss()
            })
            .error(function (data) {
                modalError(data.responseJSON.message)
            })
    }
}

function dismiss() {
    $("#modal\\.flashes").empty()
    $("#attachmentsTable").dataTable().DataTable().clear().draw()
    $("#name").val("")
    $("#subject").val("")
    $("#text_editor").val("")
    $("#html_editor").val("")
    $("#modal").modal('hide')
}

var deleteTemplate = function (idx) {
    Swal.fire({
        title: "Are you sure?",
        text: "This will delete the template. This can't be undone!",
        type: "warning",
        animation: false,
        showCancelButton: true,
        confirmButtonText: "Delete " + escapeHtml(templates[idx].name),
        confirmButtonColor: "#428bca",
        reverseButtons: true,
        allowOutsideClick: false,
        preConfirm: function () {
            return new Promise(function (resolve, reject) {
                api.templateId.delete(templates[idx].id)
                    .success(function (msg) {
                        resolve()
                    })
                    .error(function (data) {
                        reject(data.responseJSON.message)
                    })
            })
        }
    }).then(function (result) {
        if(result.value) {
            Swal.fire(
                'Template Deleted!',
                'This template has been deleted!',
                'success'
            );
        }
        $('button:contains("OK")').on('click', function () {
            location.reload()
        })
    })
}

function deleteTemplate(idx) {
    if (confirm("Delete " + templates[idx].name + "?")) {
        api.templateId.delete(templates[idx].id)
            .success(function (data) {
                successFlash(data.message)
                load()
            })
    }
}

function attach(files) {
    attachmentsTable = $("#attachmentsTable").DataTable({
        destroy: true,
        "order": [
            [1, "asc"]
        ],
        columnDefs: [{
            orderable: false,
            targets: "no-sort"
        }, {
            sClass: "datatable_hidden",
            targets: [3, 4]
        }]
    });
    $.each(files, function (i, file) {
        var reader = new FileReader();
        /* Make this a datatable */
        reader.onload = function (e) {
            var icon = icons[file.type] || "fa-file-o"
            // Add the record to the modal
            attachmentsTable.row.add([
                '<i class="fa ' + icon + '"></i>',
                escapeHtml(file.name),
                '<span class="remove-row"><i class="fa fa-trash-o"></i></span>',
                reader.result.split(",")[1],
                file.type || "application/octet-stream"
            ]).draw()
        }
        reader.onerror = function (e) {
            console.log(e)
        }
        reader.readAsDataURL(file)
    })
}

function edit(idx) {
    $("#modalSubmit").unbind('click').click(function () {
        save(idx)
    })
    $("#attachmentUpload").unbind('click').click(function () {
        this.value = null
    })
    $("#html_editor").ckeditor()
    setupAutocomplete(CKEDITOR.instances["html_editor"])
    $("#attachmentsTable").show()
    attachmentsTable = $('#attachmentsTable').DataTable({
        destroy: true,
        "order": [
            [1, "asc"]
        ],
        columnDefs: [{
            orderable: false,
            targets: "no-sort"
        }, {
            sClass: "datatable_hidden",
            targets: [3, 4]
        }]
    });
    var template = {
        attachments: []
    }
    if (idx != -1) {
        $("#templateModalLabel").text("Edit Template")
        template = templates[idx]
        $("#name").val(template.name)
        $("#subject").val(template.subject)
        $("#envelope-sender").val(template.envelope_sender)
        $("#html_editor").val(template.html)
        $("#text_editor").val(template.text)
        attachmentRows = []
        $.each(template.attachments, function (i, file) {
            var icon = icons[file.type] || "fa-file-o"
            // Add the record to the modal
            attachmentRows.push([
                '<i class="fa ' + icon + '"></i>',
                escapeHtml(file.name),
                '<span class="remove-row"><i class="fa fa-trash-o"></i></span>',
                file.content,
                file.type || "application/octet-stream"
            ])
        })
        attachmentsTable.rows.add(attachmentRows).draw()
        if (template.html.indexOf("{{.Tracker}}") != -1) {
            $("#use_tracker_checkbox").prop("checked", true)
        } else {
            $("#use_tracker_checkbox").prop("checked", false)
        }

    } else {
        $("#templateModalLabel").text("New Template")
    }
    // Handle Deletion
    $("#attachmentsTable").unbind('click').on("click", "span>i.fa-trash-o", function () {
        attachmentsTable.row($(this).parents('tr'))
            .remove()
            .draw();
    })
}

function copy(idx) {
    $("#modalSubmit").unbind('click').click(function () {
        save(-1)
    })
    $("#attachmentUpload").unbind('click').click(function () {
        this.value = null
    })
    $("#html_editor").ckeditor()
    $("#attachmentsTable").show()
    attachmentsTable = $('#attachmentsTable').DataTable({
        destroy: true,
        "order": [
            [1, "asc"]
        ],
        columnDefs: [{
            orderable: false,
            targets: "no-sort"
        }, {
            sClass: "datatable_hidden",
            targets: [3, 4]
        }]
    });
    var template = {
        attachments: []
    }
    template = templates[idx]
    $("#name").val("Copy of " + template.name)
    $("#subject").val(template.subject)
    $("#envelope-sender").val(template.envelope_sender)
    $("#html_editor").val(template.html)
    $("#text_editor").val(template.text)
    $.each(template.attachments, function (i, file) {
        var icon = icons[file.type] || "fa-file-o"
        // Add the record to the modal
        attachmentsTable.row.add([
            '<i class="fa ' + icon + '"></i>',
            escapeHtml(file.name),
            '<span class="remove-row"><i class="fa fa-trash-o"></i></span>',
            file.content,
            file.type || "application/octet-stream"
        ]).draw()
    })
    // Handle Deletion
    $("#attachmentsTable").unbind('click').on("click", "span>i.fa-trash-o", function () {
        attachmentsTable.row($(this).parents('tr'))
            .remove()
            .draw();
    })
    if (template.html.indexOf("{{.Tracker}}") != -1) {
        $("#use_tracker_checkbox").prop("checked", true)
    } else {
        $("#use_tracker_checkbox").prop("checked", false)
    }
}

function importEmail() {
    raw = $("#email_content").val()
    convert_links = $("#convert_links_checkbox").prop("checked")
    if (!raw) {
        modalError("No Content Specified!")
    } else {
        api.import_email({
                content: raw,
                convert_links: convert_links
            })
            .success(function (data) {
                $("#text_editor").val(data.text)
                $("#html_editor").val(data.html)
                $("#subject").val(data.subject)
                // If the HTML is provided, let's open that view in the editor
                if (data.html) {
                    CKEDITOR.instances["html_editor"].setMode('wysiwyg')
                    $('.nav-tabs a[href="#html"]').click()
                }
                $("#importEmailModal").modal("hide")
            })
            .error(function (data) {
                modalError(data.responseJSON.message)
            })
    }
}

function openAIModal() {
    // Clear any previous messages
    $("#generateAIModal\\.flashes").empty()
}

function generateAITemplate() {
    var scenario = $("#ai_scenario").val()
    var targetCompany = $("#ai_target_company").val()
    var includeLandingPage = $("#ai_include_landing_page").prop("checked")

    if (!targetCompany) {
        targetCompany = "Your Organization"
    }

    // Show loading state
    var btnHtml = $("#generateAIButton").html()
    $("#generateAIButton").html('<i class="fa fa-spinner fa-spin"></i> Generating...')
    $("#generateAIButton").prop("disabled", true)

    // Clear any previous flashes
    $("#generateAIModal\\.flashes").empty()

    // Record start time for minimum loading duration
    var startTime = Date.now()
    var minLoadingTime = 2000 // 2 seconds minimum for natural feel

    // Use setTimeout to ensure the loading overlay renders before the API call
    setTimeout(function() {
        // Show loading overlay in modal
        var loadingText = includeLandingPage ?
            '<h4 style="color: #333;">Generating AI Template & Landing Page...</h4>' :
            '<h4 style="color: #333;">Generating AI Template...</h4>'

        $("#generateAIModal .modal-body").append(
            '<div id="ai-loading-overlay" style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; ' +
            'background: rgba(255,255,255,0.95); z-index: 1000; display: flex; align-items: center; justify-content: center;">' +
            '<div style="text-align: center;">' +
            '<i class="fa fa-spinner fa-spin fa-3x" style="color: #0066cc; margin-bottom: 15px;"></i>' +
            loadingText +
            '<p style="color: #666;">This may take a few seconds</p>' +
            '</div></div>'
        )

        // Disable form inputs
        $("#ai_scenario").prop("disabled", true)
        $("#ai_target_company").prop("disabled", true)
        $("#ai_include_landing_page").prop("disabled", true)

        // Call the API using the api helper (which handles authentication)
        api.templates.generate_ai({
        scenario: scenario,
        target_company: targetCompany,
        include_landing_page: includeLandingPage
    })
    .success(function(data) {
        // Calculate remaining time to show loading
        var elapsedTime = Date.now() - startTime
        var remainingTime = Math.max(0, minLoadingTime - elapsedTime)

        // Wait for minimum loading time to make it feel more natural
        setTimeout(function() {
            // Remove loading overlay
            $("#ai-loading-overlay").remove()

            // Re-enable form inputs
            $("#ai_scenario").prop("disabled", false)
            $("#ai_target_company").prop("disabled", false)
            $("#ai_include_landing_page").prop("disabled", false)

            // Generate template name from scenario
            var scenarioNames = {
                'password_reset': 'Password Reset',
                'urgent_action': 'Urgent Action Required',
                'account_verification': 'Account Verification',
                'security_alert': 'Security Alert',
                'document_share': 'Document Shared',
                'invoice': 'Invoice/Payment',
                'it_support': 'IT Support',
                'hr_announcement': 'HR Announcement'
            }
            var scenarioName = scenarioNames[scenario] || 'Phishing Template'
            var templateName = "AI Generated - " + scenarioName + " - " + targetCompany

            // If landing page was generated, save it first
            if (includeLandingPage && data.landing_page) {
                var landingPageName = templateName + " - Landing Page"
                var landingPage = {
                    name: landingPageName,
                    html: data.landing_page,
                    capture_credentials: true,
                    capture_passwords: true,
                    redirect_url: "https://example.com"
                }

                // Save the landing page
                api.pages.post(landingPage)
                    .success(function(pageData) {
                        successFlash("Landing page '" + landingPageName + "' created successfully!")
                    })
                    .error(function(pageError) {
                        errorFlash("Failed to create landing page: " + (pageError.responseJSON ? pageError.responseJSON.message : "Unknown error"))
                    })
            }

            // Close the AI modal first
            $("#generateAIModal").modal("hide")

            // Reset button
            $("#generateAIButton").html(btnHtml)
            $("#generateAIButton").prop("disabled", false)

            // Open the new template modal
            edit(-1)
            $("#modal").modal("show")

            // Generate envelope sender based on scenario
            var senderEmails = {
                'password_reset': 'noreply@security-team.com',
                'urgent_action': 'alerts@company-security.com',
                'account_verification': 'verify@account-services.com',
                'security_alert': 'security@it-department.com',
                'document_share': 'noreply@document-share.com',
                'invoice': 'billing@accounts-payable.com',
                'it_support': 'support@it-helpdesk.com',
                'hr_announcement': 'hr@human-resources.com'
            }
            var senderNames = {
                'password_reset': 'Security Team',
                'urgent_action': 'Security Alerts',
                'account_verification': 'Account Services',
                'security_alert': 'IT Security',
                'document_share': 'Document Services',
                'invoice': 'Accounts Payable',
                'it_support': 'IT Support',
                'hr_announcement': 'Human Resources'
            }
            var senderEmail = senderEmails[scenario] || 'noreply@company.com'
            var senderName = senderNames[scenario] || 'System Administrator'
            var envelopeSender = senderName + " <" + senderEmail + ">"

            // Populate the template fields
            $("#name").val(templateName)
            $("#envelope-sender").val(envelopeSender)
            $("#subject").val(data.subject)
            $("#text_editor").val(data.text)
            $("#html_editor").val(data.html)

            // Switch to HTML tab if HTML content is provided
            if (data.html) {
                CKEDITOR.instances["html_editor"].setMode('wysiwyg')
                $('.nav-tabs a[href="#html"]').click()
            }

            // Show success message
            var successMsg = includeLandingPage && data.landing_page ?
                "<div style=\"text-align:center\" class=\"alert alert-success\">\
                <i class=\"fa fa-check-circle\"></i> AI template and landing page generated successfully!</div>" :
                "<div style=\"text-align:center\" class=\"alert alert-success\">\
                <i class=\"fa fa-check-circle\"></i> AI template generated successfully!</div>"

            $("#modal\\.flashes").empty().append(successMsg)
        }, remainingTime)
    })
    .error(function(data) {
        // Remove loading overlay
        $("#ai-loading-overlay").remove()

        // Re-enable form inputs
        $("#ai_scenario").prop("disabled", false)
        $("#ai_target_company").prop("disabled", false)
        $("#ai_include_landing_page").prop("disabled", false)

        // Reset button
        $("#generateAIButton").html(btnHtml)
        $("#generateAIButton").prop("disabled", false)

        var errorMsg = "Failed to generate template"
        if (data.responseJSON && data.responseJSON.message) {
            errorMsg = data.responseJSON.message
        }

        $("#generateAIModal\\.flashes").empty().append("<div style=\"text-align:center\" class=\"alert alert-danger\">\
            <i class=\"fa fa-exclamation-circle\"></i> " + errorMsg + "</div>")
    })
    }, 100) // 100ms delay to ensure UI updates
}

function load() {
    $("#templateTable").hide()
    $("#emptyMessage").hide()
    $("#loading").show()
    api.templates.get()
        .success(function (ts) {
            templates = ts
            $("#loading").hide()
            if (templates.length > 0) {
                $("#templateTable").show()
                templateTable = $("#templateTable").DataTable({
                    destroy: true,
                    columnDefs: [{
                        orderable: false,
                        targets: "no-sort"
                    }]
                });
                templateTable.clear()
                templateRows = []
                $.each(templates, function (i, template) {
                    templateRows.push([
                        escapeHtml(template.name),
                        moment(template.modified_date).format('MMMM Do YYYY, h:mm:ss a'),
                        "<div class='pull-right'><span data-toggle='modal' data-backdrop='static' data-target='#modal'><button class='btn btn-primary' data-toggle='tooltip' data-placement='left' title='Edit Template' onclick='edit(" + i + ")'>\
                    <i class='fa fa-pencil'></i>\
                    </button></span>\
		    <span data-toggle='modal' data-target='#modal'><button class='btn btn-primary' data-toggle='tooltip' data-placement='left' title='Copy Template' onclick='copy(" + i + ")'>\
                    <i class='fa fa-copy'></i>\
                    </button></span>\
                    <button class='btn btn-danger' data-toggle='tooltip' data-placement='left' title='Delete Template' onclick='deleteTemplate(" + i + ")'>\
                    <i class='fa fa-trash-o'></i>\
                    </button></div>"
                    ])
                })
                templateTable.rows.add(templateRows).draw()
                $('[data-toggle="tooltip"]').tooltip()
            } else {
                $("#emptyMessage").show()
            }
        })
        .error(function () {
            $("#loading").hide()
            errorFlash("Error fetching templates")
        })
}

$(document).ready(function () {
    // Setup multiple modals
    // Code based on http://miles-by-motorcycle.com/static/bootstrap-modal/index.html
    $('.modal').on('hidden.bs.modal', function (event) {
        $(this).removeClass('fv-modal-stack');
        $('body').data('fv_open_modals', $('body').data('fv_open_modals') - 1);
    });
    $('.modal').on('shown.bs.modal', function (event) {
        // Keep track of the number of open modals
        if (typeof ($('body').data('fv_open_modals')) == 'undefined') {
            $('body').data('fv_open_modals', 0);
        }
        // if the z-index of this modal has been set, ignore.
        if ($(this).hasClass('fv-modal-stack')) {
            return;
        }
        $(this).addClass('fv-modal-stack');
        // Increment the number of open modals
        $('body').data('fv_open_modals', $('body').data('fv_open_modals') + 1);
        // Setup the appropriate z-index
        $(this).css('z-index', 1040 + (10 * $('body').data('fv_open_modals')));
        $('.modal-backdrop').not('.fv-modal-stack').css('z-index', 1039 + (10 * $('body').data('fv_open_modals')));
        $('.modal-backdrop').not('fv-modal-stack').addClass('fv-modal-stack');
    });
    $.fn.modal.Constructor.prototype.enforceFocus = function () {
        $(document)
            .off('focusin.bs.modal') // guard against infinite focus loop
            .on('focusin.bs.modal', $.proxy(function (e) {
                if (
                    this.$element[0] !== e.target && !this.$element.has(e.target).length
                    // CKEditor compatibility fix start.
                    &&
                    !$(e.target).closest('.cke_dialog, .cke').length
                    // CKEditor compatibility fix end.
                ) {
                    this.$element.trigger('focus');
                }
            }, this));
    };
    // Scrollbar fix - https://stackoverflow.com/questions/19305821/multiple-modals-overlay
    $(document).on('hidden.bs.modal', '.modal', function () {
        $('.modal:visible').length && $(document.body).addClass('modal-open');
    });
    $('#modal').on('hidden.bs.modal', function (event) {
        dismiss()
    });
    $("#importEmailModal").on('hidden.bs.modal', function (event) {
        $("#email_content").val("")
    })
    CKEDITOR.on('dialogDefinition', function (ev) {
        // Take the dialog name and its definition from the event data.
        var dialogName = ev.data.name;
        var dialogDefinition = ev.data.definition;

        // Check if the definition is from the dialog window you are interested in (the "Link" dialog window).
        if (dialogName == 'link') {
            dialogDefinition.minWidth = 500
            dialogDefinition.minHeight = 100

            // Remove the linkType field
            var infoTab = dialogDefinition.getContents('info');
            infoTab.get('linkType').hidden = true;
        }
    });
    load()

})
