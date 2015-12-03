var NavBar = Ractive.extend({
    template: '#navbar-template',
    delimiters: ['[[', ']]'],
    tripleDelimiters: ['[[[', ']]]']
});

var ChartHeader = Ractive.extend({
    template: '#chart-header-template',
    delimiters: ['[[', ']]'],
    tripleDelimiters: ['[[[', ']]]'],
    isolated: true,
    data: {
        hidden: true
    },
    oninit: function () {
        this.on('toggleExplanation', function () {
            this.set('hidden', !this.get('hidden'));
        })
    }
});

var lookupMap = {
    "exact": {id: "=", name: "is equal to"},
    "gte": {id: ">=", name: "is greater than or equal to"},
    "lte": {id: "<=", name: "is less than or equal to"}
};

var FilterButton = Ractive.extend({
    template: '#filter-button-template',
    delimiters: ['[[', ']]'],
    tripleDelimiters: ['[[[', ']]]'],
    data: function () {
        return {
            displayName: displayName,
            getFieldType: function (fieldName) {
                var field = findField(fieldName);
                if (field.rel !== undefined) {
                    return {
                        type: "select",
                        options: filterForm.refs[field.rel]
                    };
                } else if (field.type === "select") {
                    return {type: field.type, options: field.options}
                } else {
                    return {type: field.type};
                }
            },
            buttonClass: function (field, filter) {
                if (filterValue(field, filter)) {
                    return "btn-success";
                } else {
                    return "btn-primary";
                }
            },
            filterValue: filterValue,
            displayValue: displayValue
        }
    }
});

var Filters = Ractive.extend({
    components: {'filter-button': FilterButton},
    template: '#filters-template',
    delimiters: ['[[', ']]'],
    tripleDelimiters: ['[[[', ']]]'],
    data: {
        filter: {}
    },
    oninit: function () {
        var component = this;

        function updateFilter() {
            if (window.location.hash) {
                component.set('filter', parseQueryParams(window.location.hash.slice(1)));
            } else {
                component.set('filter', {});
            }
        }

        updateFilter();
        $(window).on("hashchange", updateFilter);
    },
});

var Filter = Ractive.extend({
    template: '#filter-template',
    delimiters: ['[[', ']]'],
    tripleDelimiters: ['[[[', ']]]'],

    data: function () {
        return {
            filter: {},
            addFilter: {},
            editing: false,
            displayName: displayName,
            displayValue: displayValue,
            describeFilter: describeFilter,
            getLookups: getLookups,
            getFieldType: function (fieldName) {
                var field = findField(fieldName);
                if (field.rel !== undefined) {
                    return {
                        type: "select",
                        options: filterForm.refs[field.rel]
                    };
                } else if (field.type === "select") {
                    return {type: field.type, options: field.options}
                } else {
                    return {type: field.type};
                }
            },
            fieldLabel: function (field) {
                return field.label || humanize(field.name);
            }
        }
    },
    computed: {
        filterHash: function () {
            return "#!" + buildQueryParams(this.get('filter'));
        },
        fields: function () {
            return filterForm.fields;
        }
    },
    oninit: function () {
        var component = this;

        this.on('editfilter', function (event, action) {
            if (action === "start") {
                this.set('editing', true);
            } else if (action === "stop") {
                this.set('editing', false);
            }
        });

        this.on('removefilter', function (event, key) {
            updateHash(buildQueryParams(_.omit(this.get("filter"), key)));
        });

        this.on('addfilter', function (event) {
            var field = this.get("addFilter.field");
            var verb = this.get("addFilter.verb");
            var value = this.get("addFilter.value");
            var filter = this.get("filter");

            var key = field;
            if (verb === ">=") {
                key += "__gte";
            } else if (verb === "<=") {
                key += "__lte";
            } else if (verb === "!=") {
                key += "!";
            }

            filter = _.clone(filter);
            filter[key] = value;

            updateHash(buildQueryParams(filter));

            // prevent default
            return false;
        });

        function updateFilter() {
            if (window.location.hash) {
                component.set('filter', parseQueryParams(window.location.hash.slice(1)));
            } else {
                component.set('filter', {});
            }
        }

        updateFilter();
        $(window).on("hashchange", updateFilter);
    },
    oncomplete: function () {
        // This is here to set addFilter.value to the default value in a select
        // box. Without this, there would be no value on submit.
        this.observe("addFilter.field", function (_) {
            var self = this;

            // We use setTimeout to move this to further down in the event loop.
            // The page has to render first before this will work.
            setTimeout(function () {
                self.set("addFilter.value", $("select[name=filter_object]").val());
            }, 0)
        }, {defer: true});

        this.observe('filter', function (filter) {
            this.fire("filterUpdated", filter);
        });

        var stickySidebar = $('.filter-sidebar');
        var sizer = $("#sidebar-sizer");

        if (stickySidebar.length > 0) {
            var sidebarTop = stickySidebar.offset().top,
                sidebarLeft = stickySidebar.offset().left,
                stickyStyles = stickySidebar.attr('style');
        }

        var resetSidebar = function () {
            stickySidebar.attr('style', stickyStyles).css({
                'position': '',
                'top': '',
                'left': ''
            }).removeClass('fixed');
        };

        var smallScreen = function () {
            return sizer.width() / $("body").width() > 0.25;
        };

        $(window).scroll(function () {
            if (stickySidebar.length > 0) {
                if (!smallScreen()) {
                    var scrollTop = $(window).scrollTop();

                    if (sidebarTop < scrollTop) {
                        stickySidebar.css({
                            position: 'fixed',
                            top: 0,
                            left: sizer.offset().left,
                            minWidth: 0,
                            width: sizer.outerWidth() + 'px'
                        }).addClass('fixed');
                    } else {
                        resetSidebar();
                    }
                }
            }
        });

        $(window).resize(function () {
            if (smallScreen()) {
                resetSidebar();
            }
            stickySidebar.css({
                left: sizer.offset().left,
                width: sizer.outerWidth() + 'px'
            })
        });
    }
});

