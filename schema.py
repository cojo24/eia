import datetime as dt
import pandas as pd

from .client import EIA
from collections import namedtuple
from typing import Optional, Union


CategoryCollection = namedtuple('CategoryCollection', 'items')
SeriesCollection = namedtuple('SeriesCollection', 'items')


class Category:

    def __init__(
            self,
            category_id: Union[int, str],
            name: str,
            notes: str,
            parent_category_id: Union[int, str],
            childcategories: Optional[CategoryCollection] = None,
            childseries: Optional[SeriesCollection] = None,
    ):
        self.category_id = category_id
        self.name = name
        self.notes = notes
        self.parent_category_id = parent_category_id
        self.childcategories = CategoryCollection([]) if childcategories is None else childcategories
        self.childseries = SeriesCollection([]) if childseries is None else childseries

    def __repr__(self):
        cat = '[ Category: {}'.format(self.name)

        attrs = [
            '\n\t{} = {}'.format(a, self.__getattribute__(a))
            for a in self.__dir__()
            if not a.startswith('__') and a not in ['childcategories', 'childseries']
            if a in [
                   'category_id',
                   'name',
                   'notes',
                   'parent_category_id',
               ]
        ]

        ccats = self.__getattribute__('childcategories')
        cseries = self.__getattribute__('childseries')

        attrs.append('\n\tchildcategories = [{} Category Objects]'.format(len(ccats.items)))
        attrs.append('\n\tchildseries = [{} Series Objects]'.format(len(cseries.items)))

        attrs = ''.join(attrs)
        cat = cat + attrs + ' ]'

        return cat

    @classmethod
    def from_category_id(cls, category_id: Union[int, str], eia_client: EIA, load_series=False):
        json = eia_client.get_category(category_id)
        json = json['category']
        category = cls(
            category_id=json['category_id'],
            name=json['name'],
            notes=json['notes'],
            parent_category_id=json['parent_category_id'],
        )
        # For each child category/series:
        # Ping EIA api and instantiate classes
        childcategories = CategoryCollection([
            # recursive call
            cls.from_category_id(c['category_id'], eia_client, load_series=load_series)
            for c in json['childcategories']
        ])
        category.childcategories = childcategories

        if load_series is True:
            childseries = SeriesCollection([
                Series.from_series_id(s['series_id'], eia_client)
                for s in json['childseries']
            ])
            for s in childseries.items:
                s.category_id = category.category_id
            category.childseries = childseries

        return category


class Series:

    def __init__(
            self,
            series_id: str,
            name: str,
            units: str,
            freq: str,
            desc: str,
            start: dt.datetime,
            end: dt.datetime,
            updated: dt.datetime,
            data: pd.DataFrame,
            category_id: Optional[Union[int, str]] = None,
    ):
        self.series_id = series_id
        self.name = name
        self.units = units
        self.freq = freq
        self.desc = desc
        self.start = start
        self.end = end
        self.updated = updated
        self.data = data
        self.category_id = category_id

    def __repr__(self):
        s = '[ Series: {}'.format(self.name)
        attrs = ''.join([
            '\n\t{} = {}'.format(a, self.__getattribute__(a))
            for a in self.__dir__()
            if a in [
                'series_id',
                'name',
                'units',
                'freq',
                'desc',
                'start',
                'end',
                'updated',
                'category_id',
            ]
        ])
        s = s + attrs + ' ]'
        return s

    @classmethod
    def from_series_id(cls, series_id: Union[int, str], eia_client: EIA, dt_format=None):

        json = eia_client.get_series(series_id)
        json = json['series'][0]

        data = pd.DataFrame(json['data'], columns=['Period', json['series_id']])
        data['Period'] = pd.to_datetime(data['Period'], format=dt_format)
        data = data.set_index('Period')

        start = pd.to_datetime(json['start'], format=dt_format)
        end = pd.to_datetime(json['end'], format=dt_format)
        updated = pd.to_datetime(json['updated'])

        return cls(
            series_id=json['series_id'],
            name=json.get('name', ''),
            units=json['units'],
            freq=json['f'],
            desc=json.get('description', ''),
            start=start,
            end=end,
            updated=updated,
            data=data,
        )
