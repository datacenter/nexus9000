/* ===================================================
 * Specific dashboard functions for index.html
 * Common ones are in ./dashboard.common.js
 * https://github.com/afaqurk/linux-dash/blob/master/js/dashboard.js
 * Copyright (c) 2014 afaqurk
 * ========================================================== */

dashboard.getHostnames = function () {
    moduleData("hostnames", function (data) {
        // destroy_dataTable("table-hostnames");	// Replacing this with "bRetrieve: true" because spinner row
        $("#filter-hostnames").val("").off("keyup");
		// Add the HTML coming from JSON
		$("#table-hostnames tbody").html(data.data);
        var hostnamesTable = $("#table-hostnames").dataTable({
        	bRetrieve: true,
            bPaginate: true,
            sPaginationType: "full_numbers",
            bFilter: true,
            sDom: "lrtip",
            bAutoWidth: false,
            bInfo: false
        }).fadeIn();

        $("#filter-hostnames").on("keyup", function () {
            hostnamesTable.fnFilter(this.value);
        });
    });
}

/**
 * Refreshes all widgets. Does not call itself recursively.
 */
dashboard.getAll = function () {
    for (var item in dashboard.fnMap) {
        if (dashboard.fnMap.hasOwnProperty(item) && item !== "all") {
            try {
                dashboard.fnMap[item].call(dashboard);
            } catch (err) {
            }
        }
    }
}

dashboard.fnMap = {
    all: dashboard.getAll,
    hostnames: dashboard.getHostnames,
};
