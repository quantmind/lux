
const elements = {
    "text": {element: "input", type: "text", editable: true, textBased: true},
    "date": {element: "input", type: "date", editable: true, textBased: true},
    "datetime": {element: "input", type: "datetime", editable: true, textBased: true},
    "datetime-local": {element: "input", type: "datetime-local", editable: true, textBased: true},
    "email": {element: "input", type: "email", editable: true, textBased: true},
    "month": {element: "input", type: "month", editable: true, textBased: true},
    "number": {element: "input", type: "number", editable: true, textBased: true},
    "password": {element: "input", type: "password", editable: true, textBased: true},
    "search": {element: "input", type: "search", editable: true, textBased: true},
    "tel": {element: "input", type: "tel", editable: true, textBased: true},
    "textarea": {element: "textarea", editable: true, textBased: true},
    "time": {element: "input", type: "time", editable: true, textBased: true},
    "url": {element: "input", type: "url", editable: true, textBased: true},
    "week": {element: "input", type: "week", editable: true, textBased: true},
    //  Specialized editables
    "checkbox": {element: "input", type: "checkbox", editable: true, textBased: false},
    "color": {element: "input", type: "color", editable: true, textBased: false},
    "file": {element: "input", type: "file", editable: true, textBased: false},
    "range": {element: "input", type: "range", editable: true, textBased: false},
    "select": {element: "select", editable: true, textBased: false},
    //  Pseudo-non-editables (containers)
    "checklist": {element: "div", editable: false, textBased: false},
    "fieldset": {element: "fieldset", editable: false, textBased: false},
    "div": {element: "div", editable: false, textBased: false},
    "form": {element: "form", editable: false, textBased: false},
    "radio": {element: "div", editable: false, textBased: false},
    //  Non-editables (mostly buttons)
    "button": {element: "button", type: "button", editable: false, textBased: false},
    "hidden": {element: "input", type: "hidden", editable: false, textBased: false},
    "image": {element: "input", type: "image", editable: false, textBased: false},
    "legend": {element: "legend", editable: false, textBased: false},
    "reset": {element: "button", type: "reset", editable: false, textBased: false},
    "submit": {element: "button", type: "submit", editable: false, textBased: false}
};

export default elements;
