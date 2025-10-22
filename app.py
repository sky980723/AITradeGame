from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import time
import threading
from datetime import datetime

from trading_engine import TradingEngine
from market_data import MarketDataFetcher
from ai_trader import AITrader
from database import Database

app = Flask(__name__)
CORS(app)

db = Database('trading_bot.db')
market_fetcher = MarketDataFetcher()
trading_engines = {}
auto_trading = True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/models', methods=['GET'])
def get_models():
    models = db.get_all_models()
    return jsonify(models)

@app.route('/api/models', methods=['POST'])
def add_model():
    data = request.json
    model_id = db.add_model(
        name=data['name'],
        api_key=data['api_key'],
        api_url=data['api_url'],
        model_name=data['model_name'],
        initial_capital=float(data.get('initial_capital', 100000))
    )
    
    try:
        model = db.get_model(model_id)
        trading_engines[model_id] = TradingEngine(
            model_id=model_id,
            db=db,
            market_fetcher=market_fetcher,
            ai_trader=AITrader(
                api_key=model['api_key'],
                api_url=model['api_url'],
                model_name=model['model_name']
            )
        )
        print(f"[INFO] Model {model_id} ({data['name']}) initialized")
    except Exception as e:
        print(f"[ERROR] Model {model_id} initialization failed: {e}")
    
    return jsonify({'id': model_id, 'message': 'Model added successfully'})

