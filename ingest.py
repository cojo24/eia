import os
import pandas as pd

from .client import EIA
from fire import Fire


def get_all_updates(eia_client):
    # get number of rows available
    updates = eia_client.get_updates(deep=True)
    rows_avail = updates['data']['rows_available']
    print('Rows Available:', rows_avail)

    row_ct = 0
    all_rows = []
    while rows_avail > 0:
        # iterate through available rows in batches of 10,000
        updates = eia_client.get_updates(deep=True, rows=10000, firstrow=row_ct)

        # add rows to master list
        all_rows += updates['updates']

        # update counters: (rows retrieved, rows left to retrieve)
        rows_returned = updates['data']['rows_returned']
        row_ct += rows_returned
        rows_avail -= rows_returned
        print('Row count:', row_ct)

    df = pd.DataFrame(all_rows)
    df['updated'] = pd.to_datetime(df['updated'])

    return df


def main():
    # TODO: add command line args
    eia = EIA(os.environ['EIA_API_KEY'])
    updates = get_all_updates(eia)


if __name__ == '__main__':
    Fire(main)
