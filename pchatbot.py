import asyncio
import random
from pathlib import Path
from botbuilder.core import TurnContext, MessageFactory, CardFactory
from botbuilder.schema import ActivityTypes, ActionTypes, Attachment, CardAction, CardImage, Fact, HeroCard,  ReceiptCard, ReceiptItem



class PizzaChatBot:
    def __init__(self):
        self.existing_customers = {}
        self.returning_customers = {}
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
            "pizza": "",
            "toppings": [],
        }
        self.user_name = None
        self.wait_time = random.randint(20, 50)
        self.counter_number = random.randint(1, 10)
        self.placing_order = False  # flag to track the order placement status

    async def on_turn(self, turn_context: TurnContext):
        if turn_context.activity.type == ActivityTypes.conversation_update:
            if not turn_context.activity.members_added:
                # Existing conversation
                pass

            # New conversation
            turn_context.send_activity(f"\n{self.user_name}, {self.placing_order}, {self.order}\n")
            self.user_name = None
            self.order = {"pizza": [], "toppings": []}
            self.placing_order = False

            await self.send_welcome_card(turn_context)
        elif turn_context.activity.type == ActivityTypes.message:
            user_message = turn_context.activity.text
            if self.placing_order or user_message == "StartOrder":
                # User is in the process of placing an order
                self.placing_order = True
                await self.handle_order(turn_context, user_message)
            elif self.user_name is None:
                # Set user name and show the initial prompt
                self.user_name = user_message
                await self.send_initial_prompt_card(turn_context)
            else:
                # Handle non-order-related messages
                await self.handle_non_order(turn_context, user_message)

    async def handle_order(self, turn_context: TurnContext, user_message):
        if user_message == "StartOrder":
            await self.display_menu(turn_context, "Pizza Menu", self.menu, True)
        elif user_message == "ViewMenu":
            await self.view_menu(turn_context)
        elif user_message in self.menu:
            await self.add_pizza_to_order(turn_context, user_message)
        elif user_message in ["Small", "Medium", "Large"]:
            await self.confirm_size(turn_context, user_message)
        elif user_message in self.toppings:
            if len(self.order["toppings"]) < 4:
                await self.customize_pizza(turn_context, self.order["pizza"][0], user_message=user_message)
        elif user_message == "CompleteOrder":
            await self.complete_order(turn_context)
        else:
            await turn_context.send_activity(
                f"{self.order} Sorry, I didn't understand that. You can continue customizing your order or place the order."
            )

    async def handle_non_order(self, turn_context, user_message):
        if user_message == "StartOrder":
            # Begin order placement logic
            await self.display_menu(turn_context, "Pizza Menu", self.menu, False)
        elif user_message == "ViewMenu":
            self.placing_order = True
            await self.view_menu(turn_context)
        else:
            await turn_context.send_activity(
                "Sorry, that selection is invalid. Please try again."
            )

    async def send_welcome_card(self, turn_context):
        welcome_card = CardFactory.hero_card(
            HeroCard(
                title="Welcome to Pizza Pizzeria!",
                text="I will be your virtual assistant for all orders and related inquiries. May I know your name?",
                images=[CardImage(url="bot_logo_image_url")],
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
                    CardAction(
                        type=ActionTypes.im_back, title="Place an Order", value="StartOrder"
                    ),
                    CardAction(
                        type=ActionTypes.im_back, title="View the Menu", value="ViewMenu"
                    ),
                ],
            )
        )
        await turn_context.send_activity(MessageFactory.attachment(initial_prompt_card))

    async def send_menu_options(self, turn_context):
        menu_options_card = CardFactory.hero_card(
            HeroCard(
                title="Menu Options",
                text="What would you like to do?",
                buttons=[
                    CardAction(
                        type=ActionTypes.im_back, title="Place an Order", value="StartOrder"
                    ),
                    CardAction(
                        type=ActionTypes.im_back, title="View the Menu", value="ViewMenu"
                    ),
                ],
                images=[CardImage(url="bot_logo_image_url")],
            )
        )
        await turn_context.send_activity(MessageFactory.attachment(menu_options_card))

    async def view_menu(self, turn_context):
        await self.display_menu(turn_context, "Available Pizzas", self.menu, show_buttons=False)
        await self.display_menu(turn_context, "Available Toppings", self.toppings, show_buttons=False)
        await self.misc_place_order_btn(turn_context)

    async def misc_place_order_btn(self, turn_context):
        place_order_button = CardAction(
            type=ActionTypes.im_back, title="Place Order", value="StartOrder"
        )
        place_order_card = CardFactory.hero_card(
            HeroCard(buttons=[place_order_button], images=[CardImage(url="bot_logo_image_url")])
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
                    value=item,
                )
                hero_card.buttons = [card_action]

            cards.append(CardFactory.hero_card(hero_card))

        carousel = MessageFactory.carousel(cards)
        await turn_context.send_activity(f"{menu_title}:")
        await turn_context.send_activity(carousel)

    async def add_pizza_to_order(self, turn_context, pizza_name):
        self.order["pizza"] = pizza_name
        await self.select_pizza_size(turn_context, pizza_name)

    async def select_pizza_size(self, turn_context, pizza_name):
        size_buttons = [
            CardAction(type=ActionTypes.im_back, title="Small", value="Small"),
            CardAction(type=ActionTypes.im_back, title="Medium", value="Medium"),
            CardAction(type=ActionTypes.im_back, title="Large", value="Large"),
        ]

        size_selection_card = CardFactory.hero_card(
            HeroCard(
                title=f"Select size for {pizza_name}",
                buttons=size_buttons,
                images=[CardImage(url=self.menu[pizza_name]['image'])],
            )
        )

        await turn_context.send_activity(MessageFactory.attachment(size_selection_card))
        
    async def confirm_size(self, turn_context:TurnContext, user_message:str) -> None:
        pizza_name = self.order["pizza"]
        if (user_message) in ["Small", "Medium", "Large"]:
            pizza_details = {"pizza": pizza_name, "size": user_message, "toppings": []}
            self.order.update(pizza_details)
            await self.customize_pizza(turn_context, pizza_details)
        else:
            await turn_context.send_activity("Invalid size selection.")
            await self.select_pizza_size(turn_context, pizza_name)  # Retry size selection

    async def customize_pizza(self, turn_context: TurnContext, pizza_details, user_message = None):
        if user_message:
            # Wait for user to select toppings
            selected_toppings = []
            selected_toppings.extend(self.order["toppings"])
            choose_toppings = True if len(selected_toppings) < 3 else False
            if choose_toppings:
                response = user_message
                if response in self.toppings:
                    selected_toppings.append(response)
                    await turn_context.send_activity(
                        MessageFactory.attachment(
                            CardFactory.hero_card(
                                HeroCard(
                                    title=f"{response} added to your {pizza_details['size']} {pizza_details['name']}."
                                )
                            )
                        )
                    )
                else:
                    await turn_context.send_activity(
                        MessageFactory.attachment(
                            CardFactory.hero_card(
                                HeroCard(
                                    title="Sorry, I didn't understand that. Please select a topping from the menu."
                                )
                            )
                        )
                    )
        else:
            await self.display_menu(turn_context, "Toppings Menu", self.toppings, show_buttons=True)
             # Send the "Complete your order" button as a separate activity
            complete_order_card = HeroCard(
                title="Complete your order",
                buttons=[
                    CardAction(
                        type=ActionTypes.im_back,
                        title="Complete your order",
                        value="CompleteOrder"
                    )
                ]
            )
            await turn_context.send_activity(MessageFactory.attachment(CardFactory.hero_card(complete_order_card)))
            
        self.order["toppings"] = selected_toppings

        await self.display_menu(turn_context, "Toppings Menu", self.toppings, show_buttons=True)

    async def complete_order(self, turn_context):
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

    async def calculate_total(self, turn_context: TurnContext):
        await turn_context.send_activity(f"Your order items=>{self.order}", "Here is your order")
        total_cost = 0
        receipt_items = []
        pizza_cost = self.menu[self.order["pizza"]]["price"]
        pizza_cost = pizza_cost * .75 if self.order["size"] == "Small" else pizza_cost * 1.25 if self.order["Large"] else pizza_cost  
        toppings_cost = sum(self.toppings[topping]["price"] for topping in self.order["toppings"])
        total_cost += pizza_cost + toppings_cost

        # Add a receipt item for each pizza
        receipt_items.append(
            ReceiptItem(
                title=f"{self.order['size']} {self.order['pizza']}",
                price=f"${pizza_cost + toppings_cost}",
                quantity="1",
                image=CardImage(url=f"{(self.menu.get(self.order.get('pizza'))).get('image')}")  
            )
        )

        receipt_card = ReceiptCard(
            title="Total Order Cost",
            facts=[Fact(key="Order Number", value="1234567890")],  # replace with actual order number
            items=receipt_items,
            total=f"${total_cost}",
            buttons=[
                CardAction(
                    type=ActionTypes.im_back,
                    title="Confirm Order",
                    value="Confirm Order"
                )
            ]
        )
        receipt_attachment = Attachment(content_type="application/vnd.microsoft.card.receipt", content=receipt_card)
        await turn_context.send_activity(MessageFactory.attachment(receipt_attachment))

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
