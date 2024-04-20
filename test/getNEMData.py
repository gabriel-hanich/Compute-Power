import opennem

def get_nsw_generation_data(year):
    try:
        # Initialize the openNEM client
        client = opennem.OpenNEMClient()

        # Fetch generation data for NSW
        nsw_generation = client.fueltechs()

        print(nsw_generation)

    except Exception as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    target_year = 2024  # Specify the desired year
    get_nsw_generation_data(target_year)
