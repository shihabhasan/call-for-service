"use strict";

var url = "/api/calls/";

var call_list;

var outFormats = {
    "month": "%b %y",
    "week": "%m/%d/%y",
    "day": "%a %m/%d",
    "hour": "%m/%d %H:%M"
};

var calls = new Ractive({
    el: document.getElementById("calls"),
    template: "#calls-template",
    components: {'Filter': Filter},
    data: {
        loading: true,
        data: { 
        	'calls': []
        }
    },
    delimiters: ['[[', ']]'],
    tripleDelimiters: ['[[[', ']]]']
});

calls.on('Filter.filterUpdated', function (filter) {
    d3.json(buildURL(filter), function (error, newData) {
        if (error) throw error;
        calls.set('loading', false);
        calls.set('data', newData);
        console.log("call list is empty" + newData);
    });
});

calls.observe('data.calls', function (newData) {
    if (!calls.get('loading')) {
        if (!call_list) {
            var retval = buildCallList(newData);
            call_list = retval;
        } else {


        }
    }
});

// ========================================================================
// Functions
// ========================================================================

function buildURL(filter) {
    return url + "?" + buildQueryParams(filter);
}

function buildCallList(data) {
	console.log("building call list");
}

