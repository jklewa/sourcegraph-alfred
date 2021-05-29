# encoding: utf-8

import os
import sys
import json
from workflow import Workflow, web

icon_mapping = {
    "Java": "images/icons/java.png",
    "C": "images/icons/c-original.png",
    "Go": "images/icons/go-original.png",
    "C#": "images/icons/csharp-original.png",
    "Python": "images/icons/python-original.png"
}


def main(wf):
    try:
        sourcegraph_url = os.environ['sourcegraph_url'].rstrip('/')
        api_token = os.environ['api_token']
    except KeyError as missing_config:
        sys.stderr.write('Missing required config: {}'.format(missing_config.args[0]))
        sys.exit(1)

    if wf.args and len(wf.args) > 1:
        query = wf.args[1]

        url = "{}/.api/graphql?SearchSuggestions".format(sourcegraph_url)
        body = """
             query SearchSuggestions($query: String!) {
                 search(query: $query) {
                     suggestions(first: 20) {
                         __typename
                         ... on Repository {
                             name
                             url
                         }
                         ... on File {
                             path
                             url
                             repository {
                                 name
                             }
                         }
                     }
                 }
             }
         """
        variables = {
            'query': query
        }
        request = web.post(url,
                           data=json.dumps({'query': body, 'variables': variables}),
                           headers={'Authorization': 'token {}'.format(api_token)})

        # throw an error if request failed
        # Workflow will catch this and show it to the user
        request.raise_for_status()

        # Parse the JSON returned
        result = request.json()
        # sys.stderr.write(json.dumps(result, indent=2))
        try:
            suggestions = result['data']['search']['suggestions']
        except KeyError:
            sys.stderr.write(str(result['errors']))
            raise

        wf.clear_data()

        if not suggestions:
            wf.add_item(title="No results found for \"%s\"" % query,
                        subtitle="",
                        valid=False,
                        icon='images/sourcegraph-mark.png')
            wf.send_feedback()
            return
        repo_count = file_count = 0
        for item in suggestions:
            try:
                if item['__typename'] in 'Repository' and repo_count < 5:
                    arg = item['url']
                    title = item['name']
                    icon = "images/icons/doc-code.png"
                    repo_count += 1
                    wf.add_item(title=title,
                                arg=arg,
                                valid=True,
                                icon=icon)
                elif item['__typename'] in 'File' and file_count < 5:
                    arg = item['url']
                    title = item['path']
                    subtitle = 'from {}'.format(item['repository']['name'])
                    icon = "images/icons/doc-code.png"
                    file_count += 1
                    wf.add_item(title=title,
                                subtitle=subtitle,
                                arg=arg,
                                valid=True,
                                icon=icon)
            except Exception as e:
                sys.stderr.write(str(e))
        # Send the results to Alfred as XML
        wf.send_feedback()


if __name__ == u"__main__":

    update_settings = {
        'github_slug': 'jklewa/sourcegraph-alfred',
        'frequency': 1
    }

    wf = Workflow(update_settings=update_settings)
    if wf.update_available:
        wf.start_update()
    sys.exit(wf.run(main))
