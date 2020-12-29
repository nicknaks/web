$('.js-vote').click(function (ev) {
    ev.preventDefault()
    let $this = $(this), vote_action = $this.data('action'), id = $this.data('id'), name_class = $this.data('class');

    $.ajax('/vote/', {
        method: 'POST',
        data: {
            id: id,
            name_class: name_class,
            vote: vote_action,
            action: 'create'
        }
    }).done(function (data) {
        if (data['rating'] !== undefined) {
            document.getElementById(name_class + '-' + id).innerHTML = data['rating']
        }
    });
});