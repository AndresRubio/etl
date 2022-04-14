import os
import pathlib
import unittest
import pandas as pd

from unittest import TestCase
from aws.S3Handler import S3Handler
from monitoring import log
from steps.etl.main import Etl


class EtlModuleTests(TestCase):

    def test_etl_step(self):
        log.info('Starting etl test...')
        raw_files_ids = [dir_path for dir_path in os.listdir(self.input_path + "inputs")]
        raw_data = self.etl.ingest(raw_files_ids)
        log.info(f'Ingested data size: {len(raw_data)}')

        df = self.etl.transform(raw_data)
        log.info(f'Applied transformation to data size: {len(df)}')

        validated_df = self.etl.validation(df)
        log.info(f'Applied validation to data size: {len(validated_df)}')

        self.etl.splitting(validated_df)
        log.info(f'Applied Splitting to data size: {len(validated_df)}')

        self.etl.load(validated_df)
        log.info(f'Loaded to data size: {len(validated_df)}')

        assert len(validated_df) == len(pd.read_csv(self.input_path + "results/expected.csv"))

    def setUp(self) -> None:
        self.input_path = str(pathlib.Path().absolute()) + "/resources/"
        self.s3 = S3Handler('test-bucket')
        self.etl = Etl(None, self.s3)
        self.s3.create_bucket()

        for dir_path in os.listdir(self.input_path + "inputs"):
            self.s3.upload_file(f'{self.input_path}inputs/{dir_path}', dir_path)
        # self.spark = (
        #     SparkSession
        #         .builder
        #         .master('local[*]')
        #         .config('spark.driver.host', 'localhost')
        #         .appName('ML: Unit test')
        #         .getOrCreate()
        # )

    def tearDown(self) -> None:
        # self.spark.stop()
        self.s3.delete_bucket()


if __name__ == '__main__':
    unittest.main()
