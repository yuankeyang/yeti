import re
from datetime import timedelta
from datetime import datetime
import logging

from core.feed import Feed
from core.observables import Url
from core.errors import ObservableValidationError


class ZeusTrackerDropzones(Feed):

    default_values = {
        "frequency": timedelta(hours=1),
        "name": "ZeusTrackerDropzones",
        "source": "https://zeustracker.abuse.ch/monitor.php?urlfeed=dropzones",
        "description": "Shows the latest 50 ZeuS dropzone URLs.",
    }

    def update(self):
        for d in self.update_xml('item', ["title", "link", "description", "guid"]):
            self.analyze(d)

    def analyze(self, dict):
        url_string = re.search(r"URL: (?P<url>\S+),", dict['description']).group('url')

        context = {}
        date_string = re.search(r"\((?P<date>[0-9\-]+)\)", dict['title']).group('date')
        context['date_added'] = datetime.strptime(date_string, "%Y-%m-%d")
        context['status'] = re.search(r"status: (?P<status>[^,]+)", dict['description']).group('status')
        context['guid'] = dict['guid']
        context['source'] = self.name
        try:
            context['md5'] = re.search(r"MD5 hash: (?P<md5>[a-f0-9]+)", dict['description']).group('md5')
        except AttributeError as e:
            pass

        try:
            n = Url.get_or_create(value=url_string)
            n.add_context(context)
            n.add_source("feed")
            n.tag(['zeus', 'objective', 'banker', 'crimeware', 'malware'])
        except ObservableValidationError as e:
            logging.error(e)
