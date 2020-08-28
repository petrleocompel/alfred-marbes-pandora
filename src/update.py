# encoding: utf-8

from workflow import web, Workflow, PasswordNotFound

def get_projects(url):
    """
    Parse all pages of projects
    :return: list
    """
    wf.logger.info("Calling API page {url}".format(url=url))
    r = web.get(url)

    # throw an error if request failed
    # Workflow will catch this and show it to the user
    r.raise_for_status()

    # Parse the JSON returned extract the projects
    result = r.json()

    return result


def main(wf):
    wf.logger.info("Maing request to pandora" + wf.settings.get('api_url', 'https://pandora.marbes.cz/api/projects'))
    api_url = wf.settings.get('api_url', 'https://pandora.marbes.cz/api/projects')

    # Retrieve projects from cache if available and no more than 600
    # seconds old
    def wrapper():
        wf.logger.info("cache")
        return get_projects(api_url)

    projects = wf.cached_data('projects', wrapper, max_age=1)

    # Record our progress in the log file
    wf.logger.info('{} pandora projects cached'.format(len(projects)))


if __name__ == '__main__':
    wf = Workflow()
    wf.run(main)