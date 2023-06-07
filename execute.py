from catalog_import.data import providers
from catalog_import.models import main as main_model
from threading import Thread
import boto3
import time
import datetime


def main(**kwargs):
    time.sleep(1)
    main = main_model.Main(**kwargs)
    main.execute()

def get_metadata(provider_values):
    locations = provider_values.get("locations")
    metadata = {
        "name": provider_values.get("name"),
        "datetime": datetime.datetime.now().strftime("%m-%d-%Y, %H:%M:%S"),
        "i18n": {location.get("location_tag"): location.get("location_label") for location in locations},
    }
    return metadata

def execute(event, context):
    threads = []
    providers_dict = providers.providers
    dynamodb = boto3.resource('dynamodb')
    db_table = dynamodb.Table('test_multithread_db')
    for provider_name, provider_values in providers_dict.items():
        metadata = get_metadata(provider_values)
        provider = {
            "provider_name": provider_name,
            "provider_values": provider_values,
            "db_table": db_table,
            "metadata": metadata,
        }
        x = Thread(target=main, kwargs=provider)
        threads.append(x)
        x.start()

    for thread in threads:
        thread.join()
