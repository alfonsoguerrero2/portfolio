import pandas as pd
from datetime import datetime
from .models import Portfolio, Asset, AssetPrice, PortfolioAsset
from decimal import Decimal, InvalidOperation

def load_data_from_excel():
    # Read the Excel file
    file_path = r"C:\Users\alfon\OneDrive\6semester\portafolio2\myproject\assets\datos.xlsx"
    excel_data = pd.ExcelFile(file_path)

    portfolio_prices = excel_data.parse(sheet_name=1)
    
    asset_names = portfolio_prices.columns[1:]

    for name in asset_names:
        # Create the asset if it doesn't already exist
        asset_obj, created = Asset.objects.get_or_create(name=name)
        if created:
            print(f"Created new asset: {asset_obj.name}")
        else:
            print(f"Asset already exists: {asset_obj.name}")

    #tiene 17 assets 
    for index, row in portfolio_prices.iterrows():
        print(f"Row {index}: {row.tolist()}")
        date = pd.to_datetime(row.iloc[0], dayfirst=True, errors='coerce')

        asset_column = 1
        for price in row.iloc[1:]:
            if asset_column <= len(asset_names):
                asset_name = asset_names[asset_column - 1]
                AssetPrice.objects.get_or_create( asset=Asset.objects.get(name=asset_name), date=date, defaults={"price": price})
                asset_column = asset_column + 1





    # Parse the first sheet (Portfolio weights)
    portfolio_weights = excel_data.parse(sheet_name=0)
    start_date = datetime.strptime("15/02/2022", "%d/%m/%Y").date()

    # Create portfolios with fixed start date
    portfolio_1, _ = Portfolio.objects.get_or_create(name="Portfolio 1", defaults={"created_at": start_date})
    portfolio_2, _ = Portfolio.objects.get_or_create(name="Portfolio 2", defaults={"created_at": start_date})
    print(f"Portfolios created: {portfolio_1}, {portfolio_2}")
    for index, row in portfolio_weights.iterrows():
        # Skip header row if not automatically handled
        #print(f"Row {index}: {row.tolist()}")
        try:
            date = pd.to_datetime(row.iloc[0], dayfirst=True, errors='coerce')
            if pd.isnull(date):
                continue
        except ValueError:
            continue  # Skip rows where date is not parsable

        asset_name = row.iloc[1]
        weight_1 = row.iloc[2]
        weight_2 = row.iloc[3]


        print(f"Processing asset: {asset_name}, Weights: {weight_1}, {weight_2}")
        try:
            asset_obj = Asset.objects.get(name=asset_name)
        except Asset.DoesNotExist:
            print(f"Asset not found: {asset_name}")
            continue

        PortfolioAsset.objects.get_or_create(portfolio=portfolio_1, asset=asset_obj, defaults={"amount": 0, "weight": weight_1})

        # Create PortfolioAsset for Portfolio 2
        PortfolioAsset.objects.get_or_create(portfolio=portfolio_2, asset=asset_obj, defaults={"amount": 0, "weight": weight_2})





def initialize_portfolio_amounts():
    # Step 1: Define initial investment and date
    initial_capital = Decimal("1000000")
    start_date = datetime.strptime("15/02/2022", "%d/%m/%Y").date()

    # Step 2: Get both portfolios
    portfolios = Portfolio.objects.filter(name__in=["Portfolio 1", "Portfolio 2"])

    for portfolio in portfolios:
        print(f"\nUpdating assets for {portfolio.name}")
        for holding in portfolio.holdings.all():
            try:
                # Step 3: Get price of asset on the start date
                price = holding.asset.prices.get(date=start_date).price
                investment_amount = initial_capital * holding.weight
                amount = investment_amount / price

                # Step 4: Update the amount field
                holding.amount = amount.quantize(Decimal('0.0001'))  # Precision to 4 decimals
                holding.save()

                print(f"Updated {holding.asset.name}: amount = {holding.amount}, price = {price}")

            except AssetPrice.DoesNotExist:
                print(f"No price found for {holding.asset.name} on {start_date}")
            except InvalidOperation:
                print(f"Invalid operation for {holding.asset.name} due to zero price or weight")