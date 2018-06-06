from urllib import request
import json


def git_commits(**kw):
    if 'repo' not in kw:
        raise AttributeError('Error no repo spacified')
    if 'password' in kw and 'username' in kw:
        password_mgr = request.HTTPPasswordMgrWithDefaultRealm()
        top_level_url = "https://api.github.com/"
        password_mgr.add_password(None, top_level_url, kw['username'], kw['password'])

        handler = request.HTTPBasicAuthHandler(password_mgr)
        opener = request.build_opener(handler)
    else:
        opener = request.build_opener(request.BaseHandler)

    print('Get branches ...')
    req = request.Request('https://api.github.com/repos/{}/{}'.format(kw['owner'], kw['repo']), method='GET')
    res = opener.open(req, timeout=10)

    repo = json.loads(res.read())
    req = request.Request(
        'https://api.github.com/repos/{}/{}/branches/{}'.format(kw['owner'], kw['repo'], repo['default_branch']),
        method='GET')
    res = opener.open(req, timeout=10)

    branch = json.loads(res.read())

    commit_tree = []
    print('Get commits for branch `{}` ...'.format(branch['name']))
    page = '&page={}'.format(kw['page']) if 'page' in kw else ''
    req = request.Request(
        'https://api.github.com/repos/{}/{}/commits?per_page=100&sha={}{}'.format(kw['owner'], kw['repo'],
                                                                                  branch['commit']['sha'], page),
        method='GET')
    res = opener.open(req, timeout=10)
    commits = json.loads(res.read())
    commit_tree += commits
    print('Finalize the process')
    return commit_tree, generate_graph_data(commit_tree)


def generate_graph_data(commits):
    """Generate graph data.
    :param commits: a list of commit, which should have
        `sha`, `parents` properties.
    :returns: data nodes, a json list of
        [
          sha,
          [offset, branch], //dot
          [
            [from, to, branch],  // route 1
            [from, to, branch],  // route 2
            [from, to, branch],
          ]  // routes
        ],  // node
    """

    nodes = []
    branch_idx = [0]
    reserve = []
    branches = {}

    def get_branch(sha):
        if branches.get(sha) is None:
            branches[sha] = branch_idx[0]
            reserve.append(branch_idx[0])
            branch_idx[0] += 1
        return branches[sha]

    for commit in commits:
        branch = get_branch(commit['sha'])
        n_parents = len(commit['parents'])
        offset = reserve.index(branch)
        routes = []

        if n_parents == 1:
            # create branch
            if branches.get(commit['parents'][0]['sha']) is not None:
                routes += [[i + offset + 1, i + offset + 1 - 1, b]
                           for i, b in enumerate(reserve[offset + 1:])]
                routes += [[i, i, b]
                           for i, b in enumerate(reserve[:offset])]
                reserve.remove(branch)
                routes.append([offset,
                               reserve.index(branches[commit['parents'][0]['sha']]),
                               branch])
            # straight
            else:
                routes += [[i, i, b] for i, b in enumerate(reserve)]
                branches[commit['parents'][0]['sha']] = branch
        # merge branch
        elif n_parents == 2:
            branches[commit['parents'][0]['sha']] = branch
            routes += [[i, i, b] for i, b in enumerate(reserve)]
            other_branch = get_branch(commit['parents'][1]['sha'])
            routes.append([offset, reserve.index(other_branch),
                           other_branch])

        node = _make_node(commit['sha'],
                          offset,
                          branch,
                          routes)
        nodes.append(node)
    return nodes


def _make_node(sha, offset, branch, routes):
    return [sha, [offset, branch], routes]


if __name__ == '__main__':
    import http.server
    from urllib import parse

    PORT = 8000


    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path.startswith('/git_commits'):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                query = parse.urlparse(self.path).query
                kw = {}
                for k, v in parse.parse_qs(query).items():
                    kw[k] = v if len(v) > 1 else v[0]
                # Send the html message
                self.wfile.write(
                    json.dumps(
                        dict(zip(('tree', 'graph'), git_commits(**kw)))
                    ).encode('utf-8')
                )
            else:
                super(Handler, self).do_GET()


    with http.server.HTTPServer(("0.0.0.0", PORT), Handler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()
