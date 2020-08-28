# encoding: utf-8
import sys
import argparse
from workflow import Workflow3, ICON_WEB, ICON_WARNING, ICON_INFO, web, PasswordNotFound
from workflow.background import run_in_background, is_running
import json

log = None


def search_for_project(project):
    """
        Generate a string search key for a project
        :param project: Name of default serializer to use.
        :type project: dict
    """
    if project:
        elements = []
        log.debug("prj {prj}".format(prj=project))
        if 'name' in project and project['name'] is not None:
            elements.append(project['name'])
        if 'code' in project and project['code'] is not None:
            elements.append(project['code'])
        if 'jira' in project and project['jira'] is not None:
            elements.append(project['jira'])
        return u' '.join(elements)


def main(wf):
    # build argument parser to parse script args and collect their
    # values
    parser = argparse.ArgumentParser()
    # add an optional (nargs='?') --setkey argument and save its
    # value to 'apikey' (dest). This will be called from a separate "Run Script"
    # action with the API key
    parser.add_argument('--seturl', dest='apiurl', nargs='?', default=None)
    parser.add_argument('query', nargs='?', default=None)
    # parse the script's arguments
    args = parser.parse_args(wf.args)

    ####################################################################
    # Save the provided API key or URL
    ####################################################################

    # decide what to do based on arguments
    if args.apiurl:
        log.info("Setting API URL to {url}".format(url=args.apiurl))
        wf.settings['api_url'] = args.apiurl
        return 0

    ####################################################################
    # View/filter GitLab Projects
    ####################################################################

    query = args.query

    projects = wf.cached_data('projects', None, max_age=600)

    if wf.update_available:
        # Add a notification to top of Script Filter results
        wf.add_item('New version available',
                    'Action this item to install the update',
                    autocomplete='workflow:update',
                    icon=ICON_INFO)

    # Notify the user if the cache is being updated
    if is_running('update') and not projects:
        wf.rerun = 0.5
        wf.add_item('Updating project list via GitLab...',
                    subtitle=u'This can take some time if you have a large number of projects.',
                    valid=False,
                    icon=ICON_INFO)

    # Start update script if cached data is too old (or doesn't exist)
    if not wf.cached_data_fresh('projects', max_age=600) and not is_running('update'):
        cmd = ['/usr/bin/python', wf.workflowfile('update.py')]
        run_in_background('update', cmd)
        wf.rerun = 0.5

    # If script was passed a query, use it to filter projects
    if query and projects:
        projects = wf.filter(query, projects, key=search_for_project, min_score=20)

    if not projects:  # we have no data to show, so show a warning and stop
        wf.add_item('No projects found', icon=ICON_WARNING)
        wf.send_feedback()
        return 0

    # Loop through the returned posts and add an item for each to
    # the list of results for Alfred
    for post in projects:
        title = u''
        if post['jira'] is not None:
            title += post['jira'] + " | "

        if post['name'] is not None:
            title += post['name']

        wf.add_item(title=title.encode('utf-8').strip(),
                    subtitle="{ver} | {grp} | {code}".format(ver=post['jiraVersionType'], grp=post['group'],
                                                             code=post['code']),
                    arg=post['code'],
                    valid=True,
                    icon=ICON_WEB)

    # Send the results to Alfred as XML
    wf.send_feedback()


if __name__ == u"__main__":
    wf = Workflow3(update_settings=False)
    log = wf.logger
    sys.exit(wf.run(main))
