CREATE TABLE data (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique identifier for the user
    full_name TEXT NOT NULL,
    pass TEXT NOT NULL,
    email BLOB NOT NULL UNIQUE,
    nonce BLOB,
    tag BLOB,
    TIME_CREATED TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    TIME_UPDATED TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
);  

CREATE TABLE wallet (
    wallet_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    BTC_balance DECIMAL(18, 8),
    ETH_balance DECIMAL(18, 8),
    SOL_balance DECIMAL (18, 8),
    TIME_CREATED TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    TIME_UPDATED TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES data(user_id),
);  

CREATE TABLE transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_wallet_id INTEGER NOT NULL,
    recipient_wallet_id INTEGER NOT NULL,
    amount DECIMAL(18, 8) NOT NULL,
    currency TEXT NOT NULL,
    transaction_type TEXT(transaction_type IN ('SEND', 'RECEIVE')) NOT NULL, 
    status TEXT(status IN ('COMPLETED', 'PENDING', 'FAILED')) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_wallet_id) REFERENCES wallet(wallet_id),
    FOREIGN KEY (recipient_wallet_id) REFERENCES wallet(wallet_id)
)
