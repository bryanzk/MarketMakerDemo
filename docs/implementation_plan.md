# Robust Start/Stop Logic & UI Feedback

## Goal
Implement a safe and robust lifecycle for the bot, ensuring that stopping the bot cancels all open orders to prevent risk, and that errors are gracefully handled and reported to the UI.

## User Review Required
> [!IMPORTANT]
> **Stop Logic Change**: Stopping the bot will now **automatically cancel all open orders**. This is a safety feature.

## Proposed Changes

### Backend (`market_maker/`)

#### [MODIFY] [exchange.py](file:///Users/kezheng/Codes/VibeCoding/market_maker/exchange.py)
- Add `cancel_all_orders(self)` method.
    - Try using `ccxt`'s `cancel_all_orders`.
    - Fallback to `fetch_open_orders` + `cancel_orders` if not supported.

#### [MODIFY] [main.py](file:///Users/kezheng/Codes/VibeCoding/market_maker/main.py)
- Update `BotEngine` class:
    - `start()`:
        - Check connection (e.g., fetch account data) before starting thread.
        - Reset `self.status['error']`.
    - `stop()`:
        - Set `running = False`.
        - Join thread.
        - **Call `self.client.cancel_all_orders()`**.
    - `_run_loop()`:
        - Wrap entire loop in `try...except Exception`.
        - On exception:
            - Log error.
            - Set `self.status['error']` to the exception message.
            - Call `self.stop()` (which cancels orders).
            - Set `self.status['active'] = False`.

### Frontend (`market_maker/templates/`)

#### [MODIFY] [index.html](file:///Users/kezheng/Codes/VibeCoding/market_maker/templates/index.html)
- Update `fetchStatus()` JS function:
    - Handle `data.error` field.
    - If `data.error` exists, show an error alert or badge.
    - Update "Start" and "Stop" buttons:
        - Disable "Start" if running.
        - Disable "Stop" if stopped.
- Add CSS for `status-error`.

## Verification Plan

### Automated Tests
- None (Manual verification preferred for integration logic).

### Manual Verification
1. **Start Bot**: Click "Start". Verify status becomes "RUNNING" and buttons update.
2. **Stop Bot**: Click "Stop". Verify status becomes "STOPPED", buttons update, and **all open orders are canceled** (check "Active Orders" table or Binance dashboard).
3. **Error Handling**: Manually raise an exception in `_run_loop` (temporary code change). Verify bot stops, status shows "ERROR", and orders are canceled.
