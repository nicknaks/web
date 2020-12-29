$('.js-correct').click(function (ev) {
    ev.preventDefault()
    let $this = $(this)
    let id = $this.data('id')

    let checked = document.getElementById('answer-check-' + id).checked;

    $.ajax('/correct/', {
        method: 'POST',
        data: {
            answer_id: id,
            checked: checked
        },
    }).done(function (data) {
        document.getElementById('answer-check-' + id).checked = data['correct']
    });

})