$(document).ready(function () {
    var getUrlParameter = function getUrlParameter(sParam) {
        var sPageURL = decodeURIComponent(window.location.search.substring(1)),
            sURLVariables = sPageURL.split('&'),
            sParameterName,
            i;

        for (i = 0; i < sURLVariables.length; i++) {
            sParameterName = sURLVariables[i].split('=');

            if (sParameterName[0] === sParam) {
                return sParameterName[1] === undefined ? true : sParameterName[1];
            }
        }
    };
    var repo = getUrlParameter("repo") || 'odoo';
    var owner = getUrlParameter("owner") || 'odoo';
    var page = getUrlParameter("page") || 1;
    $.get(
        '/git_commits', {repo: repo, owner: owner, page: page}
    ).success(function (data) {
        var commit_tree = data['tree'];
        var commit_graph = data['graph'];

        $('#commit-graph').attr('data-graph', JSON.stringify(commit_graph));
        $('#commit-graph').commits({});

        for (var i = 0; i < commit_tree.length; i++) {
            var commit = commit_tree[i];
            var msg = commit.commit.message.split('\n\n')[0];
            var length =Math.min(100, msg.length);
            if (length !== msg.length){
                msg = msg.substring(0, length) + "...";
            } else {
                msg = msg.substring(0, length)
            }
            $('<li>').text(msg).appendTo('#commit-msg ul');
        }
    });

});
