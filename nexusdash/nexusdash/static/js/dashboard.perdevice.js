/* ===================================================
 * Specific dashboard functions for index.html
 * Common ones are in ./dashboard.common.js
 * https://github.com/afaqurk/linux-dash/blob/master/js/dashboard.js
 * Copyright (c) 2014 afaqurk
 * ========================================================== */

dashboard.getOverallhealth = function () {
    moduleData("overallhealth", function (data) {
        destroy_dataTable("table-overallhealth");
		// Add the HTML coming from JSON
		$("#table-overallhealth tbody").html(data.data);
        var overallhealthTable = $("#table-overallhealth").dataTable({
            bPaginate: true,
            sPaginationType: "full_numbers",
            bFilter: true,
            sDom: "lrtip",
            bAutoWidth: false,
            bInfo: false
        }).fadeIn();
    });
}

dashboard.getOs = function () {
    moduleData("osinfo", function (data) {
		// Add the HTML coming from JSON
		$("#table-osinfo tbody").html(data.data);
    });
}

var INTSTATS_GRAPH_DATA;
dashboard.getInterfaceStats = function () {
    moduleData("intstats", function (data) {
        destroy_dataTable("table-intstats");
        $("#filter-intstats").val("").off("keyup");

        var intstatsTable = $("#table-intstats").dataTable({
            aaData: data.data,
            aoColumns: [
                { sTitle: "NAME" },
                { sTitle: "STATE (protocol/admin)" },
                { sTitle: "HARDWARE TYPE" },
                { sTitle: "IP ADDRESS" },
                { sTitle: "MAC ADDRESS" },
                { sTitle: "MTU" },
                { sTitle: "BANDWIDTH (Kbit)" },
                { sTitle: "DESCRIPTION" },
                { sTitle: "RX RATE (bps)" },
                { sTitle: "TX RATE (bps)" },
                { sTitle: "POLL INTERVAL (sec)" }
            ],
            bPaginate: true,
            sPaginationType: "full_numbers",
            bFilter: true,
            sDom: "lrtip",
            bAutoWidth: false,
            bInfo: false
        }).fadeIn();

		
		INTSTATS_GRAPH_DATA = data.graph_data;
		
        $("#filter-intstats").on("keyup", function () {
            intstatsTable.fnFilter(this.value);
        });
    });
}


dashboard.getLoadAverage = function () {
    moduleData("loadavg", function (data) {
        $("#cpu-1min").text(data.data[0][0]);
        $("#cpu-5min").text(data.data[1][0]);
        $("#cpu-15min").text(data.data[2][0]);
        $("#cpu-1min-per").text(data.data[0][1]);
        $("#cpu-5min-per").text(data.data[1][1]);
        $("#cpu-15min-per").text(data.data[2][1]);
    });
}

dashboard.getRam = function () {
    moduleData("mem", function (data) {
        var ram_total = data.data[0];
        var ram_used = Math.round((data.data[1] / ram_total) * 100);
        var ram_free = Math.round((data.data[2] / ram_total) * 100);

        $("#ram-total").text(ram_total);
        $("#ram-used").text(data.data[1]);
        $("#ram-free").text(data.data[2]);

        $("#ram-free-per").text(ram_free);
        $("#ram-used-per").text(ram_used);
    });
}


dashboard.getDf = function () {
    moduleData("df", function (data) {
        var table = $("#df_dashboard");
        var ex = document.getElementById("df_dashboard");
        if ($.fn.DataTable.fnIsDataTable(ex)) {
            table.hide().dataTable().fnClearTable();
            table.dataTable().fnDestroy();
        }

        table.dataTable({
            aaData: data.data,
            aoColumns: [
                { sTitle: "Filesystem" },
                { sTitle: "Size", sType: "file-size" },
                { sTitle: "Used", sType: "file-size" },
                { sTitle: "Avail", sType: "file-size" },
                { sTitle: "Use%", sType: "percent" },
                { sTitle: "Module" }
            ],
	    iDisplayLength: 5,
            bPaginate: true,
            bFilter: false,
            bAutoWidth: true,
            bInfo: false
        }).fadeIn();
    });
}

dashboard.getModStats = function () {
    moduleData("modstats", function (data) {
        destroy_dataTable("table-modstats");
        $("#filter-modstats").val("").off("keyup");

        var modstatsTable = $("#table-modstats").dataTable({
            aaData: data.data,
            aoColumns: [
                { sTitle: "Module No." },
                { sTitle: "Ports" },
                { sTitle: "Desc" },
                { sTitle: "Model" },
                { sTitle: "Serial No." },
                { sTitle: "Status" },
                { sTitle: "Diag Status" }
            ],
            bPaginate: true,
            sPaginationType: "full_numbers",
            bFilter: true,
            sDom: "lrtip",
            bAutoWidth: false,
            bInfo: false
        }).fadeIn();
		
        $("#filter-modstats").on("keyup", function () {
            modstatsTable.fnFilter(this.value);
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
    os: dashboard.getOs,
    overallhealth: dashboard.getOverallhealth,
    intstats: dashboard.getInterfaceStats,
    cpu: dashboard.getLoadAverage,
    ram: dashboard.getRam,
    df: dashboard.getDf,
    modstats: dashboard.getModStats,
};
