"use strict";

var url = "/api/officer_allocation/";

var dashboard = new Page({
    el: $('body').get(),
    template: "#dashboard-template",
    data: {test: 'a'},
    filterUpdated: function (filter) {
        console.log(buildURL(filter));
        d3.json(buildURL(filter), _.bind(function (error, newData) {
            if (error) throw error;
            this.set('loading', false);
            this.set('initialload', false);
            newData = cleanupData(newData);
            this.set('data', newData);
        }, this));
    }
});

function cleanupData(newData) {
    return newData;
}

function buildURL(filter) {
    return url + "?" + buildQueryParams(filter);
}
