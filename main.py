from shipping_company import ShippingCompany
import matplotlib.pyplot as plt
import numpy as np

RUN_ONLY_1_DAY = True # built for multiday simulation

def main():
    lindas_delivery_company = ShippingCompany()

    day = 0
    while lindas_delivery_company.amt_packages > 0:
        lindas_delivery_company.reset_fleet()
        print(f"day {day} starts with {len(lindas_delivery_company.packages)} packages")

        lindas_delivery_company.load_fleet()

        print("\nResults:")
        for truck in lindas_delivery_company.fleet:
            truck.print_report()

            weight_data = [package.weight for package in truck.packages]
            price_category_data = [package.price_category for package in truck.packages]
            show_subplot(weight_data, "Frequency", "weight in kg", f"Truck {truck.id} weight data")
            show_subplot(price_category_data, "Frequency", "Price category", f"Truck {truck.id} price category data")

        day += 1

        if RUN_ONLY_1_DAY: break

        lindas_delivery_company.increment_late_days()

    print(f"{lindas_delivery_company.amt_packages} packages remaining")
    print(f"{lindas_delivery_company.calculate_profit_fleet()} profit made today")
    print(f"{lindas_delivery_company.calculate_sum_price_inventory()} profit remaining in inventory")
    print(f"\n\nInitial late fees: {lindas_delivery_company.initial_late_fees}")
    print(f"{lindas_delivery_company.calculate_late_fees_fleet()} sek late fee remaining")

    weight_data = [package.weight for package in lindas_delivery_company.packages]
    price_category_data = [package.price_category for package in lindas_delivery_company.packages]

    show_subplot(weight_data, "Frequency", "weight in kg", "Inventory weight data after day 1")
    show_subplot(price_category_data, "Frequency", "Price category", "Inventory price category data after day 1")

def show_subplot(data: list, ylabel: str, xlabel: str, title: str):
    median = np.median(data)
    variance = np.var(data)
    std = np.std(data)

    plt.hist(data, label=f"Variance {variance:.2f}", color='xkcd:eggshell')
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)

    plt.axvline(median, color='m', label=f'Median: {median:.2f}')
    plt.axvline(median + std, color='0.8', label=f'standard deviation: +{std:.2f}')
    plt.axvline(median - std, color='0.8', label=f'standard deviation: -{std:.2f}')

    plt.legend()
    plt.show()

if __name__ == '__main__':
    main()