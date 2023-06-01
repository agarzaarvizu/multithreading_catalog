from catalog_import.data import providers
from catalog_import.models import main as main_model
from threading import Thread


def main(**kwargs):
    main = main_model.Main(**kwargs)
    main.execute()

def execute(event, context):
    threads = []
    providers_dict = providers.providers
    for provider_name, provider_values in providers_dict.items():
        provider = {
            "provider_name": provider_name,
            "provider_values": provider_values,
        }
        x = Thread(target=main, kwargs=provider)
        threads.append(x)
        x.start()

    for thread in threads:
        thread.join()
