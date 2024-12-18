from shipping_company import ShippingCompany


def main():
    shipping_company = ShippingCompany()
    best_solution = shipping_company.genetic_algorithm()

    #TODO make a script to generate a ton of packages.

if __name__ == '__main__':
    main()