@app.route('/api/models/<int:model_id>', methods=['PUT'])
def update_model(model_id):
    data = request.json or {}
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    name = data.get('name')
    api_key = data.get('api_key')
    api_url = data.get('api_url')
    model_name = data.get('model_name')
    initial_capital = data.get('initial_capital')
    
    if name is not None:
        name = name.strip()
        if not name:
            return jsonify({'error': 'name cannot be empty'}), 400
    if api_key is not None:
        api_key = api_key.strip()
        if not api_key:
            return jsonify({'error': 'api_key cannot be empty'}), 400
    if api_url is not None:
        api_url = api_url.strip()
        if not api_url:
            return jsonify({'error': 'api_url cannot be empty'}), 400
    if model_name is not None:
        model_name = model_name.strip()
        if not model_name:
            return jsonify({'error': 'model_name cannot be empty'}), 400
    
    if initial_capital is not None:
        try:
            initial_capital = float(initial_capital)
        except ValueError:
            return jsonify({'error': 'initial_capital must be a number'}), 400
    
    if not any(
        value is not None
        for value in (name, api_key, api_url, model_name, initial_capital)
    ):
        return jsonify({'error': 'No fields provided to update'}), 400
    
    try:
        updated = db.update_model(
            model_id,
            name=name,
            api_key=api_key,
            api_url=api_url,
            model_name=model_name,
            initial_capital=initial_capital
        )
        
        if not updated:
            if not db.get_model(model_id):
                return jsonify({'error': 'Model not found'}), 404
            return jsonify({'error': 'No changes were applied'}), 400
        
        updated_model = db.get_model(model_id)
        if model_id in trading_engines and updated_model:
            trading_engines[model_id].ai_trader = AITrader(
                api_key=updated_model['api_key'],
                api_url=updated_model['api_url'],
                model_name=updated_model['model_name']
            )
            print(f"[INFO] Model {model_id} ({updated_model['name']}) reloaded with new settings")
        elif updated_model:
            print(f"[INFO] Model {model_id} ({updated_model['name']}) updated")
        
        return jsonify({'message': 'Model updated successfully'})
    except Exception as e:
        print(f"[ERROR] Update model {model_id} failed: {e}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/models/<int:model_id>', methods=['DELETE'])
def delete_model(model_id):
    try:
        model = db.get_model(model_id)
        model_name = model['name'] if model else f"ID-{model_id}"
        
        db.delete_model(model_id)
        if model_id in trading_engines:
            del trading_engines[model_id]
        
        print(f"[INFO] Model {model_id} ({model_name}) deleted")
        return jsonify({'message': 'Model deleted successfully'})
    except Exception as e:
        print(f"[ERROR] Delete model {model_id} failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/<int:model_id>/portfolio', methods=['GET'])
def get_portfolio(model_id):
    prices_data = market_fetcher.get_current_prices(['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'DOGE'])
    current_prices = {coin: prices_data[coin]['price'] for coin in prices_data}
    
    portfolio = db.get_portfolio(model_id, current_prices)
    account_value = db.get_account_value_history(model_id, limit=100)
    
    return jsonify({
        'portfolio': portfolio,
        'account_value_history': account_value
    })

@app.route('/api/models/<int:model_id>/trades', methods=['GET'])
def get_trades(model_id):
    limit = request.args.get('limit', 50, type=int)
    trades = db.get_trades(model_id, limit=limit)
    return jsonify(trades)

@app.route('/api/models/<int:model_id>/conversations', methods=['GET'])
def get_conversations(model_id):
    limit = request.args.get('limit', 20, type=int)
    conversations = db.get_conversations(model_id, limit=limit)
    return jsonify(conversations)

@app.route('/api/market/prices', methods=['GET'])
def get_market_prices():
    coins = ['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'DOGE']
    prices = market_fetcher.get_current_prices(coins)
    return jsonify(prices)

@app.route('/api/models/<int:model_id>/execute', methods=['POST'])
def execute_trading(model_id):
    if model_id not in trading_engines:
        model = db.get_model(model_id)
        if not model:
            return jsonify({'error': 'Model not found'}), 404
        
        trading_engines[model_id] = TradingEngine(
            model_id=model_id,
            db=db,
            market_fetcher=market_fetcher,
            ai_trader=AITrader(
                api_key=model['api_key'],
                api_url=model['api_url'],
                model_name=model['model_name']
            )
        )
    
    try:
        result = trading_engines[model_id].execute_trading_cycle()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def trading_loop():
    print("[INFO] Trading loop started")
    
    while auto_trading:
        try:
            if not trading_engines:
                time.sleep(30)
                continue
            
            print(f"\n{'='*60}")
            print(f"[CYCLE] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"[INFO] Active models: {len(trading_engines)}")
            print(f"{'='*60}")
            
            for model_id, engine in list(trading_engines.items()):
                try:
                    print(f"\n[EXEC] Model {model_id}")
                    result = engine.execute_trading_cycle()
                    
                    if result.get('success'):
                        print(f"[OK] Model {model_id} completed")
                        if result.get('executions'):
                            for exec_result in result['executions']:
                                signal = exec_result.get('signal', 'unknown')
                                coin = exec_result.get('coin', 'unknown')
                                msg = exec_result.get('message', '')
                                if signal != 'hold':
                                    print(f"  [TRADE] {coin}: {msg}")
                    else:
                        error = result.get('error', 'Unknown error')
                        print(f"[WARN] Model {model_id} failed: {error}")
                        
                except Exception as e:
                    print(f"[ERROR] Model {model_id} exception: {e}")
                    import traceback
                    print(traceback.format_exc())
                    continue
            
            print(f"\n{'='*60}")
            print(f"[SLEEP] Waiting 3 minutes for next cycle")
            print(f"{'='*60}\n")
            
            time.sleep(180)
            
        except Exception as e:
            print(f"\n[CRITICAL] Trading loop error: {e}")
            import traceback
            print(traceback.format_exc())
            print("[RETRY] Retrying in 60 seconds\n")
            time.sleep(60)
    
    print("[INFO] Trading loop stopped")

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    models = db.get_all_models()
    leaderboard = []
    
    prices_data = market_fetcher.get_current_prices(['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'DOGE'])
    current_prices = {coin: prices_data[coin]['price'] for coin in prices_data}
    
    for model in models:
        portfolio = db.get_portfolio(model['id'], current_prices)
        account_value = portfolio.get('total_value', model['initial_capital'])
        returns = ((account_value - model['initial_capital']) / model['initial_capital']) * 100
        
        leaderboard.append({
            'model_id': model['id'],
            'model_name': model['name'],
            'account_value': account_value,
            'returns': returns,
            'initial_capital': model['initial_capital']
        })
    
    leaderboard.sort(key=lambda x: x['returns'], reverse=True)
    return jsonify(leaderboard)

def init_trading_engines():
    try:
        models = db.get_all_models()
        
        if not models:
            print("[WARN] No trading models found")
            return
        
        print(f"\n[INIT] Initializing trading engines...")
        for model in models:
            model_id = model['id']
            model_name = model['name']
            
            try:
                trading_engines[model_id] = TradingEngine(
                    model_id=model_id,
                    db=db,
                    market_fetcher=market_fetcher,
                    ai_trader=AITrader(
                        api_key=model['api_key'],
                        api_url=model['api_url'],
                        model_name=model['model_name']
                    )
                )
                print(f"  [OK] Model {model_id} ({model_name})")
            except Exception as e:
                print(f"  [ERROR] Model {model_id} ({model_name}): {e}")
                continue
        
        print(f"[INFO] Initialized {len(trading_engines)} engine(s)\n")
        
    except Exception as e:
        print(f"[ERROR] Init engines failed: {e}\n")

if __name__ == '__main__':
    db.init_db()
    
    print("\n" + "=" * 60)
    print("AI Trading Platform")
    print("=" * 60)
    
    init_trading_engines()
    
    if auto_trading:
        trading_thread = threading.Thread(target=trading_loop, daemon=True)
        trading_thread.start()
        print("[INFO] Auto-trading enabled")
    
    print("\n" + "=" * 60)
    print("Server: http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("=" * 60 + "\n")
    
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
