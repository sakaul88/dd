import datetime
import six


class ReleaseRevision(object):
    def __init__(self, revision_json):
        self.chart = revision_json['chart']
        self.description = revision_json['description']
        self.revision = revision_json['revision']
        self.status = revision_json['status']
        self.updated = revision_json['updated']

    @property
    def chart(self):
        return self._chart

    @chart.setter
    def chart(self, chart):
        self._chart = chart

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        self._description = description

    @property
    def revision(self):
        return self._revision

    @revision.setter
    def revision(self, revision):
        self._revision = revision

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status

    @property
    def updated(self):
        return self._updated

    @updated.setter
    def updated(self, updated):
        if isinstance(updated, six.string_types):
            self._updated = datetime.datetime.strptime(updated, '%a %b %d %H:%M:%S %Y')
        else:
            self._updated = updated

    @classmethod
    def parse_release_revisions(self, revisions_json):
        """
        Helper method to parse a list of release revision dictionaries.
        This method simply iterates over the list, instantiating a ReleaseRevision object for each dictionary.
        Args:
            revisions_json: A list of revision dictionaries from the helm cli
        Returns: A list of ReleaseRevision objects
        """
        revisions = []
        for revision_json in revisions_json:
            revisions.append(ReleaseRevision(revision_json))
        return revisions
