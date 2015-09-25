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
            editing: false,
            displayName: displayName,
            displayValue: displayValue,
            describeFilter: describeFilter,
            getOptions: function (fieldName) {
                return findField(fieldName).choices;
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

function buildURL(filter) {
    return url + "?" + buildQueryParams(filter);
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

function updateFilter() {
    if (window.location.hash) {
        dashboard.set('filter', parseQueryParams(window.location.hash.slice(1)));
    } else {
        dashboard.set('filter', {});
    }
}

