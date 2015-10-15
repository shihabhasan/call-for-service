"use strict";

var predictive = new Ractive({
    el: "#predictive-summary",
    template: "#predictive-template",
    components: {'Filter': Filter, 'NavBar': NavBar},
    delimiters: ['[[', ']]'],
    tripleDelimiters: ['[[[', ']]]']
});

predictive.on('Filter.filterUpdated', function (filter) {
    // TODO Refactor this out of here
    predictive.set('filterHash', predictive.findComponent('Filter').get('filterHash'));
});

