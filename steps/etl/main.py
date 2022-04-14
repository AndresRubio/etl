import pandas as pd
import pickle

from io import StringIO
from aws.S3Handler import S3Handler
from monitoring.robustness_metric import is_cluster_robust


class Etl:
    __spark = None

    def __init__(self, spark_session, s3: S3Handler):
        self.__spark = spark_session  # not ready
        self.__s3 = s3

    def ingest(self, data_urls: list):
        # self.__spark.get_data()
        return [pd.read_csv(StringIO(self.__s3.get_content(url))) for url in data_urls]

    def transform(self, raw_data: list, pk=['store_id', 'product_id']):
        grouped_sales_df = raw_data[0].groupby(pk, as_index=False).sum()
        sales_level_0_df = pd.merge(grouped_sales_df, raw_data[1], on=pk)
        sales_level_0_1_df = pd.merge(sales_level_0_df, raw_data[2], on=pk).rename(
            columns={'cluster_id_x': 'level0', 'cluster_id_y': 'level1'})
        return sales_level_0_1_df

    def validation(self, df):
        clusters_ids = df['level0'].unique().tolist() + df['level1'].unique().tolist()

        robustness_l0, robustness_l1 = self.__calculate_robustness(df, clusters_ids)

        df['robustness_l0'] = df.apply(
            lambda row: self.__get_cluster_score(row['level0'], robustness_l0), axis=1)

        df['robustness_l1'] = df.apply(
            lambda row: self.__get_cluster_score(row['level1'], robustness_l1), axis=1)
        return df

    def splitting(self, df):
        # Depending algorithm train, test, dev sets
        pass

    def load(self, df, path='/data/'):
        from datetime import datetime
        now = datetime.now()
        self.__s3.put(pickle.dumps(df),
                      key=f'{path}{datetime.timestamp(now)}')  # No best way but I do not want to save locally

    # TODO automatize to avoid 2 vars
    def __calculate_robustness(self, df, clusters_ids: list):
        robustness_l0 = {}
        robustness_l1 = {}

        for cl in clusters_ids:
            robustness_l0[cl] = is_cluster_robust(df[df['level0'] == cl])
            robustness_l1[cl] = is_cluster_robust(df[df['level1'] == cl])

        return robustness_l0, robustness_l1

    def __get_cluster_score(self, row_level, scores: list):
        return scores[row_level]
