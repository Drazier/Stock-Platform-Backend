# stock-platform-backend
Django-backend for stock platform

User API
Description: This API manages user accounts within the application.

Functions:

register(username, password, email): Creates a new user account.
login(username, password): Authenticates an existing user and provides a session token.
logout(token): Logs out a user and invalidates their session.
get_user(user_id): Retrieves user information based on their ID.
Inputs:

register: Username, password, and email.
login: Username and password.
logout: Session token.
get_user: User ID.
Outputs:

register: User ID or error message.
login: Session token or error message.
logout: Success or error message.
get_user: User data or error message.
Purpose:

This API provides user authentication and management capabilities, enabling users to create accounts, log in, and access their information.

Strategy API
Description: This API manages trading strategies within the application.

Functions:

create_strategy(user_id, name, description, parameters): Creates a new trading strategy.
update_strategy(strategy_id, name, description, parameters): Updates an existing strategy.
delete_strategy(strategy_id): Deletes a strategy.
get_strategy(strategy_id): Retrieves a specific strategy by its ID.
list_strategies(user_id): Retrieves all strategies created by a user.
Inputs:

create_strategy: User ID, strategy name, description, and parameters.
update_strategy: Strategy ID, name, description, and parameters.
delete_strategy: Strategy ID.
get_strategy: Strategy ID.
list_strategies: User ID.
Outputs:

create_strategy: Strategy ID or error message.
update_strategy: Success or error message.
delete_strategy: Success or error message.
get_strategy: Strategy data or error message.
list_strategies: List of strategies or error message.
Purpose:

This API enables users to define and manage trading strategies, allowing them to store, modify, and retrieve their own custom strategies.

TickerSymbol API
Description: This API manages information about ticker symbols within the application.

Functions:

create_ticker_symbol(ticker, symbol_name): Creates a new ticker symbol entry.
get_ticker_symbol(ticker): Retrieves ticker symbol information based on its ticker.
list_ticker_symbols(): Retrieves a list of all available ticker symbols.
Inputs:

create_ticker_symbol: Ticker and symbol name.
get_ticker_symbol: Ticker.
list_ticker_symbols: None.
Outputs:

create_ticker_symbol: Success or error message.
get_ticker_symbol: Ticker symbol data or error message.
list_ticker_symbols: List of ticker symbols or error message.
Purpose:

This API provides access to ticker symbol data, allowing users to retrieve information about specific tickers or browse a list of available tickers.