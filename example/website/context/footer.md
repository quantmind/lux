require_context: html_footer1, html_footer2, html_footer3

<div class='small hidden-print text-muted' id='page-footer'>
    <div class='container'>
        <div class='row'>
            <div class='block col-sm-5'>
                <div class='hidden-xs'>
                    {{ html_footer1 }}
                </div>
                <div class='text-center visible-xs'>
                    {{ html_footer1 }}
                </div>
            </div>
            <div class='block col-sm-2 text-center'>
                <div class='hidden-xs'>
                    {{ html_footer2 }}
                </div>
                <div class='visible-xs'>
                    {{ html_footer3 }}
                </div>
            </div>
            <div class='block col-sm-5'>
                <div class='text-right hidden-xs'>
                    {{ html_footer3 }}
                </div>
                <div class='text-center visible-xs'>
                    {{ html_footer2 }}
                </div>
            </div>
        </div>
    </div>
</div>
