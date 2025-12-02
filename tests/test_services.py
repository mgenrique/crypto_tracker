# main.py o tests
from src.database import get_db_manager
from src.services import PortfolioService, TaxCalculator, ReportGenerator
from decimal import Decimal

# Initialize services
db = get_db_manager()
portfolio_svc = PortfolioService(db)
tax_calc = TaxCalculator(db)
report_gen = ReportGenerator(db)

# Add wallet
wallet = portfolio_svc.add_wallet(
    address="0x742d35Cc6634C0532925a3b844Bc0e8e15b51d93",
    wallet_type="hot",
    network="ethereum",
    label="My Main Wallet"
)
wallet_id = wallet["id"]

# Record transaction
portfolio_svc.record_transaction(
    wallet_id=wallet_id,
    tx_hash="0xabc123...",
    tx_type="buy",
    token_in="ETH",
    token_out="ETH",
    amount_in=Decimal("0"),
    amount_out=Decimal("1.5"),
    price_usd_in=Decimal("2000")
)

# Calculate taxes (FIFO)
tax_summary = tax_calc.calculate_fifo(
    wallet_id=wallet_id,
    year=2024,
    token="ETH"
)

# Generate reports
portfolio_report = report_gen.generate_portfolio_summary()
tax_report = report_gen.generate_tax_report(wallet_id=wallet_id, year=2024)

print(f"Portfolio Value: {portfolio_report['total_value_usd']} USD")
print(f"Tax Liability: {tax_report['summary']['estimated_tax_usd']} USD")
