import _ from '../ng';

const isAbsolute = new RegExp('^([a-z]+://|//)');
const DEFAULT_PORTS = {80: 'http', 443: 'https', 21: 'ftp'};

let urlParsingNode;
let originUrl;


export function urlResolve(url) {

    if (!urlParsingNode) urlParsingNode = window.document.createElement("a");

    urlParsingNode.setAttribute('href', url);

    // urlParsingNode provides the UrlUtils interface - http://url.spec.whatwg.org/#urlutils
    var url = {
        href: urlParsingNode.href,
        protocol: urlParsingNode.protocol ? urlParsingNode.protocol.replace(/:$/, '') : '',
        host: urlParsingNode.host,
        search: urlParsingNode.search ? urlParsingNode.search.replace(/^\?/, '') : '',
        hash: urlParsingNode.hash ? urlParsingNode.hash.replace(/^#/, '') : '',
        hostname: urlParsingNode.hostname,
        port: urlParsingNode.port,
        pathname: (urlParsingNode.pathname.charAt(0) === '/') ? urlParsingNode.pathname : '/' + urlParsingNode.pathname,
        //
        $base: function () {
            var base = `${url.protocol}://${url.hostname}`;
            if (url.protocol !== DEFAULT_PORTS[+url.port]) base += `:${url.port}`;
            return base;
        }
    };

    return url;
}


export function urlIsSameOrigin(requestUrl) {
    if (!originUrl) originUrl = urlResolve(window.location.href);
  var parsed = (_.isString(requestUrl)) ? urlResolve(requestUrl) : requestUrl;
  return (parsed.protocol === originUrl.protocol &&
          parsed.host === originUrl.host);
}


export function urlIsAbsolute(url) {
    return _.isString(url) && isAbsolute.test(url);
}

export function urlJoin () {
    var bit, url = '';
    for (var i = 0; i < arguments.length; ++i) {
        bit = arguments[i];
        if (bit) {
            var cbit = bit,
                slash = false;
            // remove front slashes if cbit has some
            while (url && cbit.substring(0, 1) === '/')
                cbit = cbit.substring(1);
            // remove end slashes
            while (cbit.substring(cbit.length - 1) === '/') {
                slash = true;
                cbit = cbit.substring(0, cbit.length - 1);
            }
            if (cbit) {
                if (url && url.substring(url.length - 1) !== '/')
                    url += '/';
                url += cbit;
                if (slash)
                    url += '/';
            }
        }
    }
    return url;
}
