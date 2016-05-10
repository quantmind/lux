export default function (object, key) {
    if (object && object[key]) {
        var value = object[key];
        delete object[key];
        return value;
    }
}
