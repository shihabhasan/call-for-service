var filterTypes = {
    "ModelChoiceField": {
        options: [{id: "=", name: "is equal to"}],
        valueType: 'select'
    },
    "ChoiceField": {
        options: [{id: "=", name: "is equal to"}],
        valueType: 'select'
    },
    "NullBooleanField": {
        options: [{id: "=", name: "is equal to"}],
        valueType: 'truth'
    },
    "DateRangeField": {
        options: [
            {id: ">=", name: "is greater than or equal to"},
            {id: ">=", name: "is less than or equal to"}
        ],
        valueType: 'date'
    },
    "DurationRangeField": {
        options: [
            {id: ">=", name: "is greater than or equal to"},
            {id: "<=", name: "is less than or equal to"}
        ],
        valueType: 'duration'
    }
};

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
            getOptions: function (fieldName) {
                return _.sortBy(findField(fieldName).choices, function (n) { return n[1]; });
            },
            getFieldType: function (fieldName) {
                return filterTypes[findField(fieldName).type];
            }
        }
    },
    computed: {
        filterHash: function () {
            return "#" + buildQueryParams(this.get('filter'));
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
            window.location.hash = buildQueryParams(_.omit(this.get("filter"), key));
        });

        this.on('addfilter', function (event) {
            var field = this.get("addFilter.field");
            var verb = this.get("addFilter.verb");
            var value = this.get("addFilter.value");
            var filter = this.get("filter");

            var key = field;
            if (verb === ">=") {
                key += "_0";
            } else if (verb === "<=") {
                key += "_1";
            }

            filter = _.clone(filter);
            filter[key] = value;

            window.location.hash = buildQueryParams(filter);

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
        this.observe('filter', function (filter) {
            this.fire("filterUpdated", filter);
        });
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

function displayValue(fieldName, value) {
    var field = findField(fieldName);
    var dValue;

    if (field.choices) {
        var choiceMap = arrayToObj(field.choices)
        dValue = choiceMap[value];
    }

    if (!dValue) {
        dValue = value;
    }

    return dValue;
}

function describeFilter(filter) {
    var components = [];
    var keys = _.keys(filter).sort();

    keys.forEach(function (key) {
        if (key.endsWith("_0")) {
            components.push({
                s: key.slice(0, -2),
                v: ">=",
                o: filter[key],
                k: key
            });
        } else if (key.endsWith("_1")) {
            components.push({
                s: key.slice(0, -2),
                v: "<=",
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
    if (typeof str != "string" || str.length == 0) return {};
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
        if (typeof query[first] == "undefined") query[first] = second; else if (query[first] instanceof Array) query[first].push(second); else query[first] = [query[first], second];
    }
    return query;
}


