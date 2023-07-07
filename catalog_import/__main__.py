from data import providers
from models import main as main_model
from threading import Thread


def main(**kwargs):
    """
    Entry point for the main program execution.

    The method initializes the `Main` instance with the provided keyword arguments and calls the `execute` method to start
    the main program execution.

    Arguments:
        **kwargs: Keyword arguments to be passed to the `Main` instance.

    Returns:
        None
    """
    main = main_model.Main(**kwargs)
    main.execute()

if __name__ == "__main__":
    """
    Main entry point of the program.

    The code block initializes multiple threads to execute the `main` function concurrently for each provider in the
    `providers_dict`. It creates a separate thread for each provider and starts its execution. After starting all the
    threads, the code block waits for each thread to complete by calling the `join` method.

    Returns:
        None
    """
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
