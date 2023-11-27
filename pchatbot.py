import asyncio
import random
from botbuilder.core import TurnContext, MessageFactory, CardFactory
from botbuilder.schema import ActivityTypes, ActionTypes, HeroCard, CardAction, CardImage
from pathlib import Path
class PizzaChatBot:
    def __init__(self):
        self.menu = {
            "Margherita": {"price": 10.99, "image": Path(r"C:\Users\Tevin\Documents\Computer Science\Artifical Intelligence Programming\BotMaker_Pizza\Bot\imgs\margherita.webp")},
            "Pepperoni": {"price": 12.99, "image": Path(r"C:\Users\Tevin\Documents\Computer Science\Artifical Intelligence Programming\BotMaker_Pizza\Bot\imgs\pepperoni.webp")},
            "Vegetarian": {"price": 11.99, "image": Path(r"C:\Users\Tevin\Documents\Computer Science\Artifical Intelligence Programming\BotMaker_Pizza\Bot\imgs\vegetarian.webp")},
            "Hawaiian": {"price": 13.99, "image": Path(r"C:\Users\Tevin\Documents\Computer Science\Artifical Intelligence Programming\BotMaker_Pizza\Bot\imgs\hawaiian.jpeg")},
            "BBQ Chicken": {"price": 14.99, "image": Path(r"C:\Users\Tevin\Documents\Computer Science\Artifical Intelligence Programming\BotMaker_Pizza\Bot\imgs\bbchicken.jpg")},
            "Custom": {"price": 14.99, "image": "custom_image_url"},
        }
        self.toppings = {
            "Mushrooms": {"price": 1.50, "image": "mushrooms_image_url"},
            "Olives": {"price": 1.00, "image": "olives_image_url"},
            "Onions": {"price": 1.00, "image": "onions_image_url"},
            "Peppers": {"price": 1.50, "image": "peppers_image_url"},
            "Extra cheese": {"price": 2.00, "image": "extra_cheese_image_url"},
        }
        self.order = {
            "pizza": [],
            "toppings": [],
        }
        self.user_name = None
        self.wait_time = random.randint(20, 50)
        self.counter_number = random.randint(1, 10)
        self.placing_order = False # flag to track the order placement status

    async def on_turn(self, turn_context: TurnContext):
        if turn_context.activity.type == ActivityTypes.conversation_update:
            await self.send_welcome_card(turn_context)
        elif turn_context.activity.type == ActivityTypes.message:
            user_message = turn_context.activity.text
            if self.placing_order:
                # User is in the process of placing an order
                await self.handle_order(turn_context, user_message)
            elif self.user_name is None:
                # Set user name and show the initial prompt
                self.user_name = user_message
                await self.send_initial_prompt_card(turn_context)
            else:
                # Handle non-order-related messages
                await self.handle_non_order(turn_context, user_message)

    async def handle_order(self, turn_context, user_message):
        if user_message == "ViewMenu":
            await self.view_menu(turn_context)
        elif user_message in self.menu:
            if user_message == 'Custom':
                await self.customize_pizza(turn_context, pizza_details={})
            else:
                self.order["pizza"].append(user_message)
                await turn_context.send_activity(f"{user_message} added to your order")
        elif user_message.lower() == "place order":
            # Proceed with the existing order placement logic
            await self.place_order(turn_context)
        else:
            await turn_context.send_activity("Sorry, I didn't understand that. You can continue customizing your order or place the order.")

    async def handle_non_order(self, turn_context, user_message):
        if user_message == "StartOrder":
            # Start placing an order
            self.placing_order = True
            await self.place_order(turn_context)
        elif user_message == "ViewMenu":
            await self.view_menu(turn_context)
        elif user_message in self.menu:
            if user_message == 'Custom':
                await self.customize_pizza(turn_context, pizza_details={})
            else:
                self.order["pizza"].append(user_message)
                await turn_context.send_activity(f"{user_message} added to your order")
        else:
            await turn_context.send_activity("Sorry, we don't have that on the menu. Please choose again.")


    async def send_welcome_card(self, turn_context):
        welcome_card = CardFactory.hero_card(
            HeroCard(
                title="Welcome to Pizza Pizzeria!",
                text="I will be your virtual assistant for all orders and related inquiries. May I know your name?",
                images=[CardImage(url="bot_logo_image_url")]
            )
        )
        await turn_context.send_activity(MessageFactory.attachment(welcome_card))

    async def send_initial_prompt_card(self, turn_context):
        initial_prompt_card = CardFactory.hero_card(
            HeroCard(
                title=f"Welcome, {self.user_name}!",
                text="Thank you for visiting Pizza Pizzeria!",
                images=[CardImage(url="bot_logo_image_url")],
                buttons=[
                    CardAction(type=ActionTypes.im_back, title="Place an Order", value="StartOrder"),
                    CardAction(type=ActionTypes.im_back, title="View the Menu", value="ViewMenu")
                ]
            )
        )
        await turn_context.send_activity(MessageFactory.attachment(initial_prompt_card))

    async def send_menu_options(self, turn_context):
        menu_options_card = CardFactory.hero_card(
            HeroCard(
                title="Menu Options",
                text="What would you like to do?",
                buttons=[
                    CardAction(type=ActionTypes.im_back, title="Place an Order", value="StartOrder"),
                    CardAction(type=ActionTypes.im_back, title="View the Menu", value="ViewMenu")
                ],
                images=[CardImage(url="bot_logo_image_url")]
            )
        )
        await turn_context.send_activity(MessageFactory.attachment(menu_options_card))

    async def view_menu(self, turn_context):
        await self.display_menu(turn_context, "Available Pizzas", self.menu, show_buttons=False)
        await self.display_menu(turn_context, "Available Toppings", self.toppings, show_buttons=False)
        await self.misc_place_order_btn(turn_context)
        
    async def misc_place_order_btn(self, turn_context):
        place_order_button = CardAction(
            type=ActionTypes.im_back,
            title="Place Order",
            value="StartOrder"
            )
        place_order_card = CardFactory.hero_card(
            HeroCard(
                buttons=[place_order_button],
                images=[CardImage(url="bot_logo_image_url")]
                )
            )
        await turn_context.send_activity(MessageFactory.attachment(place_order_card))

    async def display_menu(self, turn_context, menu_title, menu_items, show_buttons: bool):
        cards = []
        for item, details in menu_items.items():
            hero_card = HeroCard(
                title=item,
                subtitle=f"Price: ${details['price']}",
                images=[CardImage(url=details['image'])],
            )

            if show_buttons:
                card_action = CardAction(
                    type=ActionTypes.im_back,
                    title=f"Add {item} to your order",
                    value=item
                )
                hero_card.buttons = [card_action]

            cards.append(CardFactory.hero_card(hero_card))

        carousel = MessageFactory.carousel(cards)
        await turn_context.send_activity(f"{menu_title}:")
        await turn_context.send_activity(carousel)
        
    async def customize_pizza(self, turn_context, pizza_details):
        await turn_context.send_activity(f"Customize your {pizza_details['size']} {pizza_details['name']} with additional toppings:")
        await self.display_menu(turn_context, "Toppings Menu", self.toppings, show_buttons=True)

        for topping, details in self.toppings.items():
            await turn_context.send_activity(f"Do you want {topping} at ${details['price']}? (Type 'yes' or 'no')")
            response = (await turn_context.receive_activity()).text
            if response.lower() == 'yes':
                pizza_details["toppings"].append(topping)
                await turn_context.send_activity(f"{topping} added to your {pizza_details['size']} {pizza_details['name']}.")

        await turn_context.send_activity(f"Custom {pizza_details['size']} {pizza_details['name']} added to your order.")


    async def place_order(self, turn_context):
            await turn_context.send_activity("You can place your order by selecting items from the menu.")
            await self.select_pizza(turn_context)

            await self.calculate_total(turn_context)
            countdown_task = asyncio.create_task(self.countdown(turn_context, self.wait_time))

            # Provide counter number for pickup
            counter_number = random.randint(1, 10)  # Random counter number between 1 and 10

            # Wait for the countdown to finish
            await countdown_task

            # Notify the user when the order is ready
            await self.notify_order_ready(turn_context, counter_number)

            # Reset placing_order flag after completing the order
            self.placing_order = False

            await turn_context.send_activity("Thank you for ordering from Pizza Paradise!")

    async def select_pizza(self, turn_context):
        await self.display_menu(turn_context, "Pizza Menu", self.menu, show_buttons=True)
        user_choice = (await turn_context.receive_activity()).text
        if user_choice in self.menu:
            await self.select_pizza_size(turn_context, user_choice)
        else:
            await turn_context.send_activity("Invalid pizza selection.")

    async def select_pizza_size(self, turn_context, pizza_name):
        size_buttons = [
            CardAction(type=ActionTypes.im_back, title="Small", value="Small"),
            CardAction(type=ActionTypes.im_back, title="Medium", value="Medium"),
            CardAction(type=ActionTypes.im_back, title="Large", value="Large")
        ]

        size_selection_card = CardFactory.hero_card(
            HeroCard(
                title=f"Select size for {pizza_name}",
                buttons=size_buttons,
                images=[CardImage(url=self.menu[pizza_name]['image'])]
            )
        )

        await turn_context.send_activity(MessageFactory.attachment(size_selection_card))

        response = (await turn_context.receive_activity()).text.lower()
        if response in ["small", "medium", "large"]:
            pizza_details = {"name": pizza_name, "size": response, "toppings": []}
            self.order["pizza"].append(pizza_details)
            await self.customize_pizza(turn_context, pizza_details)
        else:
            await turn_context.send_activity("Invalid size selection.")

    async def calculate_total(self, turn_context):
        pizza_cost = sum(self.menu[item]["price"] for item in self.order["pizza"])
        toppings_cost = sum(self.toppings[topping]["price"] for topping in self.order["toppings"])
        total_cost = pizza_cost + toppings_cost

        total_cost_card = CardFactory.hero_card(
            HeroCard(
                title="Total Order Cost",
                text=f"Your total order cost is: ${total_cost}",
                images=[CardImage(url="bot_logo_image_url")]
            )
        )
        await turn_context.send_activity(MessageFactory.attachment(total_cost_card))

    async def countdown(self, turn_context, wait_time):
        while wait_time > 0:
            await turn_context.send_activity(f"Waiting time remaining: {wait_time} seconds.")
            await asyncio.sleep(1)  # Introduce a 1-second delay without blocking the event loop
            wait_time -= 1
            
    async def notify_order_ready(self, turn_context, counter_number):
        order_ready_card = CardFactory.hero_card(
            HeroCard(
                title="Order Ready!",
                text=f"Your order is ready for pickup at Counter No. {counter_number}. Enjoy your pizza!",
                images=[CardImage(url="bot_logo_image_url")]
            )
        )
        await turn_context.send_activity(MessageFactory.attachment(order_ready_card))

