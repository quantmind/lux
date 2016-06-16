import _ from '../ng';


// @ngInject
export default function ($window, $document, luxFormConfig) {

    luxFormConfig.onSuccess('redirect', (response, form) => {
        $window.location.href = form.redirectTo || '/';
    }).onSuccess('reload', () => {
        $window.location.reload();
    }).onSuccess('replace', replace);


    function replace(response, form) {
        var message = response.data.message;
        var el = _.element($document[0].createElement('div')).addClass('center-text');
        var height = form.$htmlElement.offsetHeight;
        el.css('height', `${height}px`).html(messageTpl(message));
        _.element(form.$htmlElement).replaceWith(el);
    }

}


const messageTpl = function (message) {
    return `<br>
<p class="lead">${message}</p>`;
};
