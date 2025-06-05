# app.py
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os, time
from datetime import datetime

# Plaid Python v31 imports
from plaid.api import plaid_api
from plaid.configuration import Configuration, Environment
from plaid.api_client import ApiClient
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.products import Products
from plaid.exceptions import ApiException
from flask import send_from_directory

# 1. Load environment variables
load_dotenv()

# 2. Plaid credentials
PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET    = os.getenv("PLAID_SECRET")

# 3. Configure Plaid sandbox client
configuration = Configuration(
    host=Environment.Sandbox,
    api_key={"clientId": PLAID_CLIENT_ID, "secret": PLAID_SECRET}
)
api_client   = ApiClient(configuration)
plaid_client = plaid_api.PlaidApi(api_client)

# 4. Flask app
app = Flask(__name__)

print("▶ DEBUG MODE:", app.debug)

@app.route("/")
def index():
    return "CreditMaestro MCP adapter is running!"

@app.route("/ping")
def ping():
    return "pong"

@app.route("/.well-known/ai-plugin.json")
def plugin_manifest():
    # app.root_path is the directory containing app.py
    return send_from_directory(app.root_path, "ai-plugin.json", mimetype="application/json")

@app.route("/.well-known/openapi.yaml")
def openapi_spec():
    return send_from_directory(app.root_path, "openapi.yaml", mimetype="text/yaml")

@app.route("/.well-known/logo.png")
def plugin_logo():
    # static/logo.png under the project root
    return send_from_directory(os.path.join(app.root_path, "static"), "logo.png", mimetype="image/png")



def fetch_transactions_with_retry(access_token, start, end, retries=5, delay=1):
    """Retry /transactions/get until the product is ready or retries exhausted."""
    tx_req = TransactionsGetRequest(
        access_token=access_token,
        start_date=start,
        end_date=end
    )
    for _ in range(retries):
        try:
            return plaid_client.transactions_get(tx_req).transactions
        except ApiException as e:
            err_json = e.body and e.body.decode() if isinstance(e.body, (bytes, bytearray)) else str(e.body)
            if "PRODUCT_NOT_READY" in err_json:
                time.sleep(delay)
                continue
            raise  # re‑raise other errors
    raise RuntimeError("Transactions product not ready after retrying.")


@app.route("/getTransactions", methods=["POST"])
def get_transactions():
    """Return sandbox transactions for the provided date range."""
    body = request.get_json() or {}
    try:
        start = datetime.fromisoformat(body["startDate"]).date()
        end   = datetime.fromisoformat(body["endDate"]).date()
    except Exception:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    # a) Create Plaid sandbox item
    sandbox_pt_req = SandboxPublicTokenCreateRequest(
        institution_id="ins_109508",
        initial_products=[Products("transactions")]
    )
    public_token = plaid_client.sandbox_public_token_create(sandbox_pt_req).public_token

    # b) Exchange for access token
    access_token = (
        plaid_client.item_public_token_exchange(
            ItemPublicTokenExchangeRequest(public_token=public_token)
        ).access_token
    )

    # c) Fetch transactions with retry until ready
    try:
        transactions = fetch_transactions_with_retry(access_token, start, end)
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 504

    return jsonify([t.to_dict() for t in transactions])


if __name__ == "__main__":
    app.run(port=5000, debug=False, use_reloader=False)
    
