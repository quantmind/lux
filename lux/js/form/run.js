import _ from '../ng';


// @ngInject
export default function ($window, $document, luxFormConfig) {

    luxFormConfig.onSuccess('redirect', function (response, form) {
        $window.location.href = form.redirectTo || '/';
    }).onSuccess('reload', function () {
        $window.location.reload();
    }).onSuccess('replace', replace);


    function replace(response, form) {
        var message = response.data.message;
        var el = _.element($document[0].createElement('div')).addClass('center-text');
        var height = form.$scope.$element[0].offsetHeight;
        el.css('height', `${height}px`).html(messageTpl(message));
        form.$scope.$element.replaceWith(el);
    }

}


const messageTpl = function (message) {
    return `<br>
<p class="lead">${message}</p>`;
}
