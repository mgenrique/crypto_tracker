from sqlalchemy.orm import Session
from app.models.wallet import Wallet
from app.models.exchange import Exchange
from app.services.blockchain import blockchain_service
from app.services.token_service import token_service
from typing import Dict, Optional

class PortfolioService:
    @staticmethod
    def get_portfolio_summary(user_id: int, db: Session) -> Dict:
        """Obtener resumen de portfolio"""
        wallets = db.query(Wallet).filter(Wallet.user_id == user_id).all()
        exchanges = db.query(Exchange).filter(Exchange.user_id == user_id).all()
        
        total_balance = 0
        wallet_data = []
        
        # Calcular balance de wallets
        for wallet in wallets:
            try:
                balance = blockchain_service.get_balance(wallet.address, wallet.network)
                wallet.balance = balance
                total_balance += balance
                wallet_data.append({
                    "id": wallet.id,
                    "name": wallet.name,
                    "address": wallet.address,
                    "network": wallet.network,
                    "balance": balance
                })
            except Exception as e:
                print(f"Error fetching balance for {wallet.address}: {str(e)}")
        
        # Calcular balance de exchanges
        exchange_data = []
        for exchange in exchanges:
            exchange_balances = exchange_service.get_account_balance()
            if exchange_balances:
                exchange_total = sum(exchange_balances.values())
                total_balance += exchange_total
                exchange_data.append({
                    "id": exchange.id,
                    "name": exchange.name,
                    "balance": exchange_total
                })
        
        return {
            "total_balance": total_balance,
            "wallets": wallet_data,
            "exchanges": exchange_data,
            "wallet_count": len(wallets),
            "exchange_count": len(exchanges)
        }
    
    @staticmethod
    def get_asset_allocation(user_id: int, db: Session) -> Dict:
        """Obtener asignación de activos"""
        summary = PortfolioService.get_portfolio_summary(user_id, db)
        
        allocation = {
            "wallets": {
                "percentage": 0,
                "value": 0
            },
            "exchanges": {
                "percentage": 0,
                "value": 0
            }
        }
        
        total = summary['total_balance']
        if total > 0:
            wallet_value = sum(w['balance'] for w in summary['wallets'])
            exchange_value = sum(e['balance'] for e in summary['exchanges'])
            
            allocation['wallets']['value'] = wallet_value
            allocation['wallets']['percentage'] = (wallet_value / total) * 100
            allocation['exchanges']['value'] = exchange_value
            allocation['exchanges']['percentage'] = (exchange_value / total) * 100
        
        return allocation

portfolio_service = PortfolioService()
