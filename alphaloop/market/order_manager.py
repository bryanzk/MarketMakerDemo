import logging

logger = logging.getLogger(__name__)

class OrderManager:
    def sync_orders(self, current_orders, target_orders):
        """
        Compares current and target orders to determine actions.
        Returns: (to_cancel_ids, to_place_orders)
        """
        to_cancel = []
        to_place = []

        # Helper to group by side
        curr_buy = next((o for o in current_orders if o['side'] == 'buy'), None)
        curr_sell = next((o for o in current_orders if o['side'] == 'sell'), None)

        tgt_buy = next((o for o in target_orders if o['side'] == 'buy'), None)
        tgt_sell = next((o for o in target_orders if o['side'] == 'sell'), None)

        # Compare Buy
        if tgt_buy:
            if curr_buy:
                # Check if price changed significantly (e.g. > 0.05%)
                # Or simple equality for MVP
                if abs(curr_buy['price'] - tgt_buy['price']) > 0.01: # Tolerance
                    to_cancel.append(curr_buy['id'])
                    to_place.append(tgt_buy)
                else:
                    # Keep current, do nothing
                    pass
            else:
                to_place.append(tgt_buy)
        else:
            if curr_buy:
                to_cancel.append(curr_buy['id'])

        # Compare Sell
        if tgt_sell:
            if curr_sell:
                if abs(curr_sell['price'] - tgt_sell['price']) > 0.01:
                    to_cancel.append(curr_sell['id'])
                    to_place.append(tgt_sell)
                else:
                    pass
            else:
                to_place.append(tgt_sell)
        else:
            if curr_sell:
                to_cancel.append(curr_sell['id'])

        return to_cancel, to_place
