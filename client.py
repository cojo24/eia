import requests


class EIA:

    _base_url = 'http://api.eia.gov'

    def __init__(self, api_key):
        self.api_key = api_key

    def get_manifest(self):
        resp = requests.get(self._base_url + '/bulk/manifest.txt')
        return resp.json()

    def search_series(self, series_id=None, keyword=None, **kwargs):
        if series_id:
            kwargs['search_term'] = 'series_id'
            kwargs['search_value'] = series_id
        if keyword:
            kwargs['search_term'] = 'name'
            kwargs['search_value'] = keyword
        resp = requests.get(self._base_url + '/search', params=kwargs)
        return resp.json()

    def get_category(self, category_id=None, **kwargs):
        kwargs['api_key'] = self.api_key
        if category_id:
            kwargs['category_id'] = category_id
        resp = requests.get(self._base_url + '/category', params=kwargs)
        return resp.json()

    def get_series(self, series_id, **kwargs):
        kwargs['api_key'] = self.api_key
        kwargs['series_id'] = series_id
        resp = requests.get(self._base_url + '/series', params=kwargs)
        return resp.json()

    def get_series_categories(self, series_id, **kwargs):
        kwargs['api_key'] = self.api_key
        kwargs['series_id'] = series_id
        resp = requests.get(self._base_url + '/series/categories', params=kwargs)
        return resp.json()

    def get_geoset(self, geoset_id, regions, **kwargs):
        kwargs['api_key'] = self.api_key
        kwargs['geoset_id'] = geoset_id
        kwargs['regions'] = ','.join(regions)
        resp = requests.get(self._base_url + '/geoset', params=kwargs)
        return resp.json()

    def get_updates(self, category_id=None, deep=False, rows=50, firstrow=0, **kwargs):
        kwargs['api_key'] = self.api_key
        if category_id:
            kwargs['category_id'] = category_id
        kwargs['deep'] = deep
        kwargs['rows'] = rows
        kwargs['firstrow'] = firstrow
        resp = requests.get(self._base_url + '/updates', params=kwargs)
        return resp.json()
