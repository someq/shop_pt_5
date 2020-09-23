from datetime import datetime


class StatsCounter:
    def __init__(self, request):
        self.request = request
        self.datetime_format = '%Y-%m-%d %H:%M:%S.%f'

        # {
        #     'total_count': 0,
        #     'total_time': 0,
        #     'pages': {
        #         '': {'count': 0, 'time': 0},
        #         'product/add/': {'count': 0, 'time': 0},
        #         # ...,
        #     }
        # }
        self._stats = self.request.session.get('stats', {})
        self._pages = self._stats.setdefault('pages', {})
        self._now = datetime.now()

    def update_stats(self):
        self._update_total_count()
        self._update_page_count()

        delta = self._get_time_delta()
        self._update_total_time(delta)
        self._update_page_time(delta)

        print(self._stats)
        self._update_session()

    def _update_session(self):
        self.request.session['stats'] = self._stats
        self.request.session['last_request_time'] = self._now.strftime(self.datetime_format)
        self.request.session['last_request_page'] = self.request.path

    def _update_total_count(self):
        total_count = self._stats.get('total_count', 0)
        total_count += 1
        self._stats['total_count'] = total_count

    def _update_total_time(self, delta):
        total_time = self._stats.get('total_time', 0)
        total_time += delta.total_seconds()
        self._stats['total_time'] = total_time

    def _update_page_count(self):
        page_stats = self._pages.get(self.request.path, {})
        count = page_stats.get('count', 0)
        count += 1
        page_stats['count'] = count
        self._pages[self.request.path] = page_stats

    def _update_page_time(self, delta):
        last_request_page = self.request.session.get('last_request_page')
        if last_request_page is not None:
            last_page_stats = self._pages.get(last_request_page, {})
            time = last_page_stats.get('time', 0)
            time += delta.total_seconds()
            last_page_stats['time'] = time
            self._pages[last_request_page] = last_page_stats

    def _get_time_delta(self):
        last_request_time = self.request.session.get('last_request_time')
        if last_request_time is not None:
            last_request_time = datetime.strptime(last_request_time, self.datetime_format)
        else:
            last_request_time = self._now
        return self._now - last_request_time
