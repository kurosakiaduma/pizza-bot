from botbuilder.core import TurnContext
from botbuilder.schema import ActivityTypes

class PizzaChatBot:
    def __init__(self):
        self.menu = {
            "Margherita": 10.99,
            "Pepperoni": 12.99,
            "Vegetarian": 11.99,
            "Custom": 14.99,
        }
        self.toppings = {
            "Mushrooms": 1.50,
            "Olives": 1.00,
            "Onions": 1.00,
        }
        self.order = {
            "pizza": [],
            "toppings": [],
        }

    async def on_turn(self, turn_context:TurnContext):
        if turn_context.activity.type == ActivityTypes.conversation_update:
            await turn_context.send_activity("Hello, welcome to Pizza Pizzeria!\nI will be your virtual assistant for all orders and related inquiries")
        elif turn_context.activity.type == ActivityTypes.message:
            user_message = turn_context.activity.text
            if user_message == "Order":
                await turn_context.send_activity("We have no pizzas available")
            elif user_message in self.menu:
                if user_message == 'Custom':
                    await self.customize_pizza(turn_context)
                else:
                    self.order["pizza"].append(user_message)
                    await turn_context.send_activity(f"{user_message} added to your order.")
            else:
                await turn_context.send_activity("Sorry, we don't have that on the menu. Please choose again.")

    async def customize_pizza(self, turn_context):
        for topping, price in self.toppings.items():
            await turn_context.send_activity(f"Do you want {topping}? (Type 'yes' or 'no')")
            # Here you need to wait for the user's response and add the topping to the order if the user says 'yes'
        await turn_context.send_activity("Custom pizza added to your order.")