var Page = Ractive.extend({
    components: {
        'Filter': Filter, 'NavBar': NavBar, 'chart-header': ChartHeader, 'Filters': Filters
    },
    delimiters: ['[[', ']]'],
    tripleDelimiters: ['[[[', ']]]'],
    data: {
        filterHash: '',
        initialload: true,
        loading: true
    },
    oninit: function () {
        this.on('Filter.filterUpdated', _.bind(function (filter) {
            this.set('loading', true);
            this.set('filterHash', this.findComponent('Filter').get('filterHash'));
            this.filterUpdated(filter);
        }, this));
    }
});


// ========================================================================
// Functions
// ========================================================================

function findField(fieldName) {
    return _(filterForm.fields).find(function (field) {
        return field.name == fieldName;
    })
}

function humanize(property) {
    return property.replace(/_/g, ' ')
        .replace(/(\w+)/g, function (match) {
            return match.charAt(0).toUpperCase() + match.slice(1);
        });
}

function displayName(fieldName) {
    if (fieldName === undefined) {
        return;
    }
    return findField(fieldName).label || humanize(fieldName);
}

function arrayToObj(arr) {
    // Given an array of two-element arrays, turn it into an object.
    var obj = {};
    arr.forEach(function (x) {
        obj[x[0]] = x[1];
    });

    return obj;
}

function getLookups(fieldName) {
    var field = findField(fieldName);
    if (field.lookups === undefined) {
        return [{id: "=", name: "is equal to"}, {
            id: "!=",
            name: "is not equal to"
        }];
    } else {
        return _(field.lookups).map(function (lookup) {
            return lookupMap[lookup]
        });
    }
}

function displayValue(fieldName, value) {
    if (fieldName === undefined) {
        return;
    }
    var field = findField(fieldName);
    var dValue;

    if (field.rel) {
        var choiceMap = arrayToObj(filterForm.refs[field.rel]);
        dValue = choiceMap[value];
    }

    if (field.options) {
        var choiceMap = arrayToObj(field.options);
        dValue = choiceMap[value];
    }

    if (!dValue) {
        dValue = value;
    }

    return dValue;
}

function filterValue(fieldName, filter) {
    return filter[fieldName];
}

function describeFilter(filter) {
    var components = [];
    var keys = _.keys(filter).sort();

    keys.forEach(function (key) {
        if (key.endsWith("__gte")) {
            components.push({
                s: key.slice(0, -5),
                v: ">=",
                o: filter[key],
                k: key
            });
        } else if (key.endsWith("__lte")) {
            components.push({
                s: key.slice(0, -5),
                v: "<=",
                o: filter[key],
                k: key
            });
        } else if (key.endsWith("!")) {
            components.push({
                s: key.slice(0, -1),
                v: "!=",
                o: filter[key],
                k: key
            });
        } else {
            components.push({s: key, v: "=", o: filter[key], k: key});
        }
    });

    return components;
}

function buildQueryParams(obj) {
    var str = "";
    for (var key in obj) {
        if (str != "") {
            str += "&";
        }
        str += key + "=" + encodeURIComponent(obj[key]);
    }
    return str;
}

function parseQueryParams(str) {
    if (typeof str != "string") return {};
    if (str.charAt(0) === "!") {
        str = str.slice(1);
    }

    if (str.length == 0) return {};

    var s = str.split("&");
    var s_length = s.length;
    var bit,
        query = {},
        first,
        second;
    for (var i = 0; i < s_length; i++) {
        bit = s[i].split("=");
        first = decodeURIComponent(bit[0]);
        if (first.length == 0) continue;
        second = decodeURIComponent(bit[1]);
        if (typeof query[first] == "undefined") {
            query[first] = second;
        } else if (query[first] instanceof Array) {
            query[first].push(second);
        } else {
            query[first] = [query[first], second];
        }
    }
    return query;
}

function updateHash(newHash) {
    var scr = document.body.scrollTop;
    window.location.hash = "!" + newHash;
    document.body.scrollTop = scr;
}

function durationFormat(secs) {
    secs = Math.round(secs);
    if (secs > 60 * 60) {
        return d3.format("d")(Math.floor(secs / 60 / 60)) + ":" +
            d3.format("02d")(Math.floor((secs / 60) % 60)) + ":" +
            d3.format("02d")(Math.floor(secs % 60));
    } else {
        return d3.format("d")(Math.floor(secs / 60)) + ":" +
            d3.format("02d")(Math.floor(secs % 60));
    }
}

function monitorChart(ractive, keypath, fn) {
    ractive.observe(keypath, function (newData) {
        if (!ractive.get('loading')) {
            // If we don't remove the tooltips before updating
            // the chart, they'll stick around
            d3.selectAll(".nvtooltip").remove();

            fn(newData);
        }
    })
}

function cloneFilter(ractive) {
    return _.clone(ractive.findComponent('Filter').get('filter'));
}

function toggleFilter(ractive, key, value) {
    var f = cloneFilter(ractive);
    if (f[key] == value) {
        delete f[key];
    } else {
        f[key] = value;
    }
    updateHash(buildQueryParams(f));
}

function buildURL(url, filter) {
    return url + "?" + buildQueryParams(filter);
}