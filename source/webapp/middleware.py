from webapp.stats_counter import StatsCounter


class StatsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        StatsCounter(request).update_stats()
        return self.get_response(request)
