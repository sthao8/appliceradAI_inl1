from shipping_company import ShippingCompany

def main():
    lindas_delivery_company = ShippingCompany()
    print(f"Initial total profit minus loss: {lindas_delivery_company.initial_total_potential_profit}")
    total_profit = 0
    day = 1
    while len(lindas_delivery_company.packages) > 0:
        print(f"day {day}: {len(lindas_delivery_company.packages)} packages")
        # best_solution = shipping_company.genetic_algorithm()
        # print(f"Best solution fitness: {best_solution.fitness}")
        # print(f"Best solution profit: {best_solution.total_profit}")
        lindas_delivery_company.load_fleet()
        for truck in lindas_delivery_company.fleet:
            truck.print_report()
        daily_profit = lindas_delivery_company.calculate_total_profit()
        print(f"Total daily profit: {daily_profit} sek")
        print(f"{len(lindas_delivery_company.packages)} packages remaining")
        print(f"Late fees remaining: {lindas_delivery_company.calculate_remaining_late_fees()} sek")
        print(f"Remaining total profit minus loss: {lindas_delivery_company.calculate_total_potential_profit_minus_loss()}")
        total_profit += daily_profit
        day += 1
    print(f"Total days: {day}")
    print(f"Total total profit: {total_profit}")

if __name__ == '__main__':
    main()