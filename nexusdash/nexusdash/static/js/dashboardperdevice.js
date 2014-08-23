// For dashboardperdevice.html

// Hide the header when modal is shown
$('#intstats_graph-modal').on('show', function (e) {
    // if (!data) return e.preventDefault() // stops modal from being shown
    $('.subnavbar').hide();
    $('#navbarid').hide();
});

$('#intstats_graph-modal').on('hide', function (e) {
    // if (!data) return e.preventDefault() // stops modal from being shown
    $('.subnavbar').show();
    $('#navbarid').show();
});

// Display graph data when modal has been shown
$('#intstats_graph-modal').on('shown', function (e) {
	spinner = new Spinner().spin();
	$("#intstats_graph-modal .modal-body .span12").html('<span style="position: absolute;display: block;top: 50%;left: 50%;">' + $(spinner.el).html() + '</span>');
    var check = function(){
        if ($(INTSTATS_GRAPH_DATA).length > 0) {
            // run when data is populated
            // Insert a combo box 1st
            intNamesHtml = '';
			$(INTSTATS_GRAPH_DATA).each(function(i, j){intNamesHtml += '<option value="' + j[0] + '">' + j[0] + '</option>\n'});
			inputInterfaceNameHtml = 'Select Interface <select class="combobox">\n<option></option>\n' + intNamesHtml + '</select><div id="insert_intstats_graph_here"></div>';
            $("#intstats_graph-modal .modal-body .span12").html(inputInterfaceNameHtml);
            $('.combobox').combobox({bsVersion: '2'});
            
            // Trigger display of Graph when input changes
			$('.combobox-container input[class="combobox"]').change(function() {
				intName = this.value;
				console.log('foooo: ' + intName);
				graphHtmlSelected = '';
				$(INTSTATS_GRAPH_DATA).each(function(i, j){
					if (j[0] == intName) {
						graphHtmlSelected = j[1];
						return false;
					}
				});
				$("#insert_intstats_graph_here").html(graphHtmlSelected);
			});
        }
        else {
            setTimeout(check, 1000); // check again in a second
        }
    }
    check();
});

