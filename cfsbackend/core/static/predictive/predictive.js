"use strict";

var predictive = new Ractive({
    el: "#predictive-summary",
    template: "#predictive-template",
    components: {'Filter': Filter},
    delimiters: ['[[', ']]'],
    tripleDelimiters: ['[[[', ']]]']
});
