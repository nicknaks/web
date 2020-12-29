$('.js-vote').click(function (ev) {
    ev.preventDefault()
    let $this = $(this), vote_action = $this.data('action'), id = $this.data('id'), name_class = $this.data('class');

    let map = {
        'like': 'dislike',
        'dislike': 'like',
    }

    let action;
    if (document.getElementById(name_class + '-' + vote_action + '-' + id).classList.contains('js-voted')) {
        action = 'delete'
    } else if (document.getElementById(name_class + '-' + map[vote_action] + '-' + id).classList.contains('js-voted')) {
        action = 'update'
    } else {
        action = 'create'
    }

    document.getElementById(name_class + '-' + 'like' + '-' + id).classList.remove('js-voted')
    document.getElementById(name_class + '-' + 'dislike' + '-' + id).classList.remove('js-voted')

    $.ajax('/vote/', {
        method: 'POST',
        data: {
            id: id,
            name_class: name_class,
            vote: vote_action,
            action: action
        }
    }).done(function (data) {
        if (data['rating'] !== undefined) {
            document.getElementById(name_class + '-' + id).innerHTML = data['rating']
            if (action !== 'delete') {
                document.getElementById(name_class + '-' + vote_action + '-' + id).classList.add('js-voted')
            }
        }
    });
});